"""针对已发现的数字、选法与留痕失败设回归测试；不依赖pytest。"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.analyze_teaching import (align_pairs, analyze_contingency, analyze_log_pairs, analyze_independent_t,
    analyze_mcnemar, analyze_mcnemar_pairs, diagnostic_sample, event_table, run_analysis, select_t_method)

spec = importlib.util.spec_from_file_location("teaching_generator", ROOT / "datasets/teaching/generate_datasets.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class TeachingAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = run_analysis()
        cls.paired = pd.read_csv(ROOT / "datasets/teaching/bioeq_cmax.csv")

    def test_frozen_tablet_values_and_matched_ci(self):
        case = self.results["tablet_assay"]
        self.assertEqual(case["primary_method"], "pooled")
        self.assertEqual(case["analysis_set"]["included_rows"], 40)
        self.assertEqual(case["groups"]["A"]["n"], 20)
        self.assertAlmostEqual(case["groups"]["A"]["mean"], 98.4975, places=10)
        self.assertAlmostEqual(case["groups"]["B"]["mean"], 99.2575, places=10)
        self.assertAlmostEqual(case["levene"]["pvalue"], 0.3954279324635631, places=9)
        self.assertAlmostEqual(case["tests"]["pooled"]["statistic"], 2.337732157502677, places=9)
        self.assertAlmostEqual(case["tests"]["pooled"]["pvalue"], 0.02476760449216479, places=9)
        np.testing.assert_allclose(case["tests"]["pooled"]["ci95"], [0.101866620760923, 1.418133379239087], atol=1e-9)
        self.assertAlmostEqual(case["tests"]["welch"]["df"], 37.359337923925146, places=8)
        self.assertAlmostEqual(case["tests"]["welch"]["pvalue"], 0.02486297726191456, places=9)
        np.testing.assert_allclose(case["tests"]["welch"]["ci95"], [0.10149578907237633, 1.418504210927634], atol=1e-9)
        self.assertAlmostEqual(case["cohens_d"], 0.7392558177127944, places=9)

    def test_unrounded_levene_branch_and_prespecified_welch(self):
        # 分支构造值，不是某个数据集真实P；两者显示到3位均为.050。
        self.assertEqual(f"{0.0496:.3f}", f"{0.0504:.3f}")
        self.assertEqual(select_t_method(0.0496), "welch")
        self.assertEqual(select_t_method(0.0504), "pooled")
        self.assertEqual(select_t_method(0.05), "welch")
        self.assertEqual(select_t_method(0.9, policy="welch"), "welch")
        self.assertEqual(select_t_method(float("nan"), policy="welch"), "welch")
        with self.assertRaises(ValueError):
            select_t_method(float("nan"))

    def test_prespecified_welch_survives_undefined_levene(self):
        frame = pd.DataFrame({"process": ["A_对照工艺"] * 2 + ["B_新工艺"] * 2,
                              "assay_pct": [0, 2, 0, 2]})
        result = analyze_independent_t(frame, policy="welch")
        self.assertEqual(result["primary_method"], "welch")
        self.assertIsNone(result["levene"]["pvalue"])
        self.assertEqual(result["tests"]["welch"]["pvalue"], 1.0)
        json.dumps(result, allow_nan=False)
        with self.assertRaises(ValueError):
            analyze_independent_t(frame, policy="course")

    def test_constant_decimal_groups_cannot_create_false_welch_precision(self):
        frame = pd.DataFrame({"process": ["A_对照工艺"] * 20 + ["B_新工艺"] * 20,
                              "assay_pct": [100.1] * 20 + [100.2] * 20})
        for policy in ("course", "welch"):
            with self.subTest(policy=policy), self.assertRaisesRegex(ValueError, "退化资料"):
                analyze_independent_t(frame, policy=policy)
        # The guard must compare the observed range, not use a broad fixed
        # tolerance that labels distinguishable low-variance samples constant.
        frame["assay_pct"] = np.r_[100.1 + np.arange(20) * 1e-10,
                                    100.2 + np.arange(20) * 1e-10]
        result = analyze_independent_t(frame, policy="welch")
        self.assertTrue(np.isfinite(result["tests"]["welch"]["statistic"]))

    def test_frozen_log_pair_values(self):
        case = self.results["paired_log_demo"]
        self.assertEqual(case["analysis_set"]["complete_pairs"], 24)
        self.assertAlmostEqual(case["paired_t"]["statistic"], -0.6238915359223507, places=9)
        self.assertAlmostEqual(case["paired_t"]["pvalue"], 0.5388380306936194, places=9)
        self.assertAlmostEqual(case["gmr_pct"], 98.09772570748653, places=8)
        np.testing.assert_allclose(case["ci90_pct"], [93.05623757542234, 103.41234547745026], atol=1e-8)
        self.assertTrue(case["interval_criterion_met"])
        self.assertEqual(case["formal_be_assessment"], "not_assessed")

    def test_interval_conclusion_changes_without_formal_be_claim(self):
        shifted = self.paired[["subject_id", "cmax_T"]].copy()
        shifted["cmax_T"] *= 0.5
        result = analyze_log_pairs(shifted, self.paired[["subject_id", "cmax_R"]])
        self.assertFalse(result["interval_criterion_met"])
        self.assertIn("未满足", result["interval_statement"])
        self.assertEqual(result["formal_be_assessment"], "not_assessed")

    def test_constant_ratios_do_not_create_false_precision_from_log_roundoff(self):
        right = pd.DataFrame({"subject_id": ["a", "b", "c"], "cmax_R": [1., 2., 3.]})
        for ratio in (1., 2.):
            with self.subTest(ratio=ratio):
                left = right.rename(columns={"cmax_R": "cmax_T"}).copy()
                left["cmax_T"] *= ratio
                with self.assertRaisesRegex(ValueError, "浮点精度"):
                    analyze_log_pairs(left, right)
        # Small, resolvable variation near 1 must remain analyzable; a fixed
        # np.isclose-to-zero default tolerance would reject these observations.
        right["cmax_R"] = 1.
        left = pd.DataFrame({"subject_id": ["a", "b", "c"],
                             "cmax_T": np.exp(np.array([1., 2., 3.]) * 1e-10)})
        result = analyze_log_pairs(left, right)
        self.assertGreater(result["sd_log_difference"], 0.)
        self.assertTrue(np.isfinite(result["paired_t"]["pvalue"]))

    def test_key_alignment_survives_shuffle_and_excludes_whole_pair(self):
        left = self.paired[["subject_id", "cmax_T"]]
        right = self.paired[["subject_id", "cmax_R"]].sample(frac=1, random_state=19)
        shuffled = analyze_log_pairs(left, right)
        self.assertAlmostEqual(shuffled["paired_t"]["pvalue"], self.results["paired_log_demo"]["paired_t"]["pvalue"], places=12)
        right = right.copy()
        right.loc[right.subject_id == "S03", "cmax_R"] = np.nan
        result = analyze_log_pairs(left, right)
        self.assertEqual(result["analysis_set"]["complete_pairs"], 23)
        self.assertEqual(result["analysis_set"]["excluded_pairs"], 1)
        self.assertNotIn("S03", result["included_ids"])
        self.assertEqual(result["analysis_set"]["exclusions"], [{"key": "S03", "reason": "missing_right"}])

    def test_duplicate_or_missing_pair_keys_are_rejected(self):
        left = pd.DataFrame({"subject_id": ["a", "a"], "value": [1, 2]})
        right = pd.DataFrame({"subject_id": ["a", "b"], "value": [2, 3]})
        with self.assertRaises(ValueError):
            align_pairs(left, right)
        left.loc[1, "subject_id"] = None
        with self.assertRaises(ValueError):
            align_pairs(left, right)

    def test_event_first_orientation_and_effects(self):
        case = self.results["adverse_events"]
        self.assertEqual(case["table"], [[24, 96], [8, 112]])
        self.assertEqual(case["column_labels"], ["发生", "未发生"])
        self.assertAlmostEqual(case["effects"]["odds_ratio_sample"]["estimate"], 3.5)
        np.testing.assert_allclose(case["effects"]["odds_ratio_sample"]["ci95"], [1.5029542306347092, 8.150614137349166], atol=1e-9)
        self.assertAlmostEqual(case["effects"]["risk_difference"]["estimate"], 0.13333333333333336)
        np.testing.assert_allclose(case["effects"]["risk_difference"]["ci95"], [0.04898836268259406, 0.21767830398407267], atol=1e-9)
        reversed_case = analyze_contingency([[96, 24], [112, 8]], column_labels=("未发生", "发生"))
        self.assertAlmostEqual(reversed_case["effects"]["odds_ratio_sample"]["estimate"], 1 / 3.5)
        self.assertIn("event=未发生", reversed_case["direction"])

    def test_fisher_is_not_reported_as_chi_square(self):
        tests = self.results["adverse_events"]["tests"]
        self.assertAlmostEqual(tests["pearson"]["statistic"], 9.23076923076923)
        self.assertAlmostEqual(tests["yates"]["statistic"], 8.11298076923077)
        self.assertAlmostEqual(tests["fisher"]["pvalue"], 0.0038347022084887932, places=10)
        self.assertNotIn("statistic", tests["fisher"])
        self.assertNotIn("df", tests["fisher"])

    def test_classroom_boundary_tables_select_different_methods(self):
        not_sparse = analyze_contingency([[3, 17], [8, 12]])
        sparse = analyze_contingency([[2, 18], [5, 15]])
        self.assertAlmostEqual(not_sparse["minimum_expected"], 5.5, places=10)
        self.assertEqual(not_sparse["primary_method"], "pearson")
        self.assertAlmostEqual(sparse["minimum_expected"], 3.5, places=10)
        self.assertEqual(sparse["primary_method"], "yates")
        self.assertEqual(analyze_contingency([[0, 11], [4, 7]])["primary_method"], "fisher")

    def test_empty_margins_and_zero_group_are_descriptive(self):
        for table in ([[30, 0], [30, 0]], [[0, 0], [2, 8]], [[0, 0], [0, 0]]):
            case = analyze_contingency(table)
            self.assertEqual(case["status"], "descriptive_only")
            self.assertFalse(case["tests"])
            self.assertFalse(case["effects"])
            if table[0] == [0, 0]:
                self.assertIsNone(case["rates"]["A药"])

    def test_isolated_zero_cell_keeps_exact_test_not_fake_wald_ci(self):
        case = analyze_contingency([[0, 20], [4, 16]])
        self.assertEqual(case["status"], "analyzed")
        self.assertAlmostEqual(case["tests"]["fisher"]["pvalue"], 0.10602910602910603, places=10)
        self.assertEqual(case["effects"]["odds_ratio_sample"]["estimate"], 0)
        self.assertIsNone(case["effects"]["odds_ratio_sample"]["ci95"])
        self.assertIsNone(case["effects"]["odds_ratio_sample"]["continuity_addition"])
        self.assertIsNone(case["effects"]["risk_difference"]["ci95"])
        self.assertEqual(case["effects"]["risk_difference"]["ci_method"], "not_estimated_sparse_or_boundary")
        infinite = analyze_contingency([[4, 16], [0, 20]])
        self.assertEqual(infinite["effects"]["odds_ratio_sample"]["estimate_status"], "infinite")
        self.assertIsNone(infinite["effects"]["odds_ratio_sample"]["estimate"])

    def test_positive_sparse_cells_do_not_receive_unqualified_wald_intervals(self):
        case = analyze_contingency([[1, 2], [12, 1]])
        self.assertEqual(case["primary_method"], "fisher")
        self.assertAlmostEqual(case["tests"]["fisher"]["pvalue"], 1 / 14, places=12)
        odds = case["effects"]["odds_ratio_sample"]
        self.assertAlmostEqual(odds["estimate"], 1 / 24, places=12)
        self.assertIsNone(odds["ci95"])
        self.assertEqual(odds["ci_method"], "not_estimated_sparse_or_zero_cell")
        self.assertIsNone(case["effects"]["risk_difference"]["ci95"])

    def test_invalid_frequency_and_unknown_codes_are_not_silently_dropped(self):
        for table in ([[0.2, 0.8], [1, 2]], [[-1, 2], [3, 4]], [[np.nan, 1], [2, 3]], [[1, 2, 3], [4, 5, 6]]):
            with self.assertRaises(ValueError):
                analyze_contingency(table)
        for frame in (pd.DataFrame({"drug": ["A药", "未知"], "adverse_event": [1, 0]}),
                      pd.DataFrame({"drug": ["A药", "B药"], "adverse_event": [1, 2]})):
            with self.assertRaises(ValueError):
                event_table(frame)

    def test_mcnemar_exact_and_asymptotic_results_remain_distinct(self):
        case = self.results["mcnemar_demo"]
        self.assertEqual(case["primary_method"], "exact_binomial")
        self.assertAlmostEqual(case["tests"]["exact_binomial"]["pvalue"], 0.022655844688415527, places=12)
        self.assertNotIn("statistic", case["tests"]["exact_binomial"])
        self.assertNotIn("df", case["tests"]["exact_binomial"])
        self.assertAlmostEqual(case["tests"]["chi_square_corrected"]["pvalue"], 0.02474467204639891, places=12)
        self.assertAlmostEqual(case["tests"]["chi_square_uncorrected"]["pvalue"], 0.014305878435429641, places=12)
        self.assertEqual(analyze_mcnemar([[12, 0], [0, 18]])["status"], "descriptive_only")
        self.assertFalse(analyze_mcnemar([[12, 0], [0, 18]])["tests"])
        self.assertEqual(analyze_mcnemar([[12, 3], [3, 18]])["tests"]["chi_square_corrected"]["statistic"], 0)

    def test_mcnemar_individual_pairs_align_by_key(self):
        left = pd.DataFrame({"subject_id": ["a", "b", "c", "d"], "positive": [1, 1, 0, 0]})
        right = pd.DataFrame({"subject_id": ["a", "b", "c", "d"], "positive": [1, 0, 1, 0]})
        result = analyze_mcnemar_pairs(left, right.sample(frac=1, random_state=2))
        self.assertEqual(result["table"], [[1, 1], [1, 1]])
        right.loc[1, "positive"] = np.nan
        self.assertEqual(analyze_mcnemar_pairs(left, right)["analysis_set"]["complete_pairs"], 3)
        with self.assertRaises(ValueError):
            analyze_mcnemar_pairs(left, pd.concat([right, right.iloc[[0]]]))

    def test_fixed_seed_generator_reproduces_csv_values_without_analysis(self):
        with tempfile.TemporaryDirectory() as temp:
            frames = generator.generate_datasets(temp)
            for filename in frames:
                pd.testing.assert_frame_equal(pd.read_csv(Path(temp) / filename), pd.read_csv(ROOT / "datasets/teaching" / filename))
            self.assertFalse((Path(temp) / "reference_outputs.txt").exists())
            with self.assertRaises(FileExistsError):
                generator.generate_datasets(temp)

    def test_cli_saves_json_csv_text_and_keeps_inputs_unchanged(self):
        paths = list((ROOT / "datasets/teaching").glob("*.csv"))
        before = {path: path.read_bytes() for path in paths}
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run"
            subprocess.run([sys.executable, str(ROOT / "scripts/analyze_teaching.py"), "--output-dir", str(output), "--t-policy", "course"], cwd=ROOT, check=True, capture_output=True, text=True)
            saved = json.loads((output / "results.json").read_text())
            self.assertEqual(saved["metadata"]["execution"]["R"], "not_executed")
            self.assertEqual(saved["metadata"]["execution"]["SPSS"], "not_executed")
            self.assertEqual(len(saved["metadata"]["inputs"]["tablet_assay"]["sha256"]), 64)
            self.assertIn("formal_be_assessment=not_assessed", (output / "summary.txt").read_text())
            fields = pd.read_csv(output / "summary.csv")["field"].tolist()
            self.assertIn("tablet_assay.tests.pooled.ci95[0]", fields)
            self.assertIn("adverse_events.effects.risk_difference.ci95[1]", fields)
            table = pd.read_csv(output / "adverse_events_table.csv", index_col=0)
            self.assertEqual(table.columns.tolist(), ["发生", "未发生"])
            self.assertEqual(table.to_numpy().tolist(), [[24, 96], [8, 112]])
            diagnostic = saved["diagnostics"]
            self.assertEqual(diagnostic["review_status"], "requires_human_review")
            self.assertEqual(diagnostic["automated_normality_decision"], "not_made")
            self.assertEqual((output / "diagnostics.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            points = pd.read_csv(output / "diagnostic_points.csv")
            self.assertEqual(points.groupby("sample").size().to_dict(),
                             {"paired_log_difference": 24, "tablet_A": 20, "tablet_B": 20})
            paired_points = points.loc[points["sample"] == "paired_log_difference"].set_index("observation_id")
            original = self.paired.set_index("subject_id")
            for key, point in paired_points.iterrows():
                self.assertAlmostEqual(point.value, np.log(original.loc[key, "cmax_T"]) - np.log(original.loc[key, "cmax_R"]), places=12)
        for path in paths:
            self.assertEqual(path.read_bytes(), before[path])

    def test_cli_requires_new_directory_and_preserves_previous_run(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "course-run"
            command = [sys.executable, str(ROOT / "scripts/analyze_teaching.py")]
            subprocess.run(command + ["--output-dir", str(output), "--t-policy", "course"],
                           cwd=ROOT, check=True, capture_output=True, text=True)
            self.assertEqual({path.name for path in output.iterdir()},
                             {"results.json", "summary.csv", "summary.txt", "adverse_events_table.csv",
                              "diagnostics.png", "diagnostic_points.csv"})
            saved = json.loads((output / "results.json").read_text())
            self.assertEqual(saved["tablet_assay"]["policy"], "course")
            (output / "student_notes.txt").write_text("本轮图形已人工查看。\n", encoding="utf-8")
            before = {path.name: path.read_bytes() for path in output.iterdir()}

            rerun = subprocess.run(command + ["--output-dir", str(output), "--t-policy", "welch"],
                                   cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(rerun.returncode, 0)
            self.assertRegex(rerun.stdout + rerun.stderr, r"新[^\n]*目录")
            self.assertEqual({path.name: path.read_bytes() for path in output.iterdir()}, before)

            new_output = Path(temp) / "welch-run"
            subprocess.run(command + ["--output-dir", str(new_output), "--t-policy", "welch"],
                           cwd=ROOT, check=True, capture_output=True, text=True)
            new_saved = json.loads((new_output / "results.json").read_text())
            self.assertEqual(new_saved["tablet_assay"]["policy"], "welch")
            self.assertEqual(new_saved["tablet_assay"]["primary_method"], "welch")
            self.assertEqual({path.name: path.read_bytes() for path in output.iterdir()}, before)

            empty_output = Path(temp) / "existing-empty"
            empty_output.mkdir()
            rejected = subprocess.run(command + ["--output-dir", str(empty_output)],
                                      cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertRegex(rejected.stdout + rejected.stderr, r"新[^\n]*目录")
            self.assertEqual(list(empty_output.iterdir()), [])

    def test_cli_rejects_existing_output_symlink_before_writing_any_file(self):
        with tempfile.TemporaryDirectory() as temp:
            data_dir = Path(temp) / "inputs"
            data_dir.mkdir()
            for name in ("tablet_assay.csv", "bioeq_cmax.csv", "adverse_events.csv"):
                (data_dir / name).write_bytes((ROOT / "datasets/teaching" / name).read_bytes())
            before = {path.name: path.read_bytes() for path in data_dir.iterdir()}
            output = Path(temp) / "existing-output"
            output.mkdir()
            link = output / "summary.csv"
            target = data_dir / "tablet_assay.csv"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"当前平台不支持创建符号链接：{error}")
            original_target = link.readlink()

            rejected = subprocess.run([sys.executable, str(ROOT / "scripts/analyze_teaching.py"),
                                       "--data-dir", str(data_dir), "--output-dir", str(output)],
                                      cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertRegex(rejected.stdout + rejected.stderr, r"新[^\n]*目录")
            self.assertEqual({path.name: path.read_bytes() for path in data_dir.iterdir()}, before)
            self.assertEqual({path.name for path in output.iterdir()}, {"summary.csv"})
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.readlink(), original_target)

    def test_qq_points_keep_ids_ties_and_do_not_certify_skewed_data(self):
        sample = diagnostic_sample("skewed", ["z", "a", "b", "c"], [100., 1., 1., 2.], "units")
        self.assertEqual([point["observation_id"] for point in sample["points"]], ["a", "b", "c", "z"])
        self.assertEqual([point["value"] for point in sample["points"]], [1., 1., 2., 100.])
        self.assertEqual(sample["n"], 4)
        self.assertTrue(np.isfinite([point["normal_quantile"] for point in sample["points"]]).all())
        self.assertNotIn("normality_passed", sample)
        for values, keys in (([1.], ["a"]), ([1., np.nan], ["a", "b"]), ([1., 2.], ["a"])):
            with self.assertRaises(ValueError):
                diagnostic_sample("invalid", keys, values, "units")

    def test_diagnostic_points_follow_analysis_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            for path in (ROOT / "datasets/teaching").glob("*.csv"):
                frame = pd.read_csv(path)
                if path.stem == "tablet_assay":
                    frame.loc[frame.tablet_id == "A01", "assay_pct"] = np.nan
                elif path.stem == "bioeq_cmax":
                    frame.loc[frame.subject_id == "S03", "cmax_R"] = np.nan
                    frame = frame.sample(frac=1, random_state=17)
                frame.to_csv(Path(temp) / path.name, index=False)
            result = run_analysis(temp)
            samples = {sample["name"]: sample for sample in result["diagnostics"]["samples"]}
            self.assertEqual(samples["tablet_A"]["n"], result["tablet_assay"]["groups"]["A"]["n"])
            self.assertEqual(samples["paired_log_difference"]["n"], result["paired_log_demo"]["analysis_set"]["complete_pairs"])
            self.assertNotIn("A01", [point["observation_id"] for point in samples["tablet_A"]["points"]])
            self.assertEqual(set(result["paired_log_demo"]["included_ids"]),
                             {point["observation_id"] for point in samples["paired_log_difference"]["points"]})


if __name__ == "__main__":
    unittest.main()
