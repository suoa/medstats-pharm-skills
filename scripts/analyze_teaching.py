#!/usr/bin/env python3
"""读取教学CSV并保存真实分析产物；不生成、修改或覆盖输入数据。"""

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def select_t_method(levene_p, policy="course", alpha=0.05):
    """课程固定 P≤alpha 读Welch；通用Welch策略不依前提检验切换。"""
    if policy not in ("course", "welch"):
        raise ValueError("t policy 必须为 course 或 welch")
    if policy == "welch":
        return "welch"
    if not np.isfinite(levene_p) or not 0 <= levene_p <= 1:
        raise ValueError("Levene P 必须是未舍入的有效概率")
    return "welch" if levene_p <= alpha else "pooled"


def _numeric(series):
    values = pd.to_numeric(series, errors="raise").astype(float)
    if np.isinf(values.to_numpy()).any():
        raise ValueError("不接受无穷值；请先核对数据")
    return values


def _shapiro(values):
    if len(values) < 3 or np.ptp(values) == 0:
        return {"statistic": None, "pvalue": None, "status": "not_assessed"}
    result = stats.shapiro(values)
    return {"statistic": float(result.statistic), "pvalue": float(result.pvalue),
            "interpretation": "非拒绝不证明正态，须结合设计、图形、异常值与样本量"}


def align_pairs(left, right, key="subject_id", value_left="value", value_right="value"):
    """先验唯一键、再按键外连接，最后删除不完整整对；不按行位置拼接。"""
    for name, frame in (("left", left), ("right", right)):
        if frame[key].isna().any() or frame[key].duplicated().any():
            raise ValueError(f"{name} 配对键缺失或重复；不可形成多对多连接")
    a = left[[key, value_left]].rename(columns={value_left: "left_value"}).copy()
    b = right[[key, value_right]].rename(columns={value_right: "right_value"}).copy()
    a["left_value"], b["right_value"] = _numeric(a.left_value), _numeric(b.right_value)
    merged = a.merge(b, on=key, how="outer", validate="one_to_one", indicator=True)
    complete = merged.left_value.notna() & merged.right_value.notna()
    excluded = []
    for _, row in merged.loc[~complete].iterrows():
        reasons = [side for side in ("left", "right") if pd.isna(row[f"{side}_value"])]
        excluded.append({"key": str(row[key]), "reason": "missing_" + "_and_".join(reasons)})
    analysis_set = {"left_rows": len(left), "right_rows": len(right),
                    "candidate_pairs": len(merged), "complete_pairs": int(complete.sum()),
                    "excluded_pairs": int((~complete).sum()), "exclusions": excluded}
    return merged.loc[complete, [key, "left_value", "right_value"]].reset_index(drop=True), analysis_set


def analyze_log_pairs(left, right, key="subject_id", value_left="cmax_T", value_right="cmax_R",
                      bounds=(80.0, 125.0)):
    """T/R对数配对等效界值演示；始终不作正式生物等效性评估。"""
    if not np.isfinite(bounds).all() or not 0 < bounds[0] < bounds[1]:
        raise ValueError("教学界值须为有限正数且下界小于上界")
    pairs, included = align_pairs(left, right, key, value_left, value_right)
    if len(pairs) < 2 or (pairs[["left_value", "right_value"]] <= 0).any().any():
        raise ValueError("对数配对分析须至少两完整对，且两条件数值均为正")
    log_left = np.log(pairs.left_value.to_numpy())
    log_right = np.log(pairs.right_value.to_numpy())
    d = log_left - log_right
    n, mean, sd = len(d), float(d.mean()), float(d.std(ddof=1))
    # Constant ratios can acquire tiny variation when subtracting rounded logs.
    # Scale the guard to floating-point precision, not a fixed statistical SD.
    log_scale = max(float(np.max(np.abs(log_left))), float(np.max(np.abs(log_right))))
    rounding_tolerance = 8 * np.finfo(float).eps * log_scale
    if sd <= rounding_tolerance:
        raise ValueError("对数差值方差为0或在浮点精度下不可分辨，当前教学t流程不计算检验")
    se = sd / np.sqrt(n)
    test = stats.ttest_1samp(d, 0.0)
    ci90 = np.exp(mean + np.array([-1, 1]) * stats.t.ppf(0.95, n - 1) * se) * 100
    ci95 = mean + np.array([-1, 1]) * stats.t.ppf(0.975, n - 1) * se
    interval_met = bool(ci90[0] >= bounds[0] and ci90[1] <= bounds[1])
    return {"design": "simplified_paired_log_demo", "direction": "ln(T) - ln(R); GMR=T/R",
            "analysis_set": included, "included_ids": pairs[key].astype(str).tolist(),
            "mean_log_difference": mean, "sd_log_difference": sd, "se_log_difference": float(se),
            "shapiro": _shapiro(d),
            "paired_t": {"method": "paired_t_on_log_values", "statistic": float(test.statistic),
                         "df": n - 1, "pvalue": float(test.pvalue), "alternative": "two-sided",
                         "ci95_mean_log_difference": ci95.tolist()},
            "cohens_dz": mean / sd, "gmr_pct": float(np.exp(mean) * 100),
            "ci90_pct": ci90.tolist(), "ci_method": "paired_log_t_interval_backtransformed",
            "teaching_bounds_pct": list(bounds), "interval_criterion_met": interval_met,
            "interval_statement": "满足本教学模型的区间条件" if interval_met else "未满足本教学模型的区间条件，未能证明等效",
            "formal_be_assessment": "not_assessed",
            "limitation": "无序列、周期和完整PK参数，不能作正式BE判定；P>0.05不证明等效"}


def analyze_independent_t(frame, group="process", value="assay_pct",
                          labels=("A_对照工艺", "B_新工艺"), policy="course"):
    unknown = set(frame[group].dropna().unique()) - set(labels)
    if unknown:
        raise ValueError(f"未知分组编码：{unknown}")
    values = _numeric(frame[value])
    usable = frame[group].notna() & values.notna()
    groups, arrays = {}, []
    for code, label in zip(("A", "B"), labels):
        sample = values[usable & (frame[group] == label)].to_numpy()
        if len(sample) < 2 or sample.var(ddof=1) == 0:
            raise ValueError("每组至少两例且方差须大于0；退化资料另行讨论")
        arrays.append(sample)
        groups[code] = {"label": label, "n": len(sample), "mean": float(sample.mean()),
                        "sd": float(sample.std(ddof=1)), "shapiro": _shapiro(sample)}
    a, b = arrays
    na, nb, va, vb = len(a), len(b), a.var(ddof=1), b.var(ddof=1)
    mean_diff = float(b.mean() - a.mean())
    pooled_var = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        levene = stats.levene(a, b, center="mean")
    tests = {}
    for method in ("pooled", "welch"):
        equal = method == "pooled"
        result = stats.ttest_ind(b, a, equal_var=equal)
        se = np.sqrt(pooled_var * (1 / na + 1 / nb)) if equal else np.sqrt(va / na + vb / nb)
        df = na + nb - 2 if equal else (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
        ci = mean_diff + np.array([-1, 1]) * stats.t.ppf(0.975, df) * se
        tests[method] = {"method": method + "_independent_t", "statistic": float(result.statistic),
                         "df": float(df), "pvalue": float(result.pvalue), "alternative": "two-sided",
                         "mean_diff": mean_diff, "ci95": ci.tolist(), "ci_method": method + "_t_interval"}
    return {"direction": "B - A", "unit": "percentage_points", "policy": policy,
            "analysis_set": {"input_rows": len(frame), "included_rows": int(usable.sum()),
                             "excluded_rows": int((~usable).sum()), "exclusion_reason": "missing_group_or_value"},
            "groups": groups, "levene": {"center": "mean", "statistic": float(levene.statistic) if np.isfinite(levene.statistic) else None,
                                         "pvalue": float(levene.pvalue) if np.isfinite(levene.pvalue) else None,
                                         "status": "assessed" if np.isfinite(levene.pvalue) else "not_assessed"},
            "primary_method": select_t_method(float(levene.pvalue), policy), "tests": tests,
            "cohens_d": float(mean_diff / np.sqrt(pooled_var)), "cohens_d_denominator": "pooled_SD",
            "professional_significance": "not_assessed", "pharmacopoeial_compliance": "not_assessed",
            "limitation": "每片独立为教学假设；无批次设计或品种标准，不推广真实工艺或判药典合格"}


def _table2x2(table):
    values = np.asarray(table, dtype=float)
    if values.shape != (2, 2) or not np.isfinite(values).all() or (values < 0).any() or (values != np.floor(values)).any():
        raise ValueError("要求2×2非负整数频数表，不能输入比例、NaN或无穷值")
    return values.astype(np.int64)


def event_table(frame, group="drug", outcome="adverse_event", labels=("A药", "B药")):
    """显式校验未知编码，不能让reindex静默丢记录；缺失按完整病例排除。"""
    unknown_groups = set(frame[group].dropna().unique()) - set(labels)
    unknown_events = set(frame[outcome].dropna().unique()) - {0, 1}
    if unknown_groups or unknown_events:
        raise ValueError(f"未知分组/结局编码：{unknown_groups} / {unknown_events}")
    complete = frame[group].notna() & frame[outcome].notna()
    table = pd.crosstab(frame.loc[complete, group], frame.loc[complete, outcome]).reindex(index=labels, columns=[1, 0], fill_value=0)
    return table, {"input_rows": len(frame), "included_rows": int(complete.sum()),
                   "excluded_rows": int((~complete).sum()), "exclusion_reason": "missing_group_or_event"}


def analyze_contingency(table, row_labels=("A药", "B药"), column_labels=("发生", "未发生")):
    """独立2×2课程链；空边际仅描述，零格不偷加0.5算Wald OR区间。"""
    if len(row_labels) != 2 or len(set(row_labels)) != 2 or len(column_labels) != 2 or len(set(column_labels)) != 2:
        raise ValueError("2×2表须有各两个不同的行、列标签")
    x = _table2x2(table)
    row_n, column_n, total = x.sum(axis=1), x.sum(axis=0), int(x.sum())
    rates = {str(label): (float(x[i, 0] / row_n[i]) if row_n[i] else None) for i, label in enumerate(row_labels)}
    result = {"table": x.tolist(), "row_labels": list(row_labels), "column_labels": list(column_labels),
              "direction": f"{row_labels[0]} relative to {row_labels[1]}; event={column_labels[0]}",
              "policy": "course_2x2_n40_expected5_1", "n": total, "row_n": row_n.tolist(), "rates": rates,
              "primary_method": None, "tests": {}, "effects": {}}
    if (row_n == 0).any() or (column_n == 0).any():
        result.update(status="descriptive_only", expected=None, reason="zero_row_or_column_margin; no_Pearson_Yates_or_Wald_OR")
        return result
    expected = np.outer(row_n, column_n) / total
    minimum = float(expected.min())
    primary = "fisher" if total < 40 or minimum < 1 else ("yates" if minimum < 5 else "pearson")
    for name, correction in (("pearson", False), ("yates", True)):
        test = stats.chi2_contingency(x, correction=correction)
        result["tests"][name] = {"method": name + "_chi_square", "statistic": float(test.statistic),
                                 "df": int(test.dof), "pvalue": float(test.pvalue)}
    fisher = stats.fisher_exact(x, alternative="two-sided")
    result["tests"]["fisher"] = {"method": "fisher_exact_two_sided", "pvalue": float(fisher.pvalue),
                                  "two_sided_definition": "sum probabilities of fixed-margin tables no more likely than observed"}
    a, b, c, d = x.ravel().astype(float)
    numerator, denominator = a * d, b * c
    odds = float(numerator / denominator) if denominator else None
    odds_ci = (np.exp(np.log(odds) + np.array([-1, 1]) * 1.96 * np.sqrt((1 / x.astype(float)).sum())).tolist()
               if (x > 0).all() else None)
    rd = float(a / row_n[0] - c / row_n[1])
    se_rd = np.sqrt((a / row_n[0]) * (1 - a / row_n[0]) / row_n[0] + (c / row_n[1]) * (1 - c / row_n[1]) / row_n[1])
    rd_ci = (rd + np.array([-1, 1]) * 1.96 * se_rd).tolist() if (x > 0).all() and minimum >= 5 else None
    result["effects"] = {
        "odds_ratio_sample": {"estimate": odds, "estimate_status": "finite" if odds is not None else "infinite",
                              "ci95": odds_ci, "ci_method": "log_Wald_z_1.96" if odds_ci else "not_estimated_zero_cell",
                              "continuity_addition": None},
        "risk_difference": {"estimate": rd, "ci95": rd_ci,
                            "unit": "proportion", "ci_method": "unpooled_Wald_z_1.96" if rd_ci else "not_estimated_sparse_or_boundary",
                            "limitation": "本最小实现对零格或Tmin<5不估计RD区间，未实现适当稀疏区间算法"}}
    result.update(status="analyzed", expected=expected.tolist(), minimum_expected=minimum, primary_method=primary)
    return result


def analyze_mcnemar(table):
    x = _table2x2(table)
    a, b, c, d = (int(value) for value in x.ravel())
    total, discordant = int(x.sum()), b + c
    result = {"table": x.tolist(), "row_labels": ["A阳性", "A阴性"], "column_labels": ["B阳性", "B阴性"],
              "b": b, "c": c, "discordant_pairs": discordant, "n_pairs": total,
              "marginal_rates": {"A": (a + b) / total if total else None, "B": (a + c) / total if total else None},
              "primary_method": None, "tests": {}, "direction": "A positive rate - B positive rate"}
    if discordant == 0:
        result.update(status="descriptive_only", reason="no_discordant_pairs; no_test_run; does_not_prove_equal")
        return result
    result["tests"]["exact_binomial"] = {"method": "mcnemar_exact_binomial_two_sided",
                                           "pvalue": float(stats.binomtest(min(b, c), discordant, 0.5, alternative="two-sided").pvalue)}
    for name, correction in (("chi_square_corrected", 1), ("chi_square_uncorrected", 0)):
        statistic = max(0, abs(b - c) - correction) ** 2 / discordant
        result["tests"][name] = {"method": "mcnemar_" + name, "statistic": statistic,
                                 "df": 1, "pvalue": float(stats.chi2.sf(statistic, 1))}
        if correction:
            result["tests"][name]["continuity_adjustment"] = "max(0, abs(b-c)-1)"
    result.update(status="analyzed", primary_method="exact_binomial" if discordant < 40 else "chi_square_uncorrected")
    return result


def analyze_mcnemar_pairs(left, right, key="subject_id", value_left="positive", value_right="positive"):
    for frame, value in ((left, value_left), (right, value_right)):
        if not frame[value].dropna().isin([0, 1]).all():
            raise ValueError("配对二分类结局必须为0/1")
    pairs, included = align_pairs(left, right, key, value_left, value_right)
    if not pairs[["left_value", "right_value"]].isin([0, 1]).all().all():
        raise ValueError("配对二分类结局必须为0/1")
    table = pd.crosstab(pairs.left_value, pairs.right_value).reindex(index=[1, 0], columns=[1, 0], fill_value=0)
    result = analyze_mcnemar(table)
    result["analysis_set"] = included
    return result


def run_analysis(data_dir=ROOT / "datasets/teaching", t_policy="course"):
    data_dir = Path(data_dir)
    paths = {name: data_dir / (name + ".csv") for name in ("tablet_assay", "bioeq_cmax", "adverse_events")}
    frames = {name: pd.read_csv(path) for name, path in paths.items()}
    for name, key in (("tablet_assay", "tablet_id"), ("adverse_events", "subject_id")):
        if frames[name][key].isna().any() or frames[name][key].duplicated().any():
            raise ValueError(f"{name}: 个体标识缺失或重复，请核查分析单位")
    be = frames["bioeq_cmax"]
    event, event_set = event_table(frames["adverse_events"])
    adverse = analyze_contingency(event)
    adverse["analysis_set"] = event_set
    result = {
        "metadata": {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                     "command": "python scripts/analyze_teaching.py --output-dir OUTPUT --t-policy " + t_policy,
                     "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
                     "inputs": {name: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": len(frames[name])} for name, path in paths.items()},
                     "execution": {"python": "executed", "R": "not_executed", "SPSS": "not_executed"}},
        "tablet_assay": analyze_independent_t(frames["tablet_assay"], policy=t_policy),
        "paired_log_demo": analyze_log_pairs(be[["subject_id", "cmax_T"]], be[["subject_id", "cmax_R"]]),
        "adverse_events": adverse,
        "mcnemar_demo": analyze_mcnemar([[42, 18], [6, 54]])}
    result["mcnemar_demo"]["source"] = "literal aggregate table in scripts/analyze_teaching.py; matches skills/methods-core/chi-square/references/examples.md; not a subject CSV"
    return result


def summary_text(result):
    def fmt(value, digits=6):
        return "not_estimated" if value is None else f"{value:.{digits}f}"

    def interval(values):
        return "not_estimated" if values is None else f"({fmt(values[0])}, {fmt(values[1])})"

    t, be, ae, mc = (result[key] for key in ("tablet_assay", "paired_log_demo", "adverse_events", "mcnemar_demo"))
    lines = ["医学统计Skills 教学分析：由提交CSV实际计算", "Python=" + result["metadata"]["versions"]["python"] + "; SciPy=" + result["metadata"]["versions"]["scipy"],
             "仅Python已运行；R/SPSS未运行。结果字段见results.json；本文件为其格式化摘要。", "", "【tablet_assay】方向 B - A；单位：百分点；policy=" + t["policy"]]
    for name, group in t["groups"].items():
        lines.append(f"  {name}: n={group['n']}, mean={group['mean']:.3f}, SD={group['sd']:.3f}; Shapiro W={fmt(group['shapiro']['statistic'], 3)}, P={fmt(group['shapiro']['pvalue'], 3)}")
    lines.append(f"  Levene(center=mean): F={fmt(t['levene']['statistic'], 3)}, P={fmt(t['levene']['pvalue'])}; primary={t['primary_method']}")
    for method, test in t["tests"].items():
        lines.append(f"  {method}: t={test['statistic']:.3f}, df={test['df']:.6f}, P={test['pvalue']:.6f}; mean_diff={test['mean_diff']:.3f}, 95%CI=({test['ci95'][0]:.3f}, {test['ci95'][1]:.3f})")
    lines.extend([f"  Cohen d (pooled SD)={t['cohens_d']:.6f}; professional_significance=not_assessed; pharmacopoeial_compliance=not_assessed", "", "【paired_log_demo】ln(T)-ln(R)；仅配对等效界值演示",
                  f"  complete_pairs={be['analysis_set']['complete_pairs']}; excluded_pairs={be['analysis_set']['excluded_pairs']}; t={be['paired_t']['statistic']:.3f}, df={be['paired_t']['df']}, P={be['paired_t']['pvalue']:.6f}",
                  f"  GMR={be['gmr_pct']:.2f}%; 90%CI=({be['ci90_pct'][0]:.2f}%, {be['ci90_pct'][1]:.2f}%); interval_criterion_met={be['interval_criterion_met']}",
                  "  " + be["interval_statement"] + "; formal_be_assessment=" + be["formal_be_assessment"], "", "【adverse_events】行[A药,B药]，列[发生,未发生]；OR为A相对B发生事件",
                  f"  table={ae['table']}; n={ae['n']}; expected={ae['expected']}; primary={ae['primary_method']}"])
    for method, test in ae["tests"].items():
        stat = f"chi2={test['statistic']:.6f}, df={test['df']}, " if "statistic" in test else ""
        lines.append(f"  {method}: {stat}P={test['pvalue']:.10f}")
    for name, effect in ae["effects"].items():
        lines.append(f"  {name}={fmt(effect['estimate'])}, 95%CI={interval(effect['ci95'])}; {effect['ci_method']}")
    if ae["status"] == "descriptive_only":
        lines.append("  退化表仅描述，不运行检验或套用Wald OR区间；零样本组的率为null。")
    lines.extend(["", "【mcnemar_demo】课堂假设汇总表，不是独立两组", f"  table={mc['table']}; n_pairs={mc['n_pairs']}; b={mc['b']}, c={mc['c']}; b+c={mc['discordant_pairs']}; primary={mc['primary_method']}"])
    for method, test in mc["tests"].items():
        stat = f"chi2={test['statistic']:.6f}, df=1, " if "statistic" in test else ""
        lines.append(f"  {method}: {stat}P={test['pvalue']:.10f}")
    return "\n".join(lines) + "\n"


def _flatten(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _flatten(child, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _flatten(child, f"{prefix}[{index}]")
    else:
        yield {"field": prefix, "value": value}


def save_results(result, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    pd.DataFrame(_flatten(result)).to_csv(output_dir / "summary.csv", index=False, encoding="utf-8-sig")
    (output_dir / "summary.txt").write_text(summary_text(result), encoding="utf-8")
    ae = result["adverse_events"]
    pd.DataFrame(ae["table"], index=ae["row_labels"], columns=ae["column_labels"]).rename_axis("药品").to_csv(output_dir / "adverse_events_table.csv", encoding="utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "datasets/teaching")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/teaching")
    parser.add_argument("--t-policy", choices=("course", "welch"), default="course")
    args = parser.parse_args()
    result = run_analysis(args.data_dir, args.t_policy)
    result["metadata"]["command"] = f"python scripts/analyze_teaching.py --data-dir {args.data_dir} --output-dir {args.output_dir} --t-policy {args.t_policy}"
    save_results(result, args.output_dir)
    print(f"已保存实际分析结果：{args.output_dir}/results.json、summary.csv、summary.txt、adverse_events_table.csv；输入CSV未修改。")


if __name__ == "__main__":
    main()
