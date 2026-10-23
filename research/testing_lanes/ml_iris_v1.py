"""ML-OPENML-IRIS-001: fixed 1-NN vs majority baseline on OpenML Iris v1.

Default is offline. --live downloads exactly OpenML dataset 61/version 1 from
its fixed public endpoint, verifies the expected 150x4+label shape, then uses
a seeded stratified holdout. The source bytes are hashed, not archived.
This is a small benchmark witness, not a claim about general ML capability.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DATASET_ID = 61
DATASET_VERSION = 1
SOURCE_URL = "https://www.openml.org/data/v1/download/61/iris.arff"
MAX_BYTES = 100_000
TIMEOUT = 15
SEED = 42
TEST_PER_CLASS = 15
EXPECTED_LABELS = {"Iris-setosa", "Iris-versicolor", "Iris-virginica"}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def parse_arff(raw: bytes) -> list[tuple[tuple[float, ...], str]]:
    text = raw.decode("utf-8-sig")
    in_data = False
    rows = []
    attributes = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        if not in_data:
            if line.lower().startswith("@attribute"):
                attributes += 1
            if line.lower() == "@data":
                in_data = True
            continue
        values = next(csv.reader([line], skipinitialspace=True))
        if len(values) != 5 or any(value.strip() in {"", "?"} for value in values):
            raise ValueError("unexpected row shape or missing value")
        features = tuple(float(value.strip()) for value in values[:4])
        label = values[4].strip()
        if label not in EXPECTED_LABELS:
            raise ValueError("unexpected class label")
        rows.append((features, label))
    if attributes != 5 or len(rows) != 150:
        raise ValueError("dataset does not match pinned Iris v1 shape")
    counts = Counter(label for _, label in rows)
    if set(counts) != EXPECTED_LABELS or any(counts[label] != 50 for label in EXPECTED_LABELS):
        raise ValueError("dataset does not match expected balanced class counts")
    return rows


def stratified_split(rows, seed=SEED):
    rng = random.Random(seed)
    by_class = {label: [] for label in EXPECTED_LABELS}
    for index, row in enumerate(rows):
        by_class[row[1]].append(index)
    train, test = [], []
    for label in sorted(by_class):
        indices = by_class[label][:]
        rng.shuffle(indices)
        test.extend(indices[:TEST_PER_CLASS])
        train.extend(indices[TEST_PER_CLASS:])
    return sorted(train), sorted(test)


def nearest_label(point, train_rows):
    best_distance = None
    best_label = None
    for features, label in train_rows:
        distance = sum((a - b) ** 2 for a, b in zip(point, features))
        if best_distance is None or distance < best_distance or (
            distance == best_distance and label < best_label
        ):
            best_distance, best_label = distance, label
    return best_label


def evaluate(rows, seed=SEED):
    train_ids, test_ids = stratified_split(rows, seed)
    if set(train_ids) & set(test_ids):
        raise ValueError("train/test leakage: row indices overlap")
    train_rows = [rows[i] for i in train_ids]
    test_rows = [rows[i] for i in test_ids]
    counts = Counter(label for _, label in train_rows)
    baseline_label = sorted(counts, key=lambda label: (-counts[label], label))[0]
    predictions = [nearest_label(features, train_rows) for features, _ in test_rows]
    actual = [label for _, label in test_rows]
    baseline_correct = sum(label == baseline_label for label in actual)
    model_correct = sum(pred == label for pred, label in zip(predictions, actual))
    confusion = {
        label: {
            predicted: sum(
                actual[i] == label and predictions[i] == predicted
                for i in range(len(actual))
            )
            for predicted in sorted(EXPECTED_LABELS)
        }
        for label in sorted(EXPECTED_LABELS)
    }
    n = len(test_rows)
    return {
        "seed": seed,
        "split": "stratified_holdout_70_30",
        "train_rows": len(train_rows),
        "test_rows": n,
        "train_test_overlap": 0,
        "baseline": {"kind": "majority_class", "label": baseline_label,
                     "correct": baseline_correct, "accuracy": baseline_correct / n},
        "model": {"kind": "1_nearest_neighbor_euclidean_raw_features",
                  "correct": model_correct, "accuracy": model_correct / n},
        "confusion_matrix_rows_actual_columns_predicted": confusion,
        "outcome": "1NN_BEATS_BASELINE" if model_correct > baseline_correct else
                   "BASELINE_NOT_BEATEN",
    }


def run_live(opener=None):
    receipt = {
        "schema_version": 1,
        "lane_id": "ML",
        "experiment_id": "ML-OPENML-IRIS-001",
        "source_id": "openml",
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "source_url": SOURCE_URL,
        "state": "SOURCE_WALL",
        "data_archived": False,
        "model_tuned": False,
        "generalization_claim": False,
    }
    client = opener if opener is not None else build_opener(NoRedirect)
    try:
        req = Request(SOURCE_URL, headers={
            "Accept": "text/plain,application/octet-stream",
            "User-Agent": "Aeren-ML-bounded-benchmark/1.0",
        })
        with client.open(req, timeout=TIMEOUT) as response:
            if response.status != 200:
                raise ValueError("non-200 OpenML response")
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("dataset byte ceiling exceeded")
        rows = parse_arff(raw)
        metrics = evaluate(rows)
        receipt.update({
            "state": "BENCHMARK_OBSERVED",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "response_status": 200,
            "response_bytes": len(raw),
            "dataset_sha256": hashlib.sha256(raw).hexdigest(),
            "row_count": len(rows),
            "feature_count": 4,
            "class_counts": dict(sorted(Counter(label for _, label in rows).items())),
            "metrics": metrics,
            "boundary": "One small fixed dataset and one seeded holdout; not a general ML claim.",
        })
    except HTTPError as exc:
        receipt.update({"state": "SOURCE_WALL", "error_class": type(exc).__name__,
                        "http_status": exc.code,
                        "redirect_denied": exc.code in {301, 302, 303, 307, 308}})
    except (URLError, ValueError, TimeoutError, OSError, UnicodeError) as exc:
        receipt.update({"state": "SOURCE_WALL", "error_class": type(exc).__name__})
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Fetch one fixed public OpenML dataset")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.live:
        receipt = run_live()
    else:
        receipt = {
            "schema_version": 1, "lane_id": "ML", "experiment_id": "ML-OPENML-IRIS-001",
            "state": "UNOBSERVED", "dataset_id": DATASET_ID, "dataset_version": DATASET_VERSION,
            "reason": "offline default; pass --live to fetch the pinned public dataset",
        }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if receipt["state"] in {"UNOBSERVED", "BENCHMARK_OBSERVED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
