"""Check whether independent NIH P2 witness catches runnable semantic mutants.

Mutate *copies* of the ACTUAL emitted synthetic temporal Python executable,
not the original source-owner, and compare executions to a separately computed
observation-level oracle. A mutation only counts as detected if the altered
program executes successfully but returns a verifiably incorrect answer.
No additional native worker or biomedical/NIH conclusion is admitted.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_benchmark_bridge import JOB_ID, NIHBenchmarkBridge, canonical
from .nih_benchmark_temporal_join import join as original_twelve
from .nih_independent_metamo import day, independent_scope
from .nih_prototype_native import oracle
from .nih_scope_native import validate_scope
from .workstation import ProcessWorkstation

SCHEMA = "nih-p2-semantic-mutation-witness/v1"
PROTOTYPE_JOB = "nih-prototype-001"
TEST_JOB = "nih-p2-game-test-001"
# Mutation target strings belong to the original emitted Python, not this module.
# Each replacement is narrow and must occur exactly once.
MUTANTS = (
    ("known_cutoff_removed",
     'if o["known_at"] <= known', 'if True',
     4, 4, "temporal_ids"),
    ("known_equality_excluded",
     'if o["known_at"] <= known', 'if o["known_at"] < known',
     7, 4, "temporal_ids"),
    ("validity_end_included",
     'o["valid_from"] <= target < o["valid_to"]',
     'o["valid_from"] <= target <= o["valid_to"]',
     20, 11, "temporal_ids"),
    ("validity_start_removed",
     'o["valid_from"] <= target < o["valid_to"]',
     'target < o["valid_to"]',
     20, 0, "temporal_ids"),
    ("provenance_from_static",
     'set(o["source_ref"] for o in temporal)',
     'set(o["source_ref"] for o in eligible)',
     4, 4, "visible_source_refs"),
    ("conflict_detection_suppressed",
     'for pred in dataset["functional_predicates"]:',
     'for pred in []:',
     7, 4, "declared_conflicts"),
    ("outside_validity_suppressed",
     'outside = [o for o in dataset["observations"] if o not in eligible]',
     'outside = []',
     20, 11, "outside_validity_ids"),
    ("future_leakage_suppressed",
     'withheld = [o for o in eligible if o["known_at"] > known]',
     'withheld = []',
     4, 4, "future_leakage_ids"),
)


def challenge_scope():
    """Independent fixture with a declared, witnessed functional conflict."""
    scope = independent_scope(4, 7)
    proposed = deepcopy(scope)
    proposed["observations"].append({
        "id": "semantic-counterexample-conflict",
        "subject": "fictional-case", "predicate": "has-status",
        "object": "alternate-synthetic-value",
        "valid_from": day(2), "valid_to": day(11),
        "known_at": day(7), "source_ref": "semantic-counterexample-source",
    })
    scope = validate_scope(proposed)
    if len(scope["observations"]) != 8:
        raise ValueError("independent conflict counterexample missing")
    return scope


def mutate(code, before, after):
    if type(code) is not str or not code.strip():
        raise ValueError("original generated program is required")
    if code.count(before) != 1 or before == after:
        raise ValueError("semantic mutation cannot be unambiguously placed")
    altered = code.replace(before, after, 1)
    if altered == code or altered.count(after) != 1:
        raise ValueError("semantic mutant differs from assigned source")
    return altered


def run(*, code, original_dataset, original_observations,
        source_owner_sha256, browser_history_sha256, output_dir):
    dataset = json.loads(original_dataset)
    if (dataset.get("synthetic") is not True
            or dataset.get("observations") != original_observations
            or not isinstance(dataset.get("functional_predicates"), list)
            or not {"has-status", "has-result"}.issubset(set(dataset["functional_predicates"]))):
        raise ValueError("original signed synthetic prototype dataset absent")
    if not isinstance(source_owner_sha256, str) or not source_owner_sha256:
        raise ValueError("original source-pinned evidence required")
    if not isinstance(browser_history_sha256, str) or len(browser_history_sha256) != 64:
        raise ValueError("original Chromium timeline evidence required")

    scope = challenge_scope()
    counterfactual = dict(dataset)
    counterfactual["case_id"] = scope["case_id"]
    counterfactual["observations"] = scope["observations"]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic-counterexample-source.json").write_text(
        json.dumps(counterfactual, sort_keys=True, indent=2) + "\n", encoding="utf8")
    results = []
    with TemporaryDirectory() as td:
        folder = Path(td)
        script = folder / "temporal_query.py"
        data = folder / "temporal_dataset.json"
        data.write_text(canonical(counterfactual), encoding="utf8")

        def execute(program, query):
            script.write_text(program, encoding="utf8")
            p = subprocess.run(
                [sys.executable, "-I", str(script), str(data)],
                input=canonical(query), capture_output=True, text=True,
                cwd=folder, timeout=5, check=False)
            if p.returncode or len(p.stdout) > 16000 or len(p.stderr) > 2000:
                raise ValueError("semantic mutant did not execute normally")
            return json.loads(p.stdout)

        # Original executable must first agree with the independently declared
        # oracle on every witness input, before testing its mutant.
        for name, before, after, known, target, field in MUTANTS:
            q = {"known_at": day(known), "target_at": day(target)}
            expected = oracle(scope, dataset["functional_predicates"],
                              known=q["known_at"], target=q["target_at"])
            original = execute(code, q)
            if original != expected:
                raise ValueError("original emitted Python contradicts source oracle")
            altered_source = mutate(code, before, after)
            observed = execute(altered_source, q)
            if (set(observed) != set(original)
                    or observed["kind"] != original["kind"]
                    or observed[field] == expected[field]):
                raise ValueError("semantic mutant escaped its intended independent witness: " + name)
            results.append({
                "mutation": name, "query": q, "property": field,
                "baseline": original[field], "mutant": observed[field],
                "source_sha256": sha256(altered_source.encode()).hexdigest(),
                "synthetic_counterexample_detected": True,
                "mutated_program_executed_successfully": True,
            })

    (out / "nih-p2-semantic-mutant-cases.json").write_text(
        json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf8")
    result = {
        "schema": SCHEMA,
        "original_native_jobs": 12,
        "original_program_sha256": sha256(code.encode()).hexdigest(),
        "original_dataset_sha256": sha256(original_dataset.encode()).hexdigest(),
        "source_edition_fingerprint": source_owner_sha256,
        "original_browser_history_sha256": browser_history_sha256,
        "independent_synthetic_fixture_sha256": sha256(canonical(counterfactual).encode()).hexdigest(),
        "semantic_mutants_attempted": len(MUTANTS),
        "semantic_mutants_detected": len(results),
        "original_program_execution_checks": len(MUTANTS),
        "synthetic_only": True,
        "general_biomedical_benchmark": False,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
        "additional_native_checkpoint": False,
        "results": results,
    }
    (out / "nih-p2-semantic-mutant-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return result


def join(*, data_dir, output_dir):
    data = Path(data_dir)
    native = original_twelve(data_dir=data, output_dir=Path(output_dir))
    if native["native_jobs"] != 12 or native["NIH_P2_BENCHMARK"] != "WITNESSED":
        raise ValueError("original native twelve-job experimental source absent")
    runtime = HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))
    h = runtime.get(JOB_ID)
    bridge = NIHBenchmarkBridge(
        runtime=runtime, workstation=ProcessWorkstation(data / "workstation"))
    bridge._pinned(h)
    proto = runtime.state(PROTOTYPE_JOB).output["prototype"]
    before = (data / "runtime.jsonl").read_bytes()
    report = run(
        code=proto["python_source"],
        original_dataset=proto["dataset_json"],
        original_observations=runtime.get(PROTOTYPE_JOB).inputs["scope"]["observations"],
        source_owner_sha256=h.metadata["edition_fingerprint"],
        browser_history_sha256=runtime.state(TEST_JOB).output["report"]["query_history_sha256"],
        output_dir=output_dir)
    if before != (data / "runtime.jsonl").read_bytes():
        raise ValueError("original workstation journal changed in mutation experiment")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    x = p.parse_args(argv)
    print(canonical(join(data_dir=x.data_dir, output_dir=x.output_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
