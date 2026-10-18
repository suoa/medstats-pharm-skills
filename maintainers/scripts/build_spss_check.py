#!/usr/bin/env python3
"""Build a portable SPSS check pack; never claim that SPSS has run."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

if __package__:
    from .analyze_teaching import ROOT, _flatten, run_analysis
else:
    from analyze_teaching import ROOT, _flatten, run_analysis


def reference_rows(result):
    """Select named values from the current computed result, not copied answers."""
    flat = {row["field"]: row["value"] for row in _flatten(result)}
    rows = []

    def unit(field):
        if field.endswith("pvalue"):
            return "probability"
        if field.endswith(".df"):
            return "degrees_of_freedom"
        if ".risk_difference." in field or ".rates." in field:
            return "proportion"
        if "gmr_pct" in field or "ci90_pct" in field:
            return "percent"
        if field.startswith("paired_log_demo.") and any(word in field for word in ("log_difference", "mean_log")):
            return "natural_log_ratio"
        if field.startswith("tablet_assay.groups.") and field.endswith(".mean"):
            return "percent_of_label_claim"
        if field.startswith("tablet_assay.") and any(word in field for word in (".mean", ".sd", "ci95")):
            return "percentage_points"
        if any(word in field for word in (".table[", ".expected[", "complete_pairs", "n_pairs", "discordant_pairs")) or field.endswith((".n", ".b", ".c")):
            return "count"
        return "dimensionless"

    def add(section, prefix, names, requirement, location):
        for name in names:
            field = prefix + name
            value = flat[field]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"Expected a computed numeric reference: {field}")
            rows.append({"section": section, "source_field": field,
                         "reference_value": value, "reference_unit": unit(field), "requirement": requirement,
                         "SPSS_location_hint": location})

    for group in ("A", "B"):
        add("01_tablet_assay", f"tablet_assay.groups.{group}.", ["n", "mean", "sd"],
            "required", "Group Statistics / Descriptives")
    add("01_tablet_assay", "tablet_assay.levene.", ["statistic", "pvalue"],
        "required", "ONEWAY homogeneity: Based on Mean")
    for method in ("pooled", "welch"):
        required = "required" if method == result["tablet_assay"]["primary_method"] else "comparison"
        add("01_tablet_assay", f"tablet_assay.tests.{method}.",
            ["statistic", "df", "pvalue", "mean_diff", "ci95[0]", "ci95[1]"], required,
            "Independent Samples Test: B minus A; use the named variance row")
    add("02_paired_log_demo", "paired_log_demo.analysis_set.", ["complete_pairs"],
        "required", "Paired Samples Statistics / valid N")
    add("02_paired_log_demo", "paired_log_demo.", ["mean_log_difference", "sd_log_difference"],
        "required", "Paired Differences / LIST d_mean and d_sd")
    add("02_paired_log_demo", "paired_log_demo.paired_t.",
        ["statistic", "df", "pvalue", "ci95_mean_log_difference[0]", "ci95_mean_log_difference[1]"],
        "required", "Paired Samples Test, CI95, ln(T) minus ln(R)")
    add("02_paired_log_demo", "paired_log_demo.", ["gmr_pct", "ci90_pct[0]", "ci90_pct[1]"],
        "required", "LIST GMR percent and CI90; not the CI95 row")
    add("03_adverse_events", "adverse_events.", ["n", "rates.A药", "rates.B药"],
        "required", "Crosstab total N and row percentages (convert percent to proportion)")
    for name in ("table", "expected"):
        add("03_adverse_events", f"adverse_events.{name}",
            [f"[{r}][{c}]" for r in range(2) for c in range(2)], "required",
            "Crosstab: rows A/B, columns event/non-event")
    for method in ("pearson", "yates"):
        add("03_adverse_events", f"adverse_events.tests.{method}.",
            ["statistic", "df", "pvalue"], "required" if method == "pearson" else "comparison",
            "Chi-Square Tests: named Pearson / Continuity Correction row")
    add("03_adverse_events", "adverse_events.tests.fisher.", ["pvalue"],
        "if_shown", "Fisher Exact Sig. (2-sided); record not_shown if absent")
    for effect in ("odds_ratio_sample", "risk_difference"):
        add("03_adverse_events", f"adverse_events.effects.{effect}.",
            ["estimate", "ci95[0]", "ci95[1]"], "required",
            "LIST derived effects, explicit z=1.96; not an unlabelled native Risk CI")
    add("04_mcnemar", "mcnemar_demo.", ["n_pairs", "b", "c", "discordant_pairs"],
        "required", "Weighted full table and discordant Binomial Test N/categories")
    add("04_mcnemar", "mcnemar_demo.tests.exact_binomial.", ["pvalue"],
        "required", "Binomial(.5): exact two-sided P, discordant cases only")
    for method in ("chi_square_corrected", "chi_square_uncorrected"):
        add("04_mcnemar", f"mcnemar_demo.tests.{method}.", ["statistic", "pvalue"],
            "reference_only", "Asymptotic reference only; do not fill an exact-test statistic")
    return rows


def build_pack(output_dir, zip_output=None):
    output_dir = Path(output_dir).resolve()
    zip_output = Path(zip_output).resolve() if zip_output else output_dir.with_name(output_dir.name + ".zip")
    if output_dir.exists() or zip_output.exists():
        raise FileExistsError("Choose new pack and ZIP paths; existing results are never overwritten")
    if zip_output.is_relative_to(output_dir):
        raise ValueError("ZIP must be outside the pack directory")
    inputs = sorted((ROOT / "datasets/teaching").glob("*.csv"))
    before = {path.name: path.read_bytes() for path in inputs}
    result = run_analysis()
    # These .sps templates are for the frozen complete, nonsparse teaching tasks.
    if ([g["n"] for g in result["tablet_assay"]["groups"].values()] != [20, 20]
            or result["paired_log_demo"]["analysis_set"]["complete_pairs"] != 24
            or result["adverse_events"]["n"] != 240
            or result["adverse_events"]["minimum_expected"] < 5
            or any(value <= 0 for row in result["adverse_events"]["table"] for value in row)):
        raise ValueError("This pack requires the supplied complete, nonsparse teaching fixtures")
    rows = reference_rows(result)
    mc_rows = "\n".join(f"{i + 1} {j + 1} {value}"
                        for i, row in enumerate(result["mcnemar_demo"]["table"])
                        for j, value in enumerate(row))
    rendered = {}
    templates = sorted((ROOT / "maintainers/spss_pack").glob("*.sps"))
    if len(templates) != 4:
        raise ValueError("Expected all four SPSS template files")
    for path in templates:
        text = path.read_text(encoding="utf-8")
        for marker, value in {"@REPO_ROOT@": ".", "@OUTPUT_DIR@": "output", "@MCNEMAR_ROWS@": mc_rows}.items():
            text = text.replace(marker, value)
        if "@" in text:
            raise ValueError(f"Unresolved SPSS placeholder: {path.name}")
        rendered[path.name] = text

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "output").mkdir()
    data_dir = output_dir / "datasets/teaching"
    data_dir.mkdir(parents=True)
    for path in inputs:
        shutil.copyfile(path, data_dir / path.name)
    for name, text in rendered.items():
        (output_dir / name).write_text(text, encoding="utf-8-sig")
    (output_dir / "00_setup.sps").write_text(
        "* Encoding: UTF-8.\n* Change only the path below to this extracted pack root.\n"
        "* Save existing work and start a new Unicode SPSS session first.\n"
        "* Use a fresh extracted pack for each run; output must be empty.\n"
        "CD '__EDIT_PACK_ROOT__'.\nSHOW VERSION.\n"
        "* Stop if CD reports an error; run task files section by section.\n", encoding="utf-8-sig")
    (output_dir / "reference_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (output_dir / "reference_values.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (output_dir / "SPSS_run_record.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        columns = ["section", "source_field", "observed_value", "observed_unit", "run_date", "output_file", "table_name",
                   "row_column", "SPSS_version", "check_state", "notes"]
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({"section": row["section"], "source_field": row["source_field"],
                          "check_state": "not_run"} for row in rows)
    shutil.copyfile(ROOT / "maintainers/qa/spss-machine-check.md", output_dir / "README.md")
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"SPSS_execution": "not_executed", "syntax_review": "official_docs_and_static_only",
                "numeric_reference": "computed_in_Python_from_supplied_CSV_not_SPSS_output",
                "reference_rows": len(rows), "python_versions": result["metadata"]["versions"],
                "inputs_sha256": {path.name: digest(path) for path in inputs},
                "template_sha256": {path.name: digest(path) for path in templates},
                "reference_results_sha256": digest(output_dir / "reference_results.json"),
                "output_rule": "SPV/PDF must be produced on the actual SPSS workstation"}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in inputs:
        if path.read_bytes() != before[path.name] or (data_dir / path.name).read_bytes() != before[path.name]:
            raise RuntimeError("Original or copied teaching CSV bytes changed")
    zip_output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(output_dir.name + "/output/", "")
        for path in sorted(output_dir.rglob("*")):
            if path.is_file():
                archive.write(path, output_dir.name + "/" + path.relative_to(output_dir).as_posix())
    return {"pack": str(output_dir), "zip": str(zip_output), "reference_rows": len(rows), "SPSS_execution": "not_executed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "maintainers/output/spss-check")
    parser.add_argument("--zip-output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_pack(args.output_dir, args.zip_output), ensure_ascii=False))


if __name__ == "__main__":
    main()
