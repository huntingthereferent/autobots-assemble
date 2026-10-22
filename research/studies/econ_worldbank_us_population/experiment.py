"""ECON lane: bounded revised-snapshot population forecast backtest.

One World Bank WDI indicator, US population, 1990-2023. Fixed horizon one
calendar year; forecast comparison of persistence and a past-only five-year
drift. This is a retrospective comparison on revised data, not a real-time
vintage-correct forecast or a claim about causes of population change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DATA_URL = (
    "https://api.worldbank.org/v2/country/US/indicator/SP.POP.TOTL"
    "?format=json&date=1990%3A2023&per_page=50"
)
SOURCE_ID = "worldbank"
SOURCE_INDICATOR = "SP.POP.TOTL"
START_YEAR = 1990
END_YEAR = 2023
BACKTEST_START = 2014
BACKTEST_END = 2023
EXPECTED_COUNT = END_YEAR - START_YEAR + 1
SOURCE_RECEIPT_SHA256 = "b7d97d40e1d86955bac3ca5bbc4fe534f1872c505479392e029e37f99d8e605c"
SOURCE_RECEIPT_URL = "https://github.com/huntingthereferent/autobots-assemble/actions/runs/39771470448"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_exact(opener=None) -> bytes:
    loc = urlsplit(DATA_URL)
    if (loc.scheme != "https" or loc.hostname != "api.worldbank.org"
            or loc.username or loc.password):
        raise ValueError("source address outside the allowed public host")
    client = opener if opener is not None else build_opener(NoRedirect)
    with client.open(Request(DATA_URL, headers={
            "Accept": "application/json", "User-Agent": "HuntingReferentResearch/1.0 econ-wdi"
    }), timeout=20) as response:
        if response.status != 200:
            raise ValueError("non-200 World Bank source status")
        if urlsplit(response.geturl()).hostname != "api.worldbank.org":
            raise ValueError("redirected outside the World Bank")
        raw = response.read(120001)
    if len(raw) > 120000:
        raise ValueError("bounded source byte limit exceeded")
    return raw


def parse_series(raw: bytes) -> dict[int, int]:
    payload = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("unexpected World Bank API envelope")
    meta, observations = payload
    if not isinstance(meta, dict) or not isinstance(observations, list):
        raise ValueError("missing source metadata or observations")
    if (int(meta.get("page", 0)) != 1 or int(meta.get("pages", 0)) != 1 or
            int(meta.get("total", 0)) != EXPECTED_COUNT or
            len(observations) != EXPECTED_COUNT):
        raise ValueError("source page count or observation count changed")
    years = {}
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("invalid observation record")
        year = int(row.get("date", "0"))
        country = row.get("country") or {}
        indicator = row.get("indicator") or {}
        if (row.get("countryiso3code") != "USA" or country.get("id") != "US" or
                indicator.get("id") != SOURCE_INDICATOR):
            raise ValueError("different country or indicator returned")
        if year < START_YEAR or year > END_YEAR or year in years:
            raise ValueError("observation year outside fixed scope or duplicated")
        value = row.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("missing or nonnumeric population")
        if not math.isfinite(value) or value <= 0 or value != int(value):
            raise ValueError("population is nonfinite, nonpositive or not an integer")
        if row.get("obs_status") not in ("", None, "A"):
            raise ValueError("forecast or unrecognized observation status")
        years[year] = int(value)
    if set(years) != set(range(START_YEAR, END_YEAR + 1)):
        raise ValueError("missing years in source series")
    return years


def forecasts(series: dict[int, int], target_year: int) -> tuple[float, float]:
    """No target-year or subsequent value may enter either prediction."""
    if not BACKTEST_START <= target_year <= BACKTEST_END:
        raise ValueError("year outside frozen historical backtest")
    past_year = target_year - 1
    old_year = target_year - 6
    if past_year not in series or old_year not in series:
        raise ValueError("prediction requires only six prior years")
    latest, old = series[past_year], series[old_year]
    persistence = float(latest)
    five_year_drift = latest + (latest - old) / 5
    return persistence, float(five_year_drift)


def measure(series: dict[int, int]) -> dict:
    if set(series) != set(range(START_YEAR, END_YEAR + 1)):
        raise ValueError("incomplete bounded historical source")
    ledger = []
    for year in range(BACKTEST_START, BACKTEST_END + 1):
        baseline, drift = forecasts(series, year)
        actual = series[year]
        ledger.append({
            "year": year,
            "persistence_absolute_error": round(abs(actual - baseline), 6),
            "drift_absolute_error": round(abs(actual - drift), 6),
        })
    n = len(ledger)
    base_mae = sum(r["persistence_absolute_error"] for r in ledger) / n
    drift_mae = sum(r["drift_absolute_error"] for r in ledger) / n
    return {
        "indicator": SOURCE_INDICATOR,
        "country_iso3": "USA",
        "unit": "persons",
        "input_start_year": START_YEAR,
        "input_end_year": END_YEAR,
        "held_out_start_year": BACKTEST_START,
        "held_out_end_year": BACKTEST_END,
        "one_year_horizon": True,
        "n_years": len(series),
        "n_backtest": n,
        "rules": {
            "persistence": "forecast(y) = published_value(y-1)",
            "five_year_drift": "forecast(y) = value(y-1) + (value(y-1)-value(y-6))/5",
        },
        "persistence_mae_persons": base_mae,
        "drift_mae_persons": drift_mae,
        "drift_minus_persistence_mae_persons": drift_mae - base_mae,
        "drift_outperforms_baseline": drift_mae < base_mae,
        "per_year_error_ledger": ledger,
        "limits": (
            "Backtest on a single retrieval-vintage revised World Bank source. "
            "Not independently timestamp-vintage-correct and not a real-time future forecast. "
            "No uncertainty interval, causal explanation, or across-country generalization."
        ),
    }


def live() -> dict:
    raw = fetch_exact()
    observed = datetime.now(timezone.utc).isoformat()
    data = parse_series(raw)
    metrics = measure(data)
    return {
        "schema_version": 1, "lane_id": "ECON",
        "state": "MEASURED_REVISED_SNAPSHOT",
        "scientific_experiments_run": 1,
        "record_identifier": "World Bank / WDI / USA / SP.POP.TOTL / 1990-2023",
        "retrieved_at_utc": observed,
        "source_url": DATA_URL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_receipt_ref": SOURCE_RECEIPT_URL,
        "source_receipt_sha256": SOURCE_RECEIPT_SHA256,
        "source_data_redistributed": False,
        "source_license": "World Development Indicators, CC BY 4.0; World Bank Dataset Terms apply",
        "measured": metrics,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Only the exact public WDI time-series query")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1, "lane_id": "ECON",
        "state": "UNOBSERVED", "scientific_experiments_run": 0,
        "reason": "Run explicitly with --live after reviewing source scope."
    }
    if args.live:
        try:
            result = live()
        except (HTTPError, URLError, ValueError, TimeoutError, OSError,
                UnicodeError, json.JSONDecodeError) as exc:
            result = {
                "schema_version": 1, "lane_id": "ECON", "state": "SOURCE_WALL",
                "scientific_experiments_run": 0,
                "error_class": type(exc).__name__,
                "error": str(exc)[:180], "source_url": DATA_URL,
            }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 2 if result["state"] == "SOURCE_WALL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
