"""Independent synthetic source challenges for the original NIH P2 executable.

Construct fresh synthetic records (not mutations of the original source) and
test query semantics plus metamorphic relations using the unchanged generated
temporal_query.py, original source-pinned benchmark worker, and independent
observation oracle. This is NOT a native CP, NIH result, or clinical evaluation.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess
import sys

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_benchmark_bridge import JOB_ID, NIHBenchmarkBridge, canonical
from .nih_benchmark_temporal_join import join as original_twelve
from .nih_prototype_native import oracle
from .nih_scope_native import validate_scope
from .workstation import ProcessWorkstation

SCHEMA = "nih-p2-independent-synthetic-metamo/v1"
SEEDS_AND_SIZES = ((1, 2), (2, 4), (3, 7), (4, 12), (5, 16))
PROTOTYPE_JOB = "nih-prototype-001"
TEST_JOB = "nih-p2-game-test-001"


def day(n):
    return (date(2026, 1, 1) + timedelta(days=n)).isoformat()


def independent_scope(seed, size):
    """No values, identities, or observations copied from original source."""
    if type(seed) is not int or type(size) is not int or not 2 <= size <= 16:
        raise ValueError("bounded independent synthetic source required")
    rows = [
        {"id": f"independent-early-{seed}", "subject": "fictional-case",
         "predicate": "has-status", "object": "baseline-value",
         "valid_from": day(2), "valid_to": day(11), "known_at": day(0),
         "source_ref": f"independent-baseline-{seed}"},
        {"id": f"independent-late-{seed}", "subject": "fictional-case",
         "predicate": "has-result", "object": "delayed-value",
         "valid_from": day(2), "valid_to": day(11), "known_at": day(7),
         "source_ref": f"independent-delay-{seed}"},
    ]
    for i in range(size - 2):
        rows.append({
            "id": f"independent-{seed}-{i:02d}",
            "subject": f"fictional-subject-{(seed+i) % 5}",
            "predicate": "has-status" if i % 2 == 0 else "has-result",
            "object": f"independent-value-{seed}-{i % 7}",
            "valid_from": day(1 + (i + seed) % 4),
            "valid_to": day(11 + (i * 2 + seed) % 7),
            "known_at": day((i * 3 + seed) % 15),
            "source_ref": f"independent-origin-{seed}-{i % 7}",
        })
    return validate_scope({
        "kind": "temporal-scope/v1", "synthetic": True,
        "case_id": f"independent-seed-{seed}",
        "application": "research-evidence",
        "question": "Which synthetic records were available at a given point in time?",
        "query_at": day(4), "target_at": day(4), "observations": rows,
    })


def queries():
    return [
        {"known_at": day(k), "target_at": day(v)}
        for k in (0, 4, 6, 7, 9) for v in (3, 4, 10, 11, 16)
    ]


def run_experiment(*, code, parent_dataset, worker_source,
                   original_observations, query_history_sha256,
                   parent_fingerprint, output_dir):
    if not isinstance(code, str) or not code.strip():
        raise ValueError("real emitted original temporal Python is required")
    if not isinstance(query_history_sha256, str) or len(query_history_sha256) != 64:
        raise ValueError("original browser provenance digest required")
    if not isinstance(parent_fingerprint, str) or not parent_fingerprint:
        raise ValueError("original source-owner fingerprint required")
    parent = json.loads(parent_dataset)
    if parent.get("synthetic") is not True or not isinstance(parent.get("functional_predicates"), list):
        raise ValueError("original synthetic runnable prototype dataset is missing")
    if parent["observations"] != original_observations:
        raise ValueError("original source observations differ")
    predicates = parent["functional_predicates"]
    if "has-status" not in predicates or "has-result" not in predicates:
        raise ValueError("metamorphic experiment requires actual native declared predicates")
    src = Path(worker_source)
    if not src.is_file() or src.is_symlink():
        raise ValueError("source-pinned benchmark worker file absent")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    logs = []
    summaries = []
    grid = queries()
    assert len(grid) == 25
    with TemporaryDirectory() as td:
        folder = Path(td)
        executable = folder / "temporal_query.py"
        executable.write_text(code, encoding="utf8")
        worker = folder / "benchmark_worker.py"
        worker.write_bytes(src.read_bytes())
        dataset_file = folder / "temporal_dataset.json"

        def execute(scope, request, *, independent=True):
            # Exact original emitted Python program (never an in-memory stand-in).
            dataset = dict(parent)
            dataset["observations"] = scope["observations"]
            dataset["case_id"] = scope["case_id"]
            dataset_file.write_text(canonical(dataset), encoding="utf8")
            result = subprocess.run(
                [sys.executable, "-I", str(executable), str(dataset_file)],
                input=canonical(request), capture_output=True, text=True,
                cwd=folder, timeout=5, check=False)
            if result.returncode or len(result.stdout) > 16000:
                raise ValueError("original generated Python rejected independent source/query")
            actual = json.loads(result.stdout)
            if independent:
                predicted = oracle(scope, predicates,
                                   known=request["known_at"], target=request["target_at"])
                if actual != predicted:
                    raise ValueError("original executable diverged from independently built source oracle")
            return actual

        for seed, size in SEEDS_AND_SIZES:
            scope = independent_scope(seed, size)
            if {r["id"] for r in scope["observations"]} & {r["id"] for r in original_observations}:
                raise ValueError("new independent fixtures reused parent observation IDs")
            name = f"seed-{seed}-count-{size}"
            dataset = dict(parent)
            dataset["case_id"] = scope["case_id"]
            dataset["observations"] = scope["observations"]
            (out / (name + "-source.json")).write_text(
                json.dumps(dataset, sort_keys=True, indent=2) + "\n", encoding="utf8")

            payload = {
                "kind": "native-synthetic-temporal-static-benchmark/v1",
                "synthetic": True, "queries": grid,
                "observations": scope["observations"],
                "prototype_sha256": sha256(code.encode()).hexdigest(),
                "query_history_sha256": query_history_sha256,
            }
            result = subprocess.run(
                [sys.executable, "-I", str(worker)], input=canonical(payload),
                capture_output=True, text=True, cwd=folder, timeout=15, check=False)
            if result.returncode or len(result.stdout) > 100000:
                raise ValueError("original pinned source benchmark worker rejected independent fixture: "
                                 + repr((result.returncode, result.stderr[:500])))
            report = json.loads(result.stdout)["report"]
            expected = []
            static_leakage_cases = 0
            static_occurrences = 0
            for q in grid:
                actual = execute(scope, q)
                expected.append({
                    "request": q, "temporal_ids": actual["temporal_ids"],
                    "static_snapshot_ids": actual["static_snapshot_ids"],
                    "future_leakage_ids": actual["future_leakage_ids"],
                })
                static_leakage_cases += bool(actual["future_leakage_ids"])
                static_occurrences += len(actual["future_leakage_ids"])
                logs.append(canonical({"dataset": name, "test": "original-replay",
                                       "query": q, "result": actual}))
            if (report["cases"] != expected or report["query_count"] != 25
                    or report["static_future_leakage_cases"] != static_leakage_cases
                    or report["static_future_leakage_ids_total"] != static_occurrences
                    or report["temporal_leakage_ids_total"] != 0
                    or report["synthetic_only"] is not True
                    or report["official_nih_submission"] is not False):
                raise ValueError("original source benchmark contradicted independent source oracle")

            # Invariant: observation permutation cannot change any query result.
            reversed_scope = deepcopy(scope)
            reversed_scope["observations"].reverse()
            for q, witness in zip(grid, expected):
                actual = execute(reversed_scope, q)
                oracle_result = oracle(scope, predicates,
                                       known=q["known_at"], target=q["target_at"])
                if (actual["temporal_ids"] != witness["temporal_ids"]
                        or actual["static_snapshot_ids"] != witness["static_snapshot_ids"]
                        or actual["future_leakage_ids"] != witness["future_leakage_ids"]
                        or actual != oracle_result):
                    raise ValueError("observation order changed semantic result")

            early = f"independent-early-{seed}"
            late = f"independent-late-{seed}"
            now = {"known_at": day(4), "target_at": day(4)}
            before = execute(scope, now)
            # At exact known_at, a delayed record becomes visible, not earlier.
            at_early = execute(scope, {"known_at": day(6), "target_at": day(4)})
            at_late = execute(scope, {"known_at": day(7), "target_at": day(4)})
            if late in at_early["temporal_ids"] or late not in at_late["temporal_ids"]:
                raise ValueError("known-at inclusive boundary failed")
            # Validity end is exclusive.
            at_end_minus = execute(scope, {"known_at": day(15), "target_at": day(10)})
            at_end = execute(scope, {"known_at": day(15), "target_at": day(11)})
            if early not in at_end_minus["temporal_ids"] or early in at_end["temporal_ids"]:
                raise ValueError("half-open valid-to boundary failed")

            # Knowledge accumulation is monotone when target time is fixed.
            seen = set()
            for cutoff in (0, 4, 6, 7, 9, 15):
                ids = set(execute(scope, {"known_at": day(cutoff), "target_at": day(4)})["temporal_ids"])
                if not seen <= ids:
                    raise ValueError("evidence vanished as known-time advanced")
                seen = ids

            # Source identity is retained; reassigning source_ref changes
            # visible provenance only, not whether an observation is visible.
            source_change = deepcopy(scope)
            for row in source_change["observations"]:
                if row["id"] == early:
                    row["source_ref"] = f"independent-reassignment-{seed}"
            shifted = execute(source_change, now)
            if shifted["temporal_ids"] != before["temporal_ids"] or (
                shifted["visible_source_refs"] == before["visible_source_refs"]
            ):
                raise ValueError("source-provenance sensitivity failed")

            checked = ("permutation", "knowledge-cutover", "validity-end",
                       "knowledge-monotonicity", "source-provenance")
            # Future-only information cannot affect temporal answer before known-at,
            # but must be visible as leakage in the static comparator.
            if size < 16:
                future = deepcopy(scope)
                future["observations"].append({
                    "id": f"future-only-{seed}", "subject": "fictional-new",
                    "predicate": "has-result", "object": "future-value",
                    "valid_from": day(2), "valid_to": day(11),
                    "known_at": day(19), "source_ref": f"future-origin-{seed}",
                })
                future = validate_scope(future)
                future_result = execute(future, now)
                if (future_result["temporal_ids"] != before["temporal_ids"]
                        or f"future-only-{seed}" not in future_result["future_leakage_ids"]
                        or f"future-only-{seed}" not in future_result["static_snapshot_ids"]):
                    raise ValueError("withheld future-only evidence altered past knowledge")
                checked += ("future-only-evidence",)
            else:
                full = deepcopy(scope)
                full["observations"].append(dict(full["observations"][0], id="overflow-synthetic"))
                try:
                    validate_scope(full)
                except ValueError:
                    pass
                else:
                    raise ValueError("maximum source record bound was bypassed")
                checked += ("scope-size-bound",)

            # Functional conflict appears once both contradictory values are
            # visible at target, not before the new record becomes known.
            conflict = deepcopy(scope)
            additional = {
                "id": f"independent-conflict-{seed}", "subject": "fictional-case",
                "predicate": "has-status", "object": "alternate-value",
                "valid_from": day(2), "valid_to": day(11),
                "known_at": day(7), "source_ref": f"independent-conflict-origin-{seed}",
            }
            if size < 16:
                conflict["observations"].append(additional)
            else:
                # For a full 16-row scope, replace one additional row, not anchor.
                conflict["observations"][-1] = additional
            conflict = validate_scope(conflict)
            not_yet = execute(conflict, {"known_at": day(6), "target_at": day(4)})
            visible = execute(conflict, {"known_at": day(7), "target_at": day(4)})
            pairing = sorted((early, f"independent-conflict-{seed}"))
            if pairing in not_yet["declared_conflicts"] or pairing not in visible["declared_conflicts"]:
                raise ValueError("functional predicate conflict reveal boundary failed")
            checked += ("functional-conflict",)

            # Malformed requests are rejected by the unchanged original CLI.
            invalid = subprocess.run(
                [sys.executable, "-I", str(executable), str(dataset_file)],
                input=canonical({"known_at": "2026-99-99", "target_at": day(4)}),
                capture_output=True, text=True, cwd=folder, timeout=5, check=False)
            if invalid.returncode == 0:
                raise ValueError("original Python accepted an invalid date")

            summaries.append({
                "name": name, "seed": seed, "observation_count": size,
                "dataset_sha256": sha256(canonical(dataset).encode()).hexdigest(),
                "query_count": len(grid), "static_future_leakage_cases": static_leakage_cases,
                "static_future_leakage_occurrences": static_occurrences,
                "source_worker_original_program_and_oracle_agreed": True,
                "metamorphic_properties_checked": list(checked),
            })
            logs.append(canonical({"dataset": name, "test": "metamorphic",
                                   "properties_passed": list(checked)}))

    record_file = out / "nih-p2-independent-metamo-cases.jsonl"
    record_file.write_text("\n".join(logs) + "\n", encoding="utf8")
    result = {
        "schema": SCHEMA, "synthetic_only": True, "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False, "general_biomedical_benchmark": False,
        "additional_native_checkpoint": False, "original_native_jobs": 12,
        "independent_source_fixture_count": len(summaries),
        "independent_query_replays": len(summaries) * len(grid),
        "original_program_sha256": sha256(code.encode()).hexdigest(),
        "benchmark_worker_sha256": sha256(src.read_bytes()).hexdigest(),
        "parent_edition_fingerprint": parent_fingerprint,
        "original_browser_history_sha256": query_history_sha256,
        "case_evidence_sha256": sha256(record_file.read_bytes()).hexdigest(),
        "source_cases": summaries,
    }
    (out / "nih-p2-independent-metamo-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return result


def join(*, data_dir, output_dir):
    data = Path(data_dir)
    parent = original_twelve(data_dir=data, output_dir=Path(output_dir))
    if parent["native_jobs"] != 12 or parent["NIH_P2_BENCHMARK"] != "WITNESSED":
        raise ValueError("exact native benchmark ancestry is required")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    bridge = NIHBenchmarkBridge(runtime=runtime, workstation=ProcessWorkstation(data / "workstation"))
    handoff = runtime.get(JOB_ID)
    source_folder = bridge._pinned(handoff)
    prototype = runtime.state(PROTOTYPE_JOB).output["prototype"]
    before = (data / "runtime.jsonl").read_bytes()
    result = run_experiment(
        code=prototype["python_source"], parent_dataset=prototype["dataset_json"],
        worker_source=source_folder / "benchmark_worker.py",
        original_observations=runtime.get(PROTOTYPE_JOB).inputs["scope"]["observations"],
        query_history_sha256=runtime.state(TEST_JOB).output["report"]["query_history_sha256"],
        parent_fingerprint=handoff.metadata["edition_fingerprint"],
        output_dir=output_dir,
    )
    if before != (data / "runtime.jsonl").read_bytes():
        raise ValueError("independent-source experiment altered original native journal")
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
