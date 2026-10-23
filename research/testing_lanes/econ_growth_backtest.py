"""ECON-GROWTH-BACKTEST-001: one-country historical baseline comparison.

Fetches one public World Bank indicator series and compares two predeclared
one-step annual baselines on a held-out interval. It is descriptive and does not
claim a general economic forecasting advantage or causal explanation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

COUNTRY = "USA"
INDICATOR = "NY.GDP.MKTP.KD.ZG"
START_YEAR = 1990
END_YEAR = 2023
TRAIN_END = 2014
MAX_RESPONSE_BYTES = 500_000
ENDPOINT = (
    f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{INDICATOR}"
    f"?date={START_YEAR}:{END_YEAR}&format=json&per_page=100"
)


def validate_and_extract(payload: object) -> list[dict]:
    if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[1], list):
        raise ValueError("World Bank response must contain metadata and a record list")
    records = []
    seen_years = set()
    for row in payload[1]:
        if not isinstance(row, dict):
            raise ValueError("series row must be an object")
        year_text = row.get("date")
        value = row.get("value")
        if not isinstance(year_text, str) or not year_text.isdigit():
            raise ValueError("invalid observation year")
        year = int(year_text)
        if not START_YEAR <= year <= END_YEAR:
            raise ValueError("observation outside frozen year window")
        if year in seen_years:
            raise ValueError("duplicate year")
        seen_years.add(year)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError("observation value must be finite numeric or null")
        records.append({"year": year, "value": float(value)})
    records.sort(key=lambda r: r["year"])
    if len(records) < 20:
        raise ValueError("too few non-null annual observations for bounded backtest")
    if any(b["year"] != a["year"] + 1 for a, b in zip(records, records[1:])):
        raise ValueError("annual series has gaps after null removal; do not silently bridge years")
    return records


def score_backtest(records: list[dict]) -> dict:
    train = [r for r in records if r["year"] <= TRAIN_END]
    test = [r for r in records if r["year"] > TRAIN_END]
    if len(train) < 10 or len(test) < 5:
        raise ValueError("insufficient train/test observations for frozen split")
    train_mean = sum(r["value"] for r in train) / len(train)
    by_year = {r["year"]: r["value"] for r in records}
    predictions = []
    for row in test:
        previous_year = row["year"] - 1
        if previous_year not in by_year:
            raise ValueError("one-step persistence baseline lacks prior-year observation")
        actual = row["value"]
        predictions.append({
            "year": row["year"],
            "actual": actual,
            "persistence_prediction": by_year[previous_year],
            "train_mean_prediction": train_mean,
        })
    def mae(key: str) -> float:
        return sum(abs(p["actual"] - p[key]) for p in predictions) / len(predictions)
    persistence_mae = mae("persistence_prediction")
    mean_mae = mae("train_mean_prediction")
    return {
        "country": COUNTRY,
        "indicator": INDICATOR,
        "train_years": [train[0]["year"], train[-1]["year"]],
        "test_years": [test[0]["year"], test[-1]["year"]],
        "train_n": len(train),
        "test_n": len(test),
        "frozen_training_mean": train_mean,
        "persistence_mae_percentage_points": persistence_mae,
        "training_mean_mae_percentage_points": mean_mae,
        "lower_mae_baseline": "persistence" if persistence_mae < mean_mae else (
            "training_mean" if mean_mae < persistence_mae else "tie"
        ),
        "test_predictions": predictions,
    }


def fetch_payload() -> tuple[object, str]:
    request = Request(ENDPOINT, headers={"User-Agent": "bounded-research-witness/1.0"})
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"World Bank API returned HTTP {response.status}")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("response exceeded configured byte cap")
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def build_receipt(payload: object, raw_sha256: str) -> dict:
    records = validate_and_extract(payload)
    result = score_backtest(records)
    return {
        "schema_version": 1,
        "experiment_id": "ECON-GROWTH-BACKTEST-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "BACKTEST_COMPLETE",
        "source": {"name": "World Bank Indicators API", "endpoint": ENDPOINT,
                   "response_sha256": raw_sha256, "max_response_bytes": MAX_RESPONSE_BYTES},
        "method": {
            "target": "annual real GDP growth (NY.GDP.MKTP.KD.ZG)",
            "split": f"train <= {TRAIN_END}; held-out one-step predictions > {TRAIN_END}",
            "baselines": ["previous year's observed value", "fixed mean of training period"],
            "metric": "mean absolute error in percentage points",
            "revision_policy": "one retrieved API snapshot; no vintage archive reconstructed",
        },
        "result": result,
        "limits": [
            "One country, one indicator and one frozen retrieval snapshot only.",
            "The API may revise historical values; no real-time data vintage was reconstructed.",
            "Baseline comparison is descriptive and not a general forecasting or causal claim.",
            "No future observations are used to fit the training mean; persistence uses only the previous year's observed value."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload, digest = fetch_payload()
    receipt = build_receipt(payload, digest)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
