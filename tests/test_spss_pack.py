"""Check packaging provenance and overwrite protection; this does not run SPSS."""

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_spss_check import build_pack


class SPSSPackTests(unittest.TestCase):
    def test_portable_pack_has_honest_status_blank_observations_and_exact_inputs(self):
        sources = list((ROOT / "datasets/teaching").glob("*.csv"))
        before = {path.name: path.read_bytes() for path in sources}
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "spss-check"
            completed = subprocess.run([sys.executable, str(ROOT / "scripts/build_spss_check.py"),
                                        "--output-dir", str(out)], check=True, text=True, capture_output=True)
            built = json.loads(completed.stdout)
            self.assertEqual(built["SPSS_execution"], "not_executed")
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["SPSS_execution"], "not_executed")
            result_bytes = (out / "reference_results.json").read_bytes()
            self.assertEqual(hashlib.sha256(result_bytes).hexdigest(), manifest["reference_results_sha256"])
            reference = json.loads(result_bytes)
            values = list(csv.DictReader(io.StringIO((out / "reference_values.csv").read_text(encoding="utf-8-sig"))))
            mapped = {row["source_field"]: row for row in values}
            self.assertEqual(float(mapped["adverse_events.effects.odds_ratio_sample.estimate"]["reference_value"]),
                             reference["adverse_events"]["effects"]["odds_ratio_sample"]["estimate"])
            self.assertEqual(mapped["adverse_events.effects.risk_difference.estimate"]["reference_unit"], "proportion")
            self.assertNotIn("adverse_events.tests.fisher.statistic", mapped)
            self.assertNotIn("mcnemar_demo.tests.exact_binomial.statistic", mapped)
            observed = list(csv.DictReader(io.StringIO((out / "SPSS_run_record.csv").read_text(encoding="utf-8-sig"))))
            self.assertEqual(len(observed), len(values))
            self.assertTrue(all(row["check_state"] == "not_run" and not row["observed_value"]
                                and not row["output_file"] for row in observed))
            self.assertEqual(list((out / "output").iterdir()), [])
            self.assertFalse(list(out.rglob("*.spv")) + list(out.rglob("*.pdf")))
            with zipfile.ZipFile(built["zip"]) as archive:
                for path in sources:
                    data = archive.read("spss-check/datasets/teaching/" + path.name)
                    self.assertEqual(data, before[path.name])
                    self.assertEqual((out / "datasets/teaching" / path.name).read_bytes(), data)
                    self.assertEqual(hashlib.sha256(data).hexdigest(), manifest["inputs_sha256"][path.name])
                self.assertIn("spss-check/output/", archive.namelist())
                self.assertEqual(len([name for name in archive.namelist() if name.endswith(".sps")]), 5)
        for path in sources:
            self.assertEqual(path.read_bytes(), before[path.name])

    def test_existing_pack_or_archive_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "existing"
            out.mkdir()
            evidence = out / "actual-SPSS-result.spv"
            evidence.write_bytes(b"existing workstation result")
            with self.assertRaises(FileExistsError):
                build_pack(out)
            self.assertEqual(evidence.read_bytes(), b"existing workstation result")
            archive = Path(temp) / "new.zip"
            archive.write_bytes(b"existing archive")
            with self.assertRaises(FileExistsError):
                build_pack(Path(temp) / "new", archive)
            self.assertEqual(archive.read_bytes(), b"existing archive")
            self.assertFalse((Path(temp) / "new").exists())


if __name__ == "__main__":
    unittest.main()
