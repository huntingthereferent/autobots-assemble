"""COMP-SORT-COMPARISON-001: stable merge sort vs Python's sorted baseline.

Uses the same frozen deterministic inputs and comparison relation. Reports
comparison counts and exact output equivalence; it makes no wall-clock or
general algorithm superiority claim. No network access or external dataset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
from datetime import datetime, timezone
from pathlib import Path

SEED = 20261022
N = 512


def compare(a, b):
    return (a[0] > b[0]) - (a[0] < b[0])


def merge_sort(items, cmp, counter):
    """Stable top-down merge sort; counter is incremented for each key compare."""
    if len(items) < 2:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], cmp, counter)
    right = merge_sort(items[middle:], cmp, counter)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if cmp(left[i], right[j]) <= 0:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def fixed_cases():
    rng = random.Random(SEED)
    random_values = [rng.randrange(0, 64) for _ in range(N)]
    ascending = list(range(N))
    descending = list(reversed(ascending))
    duplicates = [7] * N
    organ_pipe = list(range(N // 2)) + list(reversed(range(N // 2)))
    alternating = [i % 2 for i in range(N)]
    return {
        "seeded_duplicates": random_values,
        "ascending": ascending,
        "descending": descending,
        "all_equal": duplicates,
        "organ_pipe": organ_pipe,
        "two_value_alternation": alternating,
    }


def measure(values):
    # Index preserves an observable identity for stable ordering on equal keys.
    records = [(value, index) for index, value in enumerate(values)]
    baseline_count = [0]

    def counted_cmp(a, b):
        baseline_count[0] += 1
        return compare(a, b)

    # Baseline uses Python's production Timsort, with the same comparator.
    from functools import cmp_to_key
    baseline = sorted(records, key=cmp_to_key(counted_cmp))
    candidate_count = [0]
    candidate = merge_sort(records, compare, candidate_count)
    return {
        "items": len(records),
        "input_sha256": hashlib.sha256(
            json.dumps(values, separators=(",", ":")).encode()
        ).hexdigest(),
        "outputs_equal": candidate == baseline,
        "baseline_stable": baseline == sorted(baseline, key=lambda item: item[0]),
        "baseline_comparisons": baseline_count[0],
        "candidate_comparisons": candidate_count[0],
        "candidate_comparison_delta": candidate_count[0] - baseline_count[0],
        "candidate_uses_fewer_comparisons": candidate_count[0] < baseline_count[0],
    }


def build_receipt():
    results = {name: measure(values) for name, values in fixed_cases().items()}
    return {
        "schema_version": 1,
        "experiment_id": "COMP-SORT-COMPARISON-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETED_BOUNDED_COMPARISON",
        "question": "Does stable merge sort reduce comparisons against Python sorted on the same inputs?",
        "baseline": "Python sorted/Timsort with the same comparator relation",
        "candidate": "stable top-down merge sort",
        "seed": SEED,
        "cases": results,
        "all_outputs_equal": all(row["outputs_equal"] for row in results.values()),
        "all_baselines_stable": all(row["baseline_stable"] for row in results.values()),
        "environment": {"python": platform.python_version(), "implementation": platform.python_implementation()},
        "limits": [
            "Comparison counts are not wall-clock runtime or memory measurements.",
            "Six deterministic synthetic input shapes do not establish general superiority.",
            "No external dataset or source paper was used; this is a controlled implementation comparison.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = build_receipt()
    if not receipt["all_outputs_equal"] or not receipt["all_baselines_stable"]:
        raise SystemExit("comparison witness failed")
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
