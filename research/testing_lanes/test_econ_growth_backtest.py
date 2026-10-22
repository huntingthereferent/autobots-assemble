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


if __name__ == "__main__":
    unittest.main()
