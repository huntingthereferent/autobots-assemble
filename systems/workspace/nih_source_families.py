"""Independent synthetic source-family stress test of ORIGINAL NIH P2 Python.

This is a separate read-only experiment after the twelve-job native benchmark.
It does not admit an additional handoff or claim NIH or clinical validation.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
import argparse
import json

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_benchmark_bridge import JOB_ID, NIHBenchmarkBridge, canonical
from .nih_benchmark_temporal_join import join as original_twelve
from .nih_dataset_sensitivity import run_experiment
from .nih_scope_native import validate_scope
from .workstation import ProcessWorkstation

SCHEMA = "nih-p2-source-families/v1"
LABEL = "nih-p2-source-families"
PROTOTYPE_JOB = "nih-prototype-001"
TEST_JOB = "nih-p2-game-test-001"
# New layouts are constructed from the original synthetic two-record fixture.
# These are controlled counterfactual families, not independent external data.
FAMILY_SIZES = (
    ("four-mixed", 4),
    ("six-overlap", 6),
    ("nine-conflicts", 9),
    ("twelve-late", 12),
    ("sixteen-sources", 16),
)


def day(offset):
    return (date(2026, 1, 1) + timedelta(days=offset)).isoformat()


def families(original):
    base = validate_scope(original)
    result = {"original": deepcopy(base)}
    for variant, (name, size) in enumerate(FAMILY_SIZES):
        change = deepcopy(base)
        for i in range(size - len(base["observations"])):
            subject = "fictional-case" if name == "nine-conflicts" and i % 2 == 0 else (
                "fictional-subject-" + str((i + variant) % 4))
            predicate = "has-status" if (name == "nine-conflicts" or i % 3 == 0) else "has-result"
            change["observations"].append({
                "id": f"family-{variant}-{i:02d}",
                "subject": subject,
                "predicate": predicate,
                "object": f"synthetic-value-{variant}-{i % 5}",
                "valid_from": day((i + variant * 2) % 7),
                "valid_to": day(10 + (i * 2 + variant) % 7),
                "known_at": day((i * 3 + variant * 2) % 13),
                "source_ref": f"synthetic-origin-{variant}-{i % 5}",
            })
        validated = validate_scope(change)
        if len(validated["observations"]) != size:
            raise ValueError("synthetic family does not match declared size")
        result[name] = validated
    if len({canonical(s["observations"]) for s in result.values()}) != len(result):
        raise ValueError("duplicate synthetic source families")
    return result


def join(*, data_dir, output_dir):
    data, out = Path(data_dir), Path(output_dir)
    parent = original_twelve(data_dir=data, output_dir=out)
    if parent["native_jobs"] != 12 or parent["NIH_P2_BENCHMARK"] != "WITNESSED":
        raise ValueError("original benchmark did not pass independent verification")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    bridge = NIHBenchmarkBridge(runtime=runtime, workstation=ProcessWorkstation(data / "workstation"))
    handoff = runtime.get(JOB_ID)
    folder = bridge._pinned(handoff)
    prototype = runtime.state(PROTOTYPE_JOB).output["prototype"]
    original_inputs = runtime.get(PROTOTYPE_JOB).inputs
    test = runtime.state(TEST_JOB).output["report"]
    before = (data / "runtime.jsonl").read_bytes()
    result = run_experiment(
        scope=original_inputs["scope"],
        predicates=original_inputs["reasoning_request"]["functional_predicates"],
        code=prototype["python_source"],
        dataset_text=prototype["dataset_json"],
        worker_source=folder / "benchmark_worker.py",
        query_history_sha256=test["query_history_sha256"],
        output_dir=out,
        edition_fingerprint=handoff.metadata["edition_fingerprint"],
        sources=families(original_inputs["scope"]),
        label=LABEL,
        experiment_schema=SCHEMA,
    )
    if (data / "runtime.jsonl").read_bytes() != before:
        raise ValueError("source-family research changed the twelve-job native journal")
    if result["variation_count"] != len(FAMILY_SIZES) + 1:
        raise ValueError("synthetic family experiment omitted cases")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    print(canonical(join(data_dir=args.data_dir, output_dir=args.output_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
