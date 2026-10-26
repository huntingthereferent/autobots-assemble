"""Compare Phase 1 world output receipts without confusing extensions with replacements.

Usage: python -m systems.workspace.nih_phase1_output_compare --receipts DIR --output report.json
Only real JSON receipts count; absent receipts stay UNKNOWN. No winner by recency.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

CANDIDATES = {
    "frontier": ("nih-phase1-original-world-frontier.json",
                 "nih-phase1-original-w13-world-frontier/v1",
                 ("original_native_jobs", 12),
                 ("browser_world_solved", True),
                 ("independent_scope_oracle_agreed", True),
                 ("future_evidence_withheld_then_revealed", True)),
    "two_clock": ("nih-phase1-two-clock-world-report.json",
                  "nih-phase1-original-w13-world-two-clock/v1",
                  ("original_native_jobs", 12),
                  ("original_game_solved", True),
                  ("both_clock_dimensions_observed", True),
                  ("independent_source_oracle_agreed", True),
                  ("preserved_original_native_ancestry", True)),
    "source_motion": ("nih-phase1-world-source-motion.json",
                      "nih-phase1-original-world-source-motion/v1",
                      ("native_jobs", 12),
                      ("actual_world_solved", True),
                      ("source_partition_verified", True),
                      ("source_conflict_found_in_counterfactual", True),
                      ("original_journals_preserved", True)),
    "publication_uncertainty": ("nih-phase1-world-publication-uncertainty.json",
                                "nih-phase1-original-world-publication-uncertainty/v1",
                                ("original_native_jobs", 12),
                                ("played_original_game_solved", True),
                                ("independent_three_state_policy_verified", True),
                                ("original_native_journals_preserved", True),
                                ("three_state_logic_is_not_in_original_python", True)),
}
CAPABILITIES = {
    "frontier": ["known-time-frontier"],
    "two_clock": ["known-time-frontier", "independent-valid-time"],
    "source_motion": ["known-time-frontier", "independent-valid-time", "source-variation", "explicit-conflict"],
    "publication_uncertainty": ["known-time-frontier", "independent-valid-time", "three-state-source-policy"],
}


def compare(receipts):
    results = {}
    for name, (filename, schema, *checks) in CANDIDATES.items():
        path = Path(receipts) / name / filename
        item = {"receipt": str(path), "capabilities": CAPABILITIES[name],
                "status": "UNKNOWN", "checks": {}, "source": None}
        exit_path = path.parent / "exit-code.txt"
        if exit_path.is_file():
            exit_code = exit_path.read_text(encoding="utf-8").strip()
            item["exit_code"] = exit_code
        else:
            exit_code = None
            item["exit_code"] = None
        if path.is_file():
            try:
                raw = path.read_bytes()
                item["receipt_sha256"] = sha256(raw).hexdigest()
                doc = json.loads(raw)
                item["checks"] = {"schema": doc.get("schema") == schema}
                item["checks"].update({key: doc.get(key) == value for key, value in checks})
                item["checks"]["process_exit_zero"] = exit_code == "0"
                item["status"] = "REPORTED_PASS" if all(item["checks"].values()) else "REPORTED_FAIL"
                item["source"] = "local-receipt-unverified"
            except (ValueError, OSError) as exc:
                item["status"] = "INVALID"
                item["error"] = str(exc)
        if not path.is_file() and exit_code is not None and exit_code != "0":
            item["status"] = "EXECUTION_FAILED"
        results[name] = item
    admitted = [name for name, item in results.items() if item["status"] == "REPORTED_PASS"]
    shared = sorted(set.intersection(*(set(CAPABILITIES[name]) for name in admitted))) if admitted else []
    maximal = [name for name in admitted if not any(
        set(CAPABILITIES[name]) < set(CAPABILITIES[other]) for other in admitted)]
    return {"schema": "nih-phase1-output-comparison/v1",
            "reported_pass_candidates": admitted,
            "shared_capabilities": shared,
            "capability_maximal_candidates_unverified": maximal,
            "comparison_kind": "capability-coverage-only; not measured head-to-head",
            "referent": "select strongest reproducible Phase 1 output on common tests",
            "candidates": results,
            "shared_baseline": "original 12-job W13/NIH source-owned native program",
            "selection": "UNDETERMINED",
            "reason": ("Distinct extensions are not interchangeable versions; a local receipt "
                       "alone does not prove its producing GitHub run or a common-input head-to-head replay."),
            "next": "Admit producing run IDs and immutable artifact hashes, then replay shared cases."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.receipts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["status"] for k, v in report["candidates"].items()}, indent=2))
    print("Selection:", report["selection"])


if __name__ == "__main__":
    main()
