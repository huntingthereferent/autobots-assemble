"""Offline controls for ECON-GROWTH-BACKTEST-001."""
import unittest

from econ_growth_backtest import END_YEAR, START_YEAR, TRAIN_END, score_backtest, validate_and_extract


def payload():
    rows = []
    for year in range(START_YEAR, END_YEAR + 1):
        value = float(year - 2000)
        rows.append({"date": str(year), "value": value})
    return [{"page": 1, "pages": 1, "total": len(rows)}, rows]


class EconGrowthBacktestTests(unittest.TestCase):
    def test_extracts_and_sorts_pinned_annual_series(self):
        rows = validate_and_extract(payload())
        self.assertEqual(rows[0]["year"], START_YEAR)
        self.assertEqual(rows[-1]["year"], END_YEAR)
        self.assertEqual(len(rows), END_YEAR - START_YEAR + 1)

    def test_rejects_duplicate_years(self):
        data = payload()
        data[1].append(dict(data[1][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_and_extract(data)

    def test_rejects_gaps_in_observed_annual_series(self):
        data = payload()
        data[1] = [r for r in data[1] if r["date"] != "2001"]
        with self.assertRaisesRegex(ValueError, "gaps"):
            validate_and_extract(data)

    def test_split_is_chronological_and_reports_both_baselines(self):
        rows = validate_and_extract(payload())
        result = score_backtest(rows)
        self.assertLessEqual(result["train_years"][1], TRAIN_END)
        self.assertGreater(result["test_years"][0], TRAIN_END)
        self.assertEqual(result["test_n"], END_YEAR - TRAIN_END)
        self.assertIn(result["lower_mae_baseline"], {"persistence", "training_mean", "tie"})
        self.assertEqual(len(result["test_predictions"]), result["test_n"])

    def test_pinned_live_receipt_recalculates_both_scored_baselines(self):
        import json
        from pathlib import Path
        path = (Path(__file__).parent / "observations" /
                "2026-10-22-ECON-GROWTH-BACKTEST-001-run-39827537491.json")
        archived = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(archived["run_id"], 39827537491)
        self.assertEqual(archived["source_code_commit"],
                         "d5b514f9056ff1a543ec7884aeb53ca6c6c48f82")
        self.assertFalse(archived["source_raw_response_archived"])
        r = archived["observation"]
        self.assertEqual(r["status"], "BACKTEST_COMPLETE")
        self.assertRegex(r["source"]["response_sha256"], r"^[0-9a-f]{64}$")
        scored = r["result"]
        observations = scored["test_predictions"]
        self.assertEqual(scored["train_years"], [1990, 2014])
        self.assertEqual(scored["test_years"], [2015, 2023])
        self.assertEqual(scored["test_n"], 9)
        self.assertEqual([x["year"] for x in observations], list(range(2015, 2024)))
        def mae(key):
            return sum(abs(x["actual"] - x[key]) for x in observations) / len(observations)
        self.assertAlmostEqual(mae("persistence_prediction"),
                               scored["persistence_mae_percentage_points"], places=12)
        self.assertAlmostEqual(mae("train_mean_prediction"),
                               scored["training_mean_mae_percentage_points"], places=12)
        self.assertLess(scored["training_mean_mae_percentage_points"],
                        scored["persistence_mae_percentage_points"])
        self.assertEqual(scored["lower_mae_baseline"], "training_mean")
        self.assertEqual(archived["license_context"]["third_party_indicator_exception_review"],
                         "REQUIRED_BEFORE_REDISTRIBUTING_DATA")



if __name__ == "__main__":
    unittest.main()
