"""Follow-on synthetic source-variation experiment in the original NIH P2 workstation.

This is a separate experiment, NOT a thirteenth native handoff or a new NIH
checkpoint. Reuses the source-pinned benchmark worker and the ORIGINAL emitted
temporal_query.py, alters the observations rather than merely their query dates,
and verifies both against the independent observation-level oracle.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_benchmark_bridge import (
    JOB_ID, WORKER_ID, VERSION, NIHBenchmarkBridge, canonical,
)
from .nih_benchmark_temporal_join import join as original_twelve
from .nih_prototype_native import oracle
from .nih_scope_native import validate_scope
from .workstation import ProcessWorkstation

PROTOTYPE_JOB = "nih-prototype-001"
TEST_JOB = "nih-p2-game-test-001"
EXPERIMENT = "nih-p2-source-variation/v1"


def digest(obj):
    return sha256(canonical(obj).encode("utf8")).hexdigest()


def move(day, offset):
    return (date.fromisoformat(day) + timedelta(days=offset)).isoformat()


def variants(original, predicates):
    """Deterministic, recorded counterfactuals derived from actual source rows."""
    scope = validate_scope(original)
    rows = scope["observations"]
    early = min(rows, key=lambda r: (r["known_at"], r["id"]))
    late = max(rows, key=lambda r: (r["known_at"], r["id"]))
    if early["id"] == late["id"]:
        raise ValueError("source scope lacks distinct knowledge-time observations")

    result = {}
    for name in (
        "original", "later-knowledge", "earlier-knowledge",
        "later-valid-start", "shorter-valid-end", "longer-valid-end",
        "additional-delayed", "additional-conflict", "source-change"
    ):
        modified = deepcopy(scope)
        by_id = {o["id"]: o for o in modified["observations"]}
        first, last = by_id[early["id"]], by_id[late["id"]]
        if name == "later-knowledge":
            last["known_at"] = move(last["known_at"], 3)
        elif name == "earlier-knowledge":
            first["known_at"] = move(first["known_at"], -2)
        elif name == "later-valid-start":
            last["valid_from"] = move(last["valid_from"], 1)
            if last["valid_from"] > scope["target_at"]:
                raise ValueError("source validity cannot be narrowed around target")
        elif name == "shorter-valid-end":
            last["valid_to"] = move(scope["target_at"], 1)
            if last["valid_to"] >= late["valid_to"]:
                raise ValueError("source validity cannot be shortened")
        elif name == "longer-valid-end":
            first["valid_to"] = move(first["valid_to"], 3)
        elif name == "additional-delayed":
            extra = deepcopy(last)
            extra["id"] = "synthetic-extra-delayed"
            extra["source_ref"] = "synthetic-extra-source"
            extra["known_at"] = move(last["known_at"], 2)
            modified["observations"].append(extra)
        elif name == "additional-conflict":
            extra = deepcopy(first)
            extra["id"] = "synthetic-extra-conflict"
            extra["source_ref"] = "synthetic-conflict-source"
            extra["object"] = "synthetic-alternate-value"
            modified["observations"].append(extra)
        elif name == "source-change":
            first["source_ref"] = "synthetic-reassigned-source"
        checked = validate_scope(modified)
        result[name] = checked

    if len({digest(v["observations"]) for v in result.values()}) != len(result):
        raise ValueError("source variations were duplicates")
    if early["predicate"] in predicates and not any(
        r["predicate"] == early["predicate"] for r in result["additional-conflict"]["observations"]
    ):
        raise ValueError("functional conflict mutation failed")
    return result


def _axis(candidates, required, limit=9):
    result = set(required)
    if len(result) > limit:
        raise ValueError("too many required experiment boundaries")
    pool = sorted(candidates)
    if not pool:
        raise ValueError("empty temporal boundary grid")
    result.update((pool[0], pool[-1]))
    if len(result) > limit:
        raise ValueError("invalid pinned boundary grid")
    for i in range(25):
        if len(result) >= limit:
            break
        result.add(pool[round(i * (len(pool) - 1) / 24)])
    return sorted(result)


def grid(scopes):
    baseline = scopes["original"]
    known, valid = set(), set()
    must_known = {baseline["query_at"]}
    must_valid = {baseline["target_at"]}
    for name, scope in scopes.items():
        for row in scope["observations"]:
            for key in ("known_at",):
                known.update(move(row[key], i) for i in (-1, 0, 1))
            for key in ("valid_from", "valid_to"):
                valid.update(move(row[key], i) for i in (-1, 0, 1))
        if name in ("original", "later-knowledge", "earlier-knowledge", "additional-delayed"):
            must_known.add(max(r["known_at"] for r in scope["observations"]))
        if name in ("original", "shorter-valid-end", "later-valid-start"):
            must_valid.add(max(r["valid_from"] for r in scope["observations"]))
    known_axis = _axis(known, must_known)
    valid_axis = _axis(valid, must_valid)
    queries = [{"known_at": k, "target_at": v}
               for k in known_axis for v in valid_axis]
    if not 20 <= len(queries) <= 96:
        raise ValueError("source variations lack a bounded temporal grid")
    return queries


def run_experiment(*, scope, predicates, code, dataset_text, worker_source,
                   query_history_sha256, output_dir, edition_fingerprint,
                   sources=None, label="nih-p2-source-variation",
                   experiment_schema=EXPERIMENT):
    """Execute source worker, original Python, and independent oracle per variant."""
    scope = validate_scope(scope)
    original_data = json.loads(dataset_text)
    if (original_data.get("observations") != scope["observations"]
            or original_data.get("synthetic") is not True
            or original_data.get("functional_predicates") != predicates):
        raise ValueError("original prototype dataset is not exact native source")
    if any(x is None for x in (code, worker_source, edition_fingerprint)):
        raise ValueError("original source evidence missing")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if sources is None:
        sources = variants(scope, predicates)
    else:
        if type(sources) is not dict or "original" not in sources:
            raise ValueError("source families must include the original source")
        sources = {name: validate_scope(v) for name, v in sources.items()}
        if sources["original"] != scope or len({digest(v) for v in sources.values()}) != len(sources):
            raise ValueError("independent source families duplicate or replace the original")
    if not isinstance(label, str) or label not in ("nih-p2-source-variation", "nih-p2-source-families"):
        raise ValueError("unrecognized experimental evidence label")
    queries = grid(sources)
    cases_path = out / (label + "-cases.jsonl")
    lines = []
    summaries = []
    with TemporaryDirectory() as td:
        folder = Path(td)
        executable = folder / "temporal_query.py"
        executable.write_text(code, encoding="utf8")
        worker = folder / "benchmark_worker.py"
        worker.write_text(Path(worker_source).read_text(encoding="utf8"), encoding="utf8")
        dataset_file = folder / "temporal_dataset.json"
        for name, source_scope in sources.items():
            dataset = dict(original_data)
            dataset["observations"] = source_scope["observations"]
            dataset_file.write_text(canonical(dataset), encoding="utf8")
            (out / ("dataset-" + name + ".json")).write_text(
                json.dumps(dataset, sort_keys=True, indent=2) + "\n", encoding="utf8")
            request = {
                "kind": "native-synthetic-temporal-static-benchmark/v1",
                "synthetic": True,
                "queries": queries,
                "observations": source_scope["observations"],
                "prototype_sha256": sha256(code.encode()).hexdigest(),
                "query_history_sha256": query_history_sha256,
            }
            worker_run = subprocess.run(
                [sys.executable, "-I", str(worker)], input=canonical(request),
                capture_output=True, text=True, cwd=folder, timeout=15)
            if worker_run.returncode or len(worker_run.stdout) > 120000:
                raise ValueError("source-owned worker failed variation " + name)
            receipt = json.loads(worker_run.stdout)
            report = receipt.get("report")
            if not isinstance(report, dict) or report.get("query_count") != len(queries):
                raise ValueError("source worker case receipt invalid")
            expected_cases = []
            leaked = 0
            total = 0
            for q in queries:
                checked = oracle(source_scope, predicates,
                                 known=q["known_at"], target=q["target_at"])
                execution = subprocess.run(
                    [sys.executable, "-I", str(executable), str(dataset_file)],
                    input=canonical(q), capture_output=True, text=True,
                    cwd=folder, timeout=5)
                if execution.returncode or len(execution.stdout) > 16000:
                    raise ValueError("original program rejected source variant " + name)
                observed = json.loads(execution.stdout)
                if observed != checked:
                    raise ValueError("original program diverged from oracle: " + name)
                expected_cases.append({
                    "request": q,
                    "temporal_ids": checked["temporal_ids"],
                    "static_snapshot_ids": checked["static_snapshot_ids"],
                    "future_leakage_ids": checked["future_leakage_ids"],
                })
                leaked += bool(checked["future_leakage_ids"])
                total += len(checked["future_leakage_ids"])
                lines.append(canonical({"variant": name, "query": q,
                                        "result": observed}))
            if (report["cases"] != expected_cases
                    or report["static_future_leakage_cases"] != leaked
                    or report["static_future_leakage_ids_total"] != total
                    or report["temporal_leakage_ids_total"] != 0
                    or report["synthetic_only"] is not True
                    or report["official_nih_submission"] is not False
                    or report["prototype_sha256"] != sha256(code.encode()).hexdigest()
                    or report["query_history_sha256"] != query_history_sha256):
                raise ValueError("source worker disagreed with independent replay: " + name)
            summaries.append({
                "variant": name,
                "dataset_sha256": digest(dataset),
                "observation_count": len(source_scope["observations"]),
                "query_count": len(queries),
                "static_future_leakage_cases": leaked,
                "static_future_leakage_occurrences": total,
                "source_worker_matches_original_program_and_oracle": True,
            })
    cases_path.write_text("\n".join(lines) + "\n", encoding="utf8")
    summary = {
        "schema": experiment_schema,
        "parent_benchmark": "NIH-P2-BENCHMARK",
        "parent_edition_fingerprint": edition_fingerprint,
        "original_program_sha256": sha256(code.encode()).hexdigest(),
        "original_dataset_sha256": sha256(dataset_text.encode()).hexdigest(),
        "original_browser_history_sha256": query_history_sha256,
        "variation_count": len(sources),
        "queries_per_variation": len(queries),
        "total_independent_original_program_executions": len(sources) * len(queries),
        "case_evidence_sha256": sha256(cases_path.read_bytes()).hexdigest(),
        "variations": summaries,
        "source_owned_native_checkpoint": False,
        "official_NIH_submission": False,
        "synthetic_only": True,
        "clinical_verdict": "NOT_EVALUATED",
        "general_biomedical_benchmark": False,
    }
    (out / (label + "-summary.json")).write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return summary


def join(*, data_dir, output_dir):
    data, out = Path(data_dir), Path(output_dir)
    parent = original_twelve(data_dir=data, output_dir=out)
    if parent["NIH_P2_BENCHMARK"] != "WITNESSED" or parent["native_jobs"] != 12:
        raise ValueError("original twelve-job benchmark is not independently witnessed")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    desk = ProcessWorkstation(data / "workstation")
    bridge = NIHBenchmarkBridge(runtime=runtime, workstation=desk)
    handoff = runtime.get(JOB_ID)
    worker_folder = bridge._pinned(handoff)
    prototype = runtime.state(PROTOTYPE_JOB).output["prototype"]
    original_inputs = runtime.get(PROTOTYPE_JOB).inputs
    original_report = runtime.state(TEST_JOB).output["report"]
    before = (data / "runtime.jsonl").read_bytes()
    result = run_experiment(
        scope=original_inputs["scope"],
        predicates=original_inputs["reasoning_request"]["functional_predicates"],
        code=prototype["python_source"],
        dataset_text=prototype["dataset_json"],
        worker_source=worker_folder / "benchmark_worker.py",
        query_history_sha256=original_report["query_history_sha256"],
        edition_fingerprint=handoff.metadata["edition_fingerprint"],
        output_dir=out,
    )
    if before != (data / "runtime.jsonl").read_bytes():
        raise ValueError("source-variation exploration mutated original native journal")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args(argv)
    print(canonical(join(data_dir=a.data_dir, output_dir=a.output_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
