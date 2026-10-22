"""Synthetic-only regression tests for source-bound WDI temporal baseline comparison."""
import json
import unittest

from experiment import DATA_URL, fetch_exact, parse_series, measure, forecasts


def series_with_increment(increment=1000):
    return {year: 1000000 + (year - 1990) * increment for year in range(1990, 2024)}


def api_body(data=None):
    values = data or series_with_increment()
    return json.dumps([
        {"page": 1, "pages": 1, "per_page": 50, "total": 34},
        [{"countryiso3code": "USA", "country": {"id": "US", "value": "United States"},
          "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
          "date": str(year), "value": value, "obs_status": ""}
         for year, value in sorted(values.items(), reverse=True)]
    ]).encode()


class Response:
    status = 200

    def __init__(self, data, source=DATA_URL):
        self.data, self.source = data, source

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def geturl(self):
        return self.source

    def read(self, n):
        return self.data[:n]


class Transport:
    def __init__(self, data, source=DATA_URL):
        self.data = data
        self.source = source

    def open(self, request, timeout=20):
        if request.full_url != DATA_URL:
            raise AssertionError("query changed")
        return Response(self.data, self.source)


class WDIStudyTests(unittest.TestCase):
    def test_exact_source_and_complete_series(self):
        x = fetch_exact(opener=Transport(api_body()))
        self.assertEqual(parse_series(x), series_with_increment())

    def test_wrong_country_does_not_enter_population_series(self):
        b = api_body().replace(b'"countryiso3code": "USA"', b'"countryiso3code": "CAN"', 1)
        with self.assertRaisesRegex(ValueError, "country"):
            parse_series(b)

    def test_wrong_indicator_rejected(self):
        b = api_body().replace(b'"id": "SP.POP.TOTL"', b'"id": "NY.GDP.MKTP.CD"', 1)
        with self.assertRaisesRegex(ValueError, "country or indicator"):
            parse_series(b)

    def test_historical_series_must_have_every_year(self):
        values = series_with_increment()
        del values[2004]
        with self.assertRaisesRegex(ValueError, "count"):
            parse_series(api_body(values))

    def test_duplicate_year_rejected(self):
        decoded = json.loads(api_body())
        decoded[1][1]["date"] = decoded[1][0]["date"]
        with self.assertRaisesRegex(ValueError, "duplicated"):
            parse_series(json.dumps(decoded).encode())

    def test_forecast_status_is_not_history(self):
        d = json.loads(api_body())
        d[1][0]["obs_status"] = "F"
        with self.assertRaisesRegex(ValueError, "status"):
            parse_series(json.dumps(d).encode())

    def test_null_population_is_explicit_missing_data(self):
        d = json.loads(api_body())
        d[1][0]["value"] = None
        with self.assertRaisesRegex(ValueError, "nonnumeric"):
            parse_series(json.dumps(d).encode())

    def test_positive_linear_trend_is_narrow_example(self):
        r = measure(series_with_increment(1000))
        self.assertEqual(r["n_backtest"], 10)
        self.assertEqual(r["persistence_mae_persons"], 1000)
        self.assertEqual(r["drift_mae_persons"], 0)
        self.assertTrue(r["drift_outperforms_baseline"])

    def test_constant_series_has_no_artificial_winner(self):
        r = measure(series_with_increment(0))
        self.assertEqual(r["persistence_mae_persons"], 0)
        self.assertEqual(r["drift_mae_persons"], 0)
        self.assertFalse(r["drift_outperforms_baseline"])

    def test_no_target_leakage_or_future_retrofit(self):
        values = series_with_increment()
        p = forecasts(values, 2018)
        # Changing 2018 or later values must not alter a 2018 prediction.
        for year in range(2018, 2024):
            values[year] = 9999999999
        self.assertEqual(p, forecasts(values, 2018))

    def test_window_cannot_be_retrained_to_future_without_changing_contract(self):
        with self.assertRaisesRegex(ValueError, "frozen"):
            forecasts(series_with_increment(), 2024)
        with self.assertRaisesRegex(ValueError, "frozen"):
            forecasts(series_with_increment(), 2013)

    def test_source_size_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "byte limit"):
            fetch_exact(opener=Transport(b"x" * 120001))

    def test_unexpected_redirect_is_wall(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            fetch_exact(opener=Transport(api_body(), "https://example.com/data"))

    def test_missing_year_cannot_be_backtested(self):
        values = series_with_increment()
        del values[2012]
        with self.assertRaisesRegex(ValueError, "incomplete"):
            measure(values)

    def test_archived_source_witness_preserves_unfavorable_years(self):
        from pathlib import Path
        witness = json.loads((Path(__file__).parent / "observations" /
                              "2026-10-22-run-39785188011.json").read_text(encoding="utf-8"))
        r = witness["result"]
        self.assertEqual(witness["run_id"], 39785188011)
        self.assertEqual(r["state"], "MEASURED_REVISED_SNAPSHOT")
        self.assertEqual(r["source_sha256"],
                         "39dbc6b900f4a4f44fd42001346d71be15df08b605e44463329265fbfdc5bdbc")
        measured = r["measured"]
        self.assertEqual(measured["n_backtest"], 10)
        self.assertEqual(measured["persistence_mae_persons"], 2002877.0)
        self.assertEqual(measured["drift_mae_persons"], 546083.24)
        ledger = measured["per_year_error_ledger"]
        self.assertEqual([x["year"] for x in ledger], list(range(2014, 2024)))
        unfavorable = [x for x in ledger if x["drift_absolute_error"] > x["persistence_absolute_error"]]
        self.assertGreater(len(unfavorable), 0)
        self.assertIn(2021, [x["year"] for x in unfavorable])



if __name__ == "__main__":
    unittest.main()
