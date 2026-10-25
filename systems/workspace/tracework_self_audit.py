"""Evaluate one explicitly selected finite audit; never select latest main as referent."""
import argparse
import json
import os
from pathlib import Path
from systems.workspace.bounded_audit import assess, load, next_handoffs
from systems.workspace.audit_source import github_run, verify_audit

DEFAULT = Path(__file__).with_name("audits") / "tracework-self-audit-2026-10-25.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT)
    parser.add_argument("--out", type=Path, default=Path("tracework-self-audit.json"))
    args = parser.parse_args()
    audit = load(args.audit)
    result = assess(audit)
    result["next_handoffs"] = next_handoffs(audit)
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if repo and token:
        comparisons = verify_audit(audit, lambda run_id: github_run(repo, token, run_id))
    else:
        comparisons = {n["id"]: {"matches": False, "error": "authenticated GitHub source unavailable"}
                       for n in audit["nodes"] if n["kind"] == "workflow"}
    result["source_comparisons"] = comparisons
    result["ready_to_close"] = result["ready_to_close"] and all(v["matches"] for v in comparisons.values())
    result["closed"] = result["closed"] and all(v["matches"] for v in comparisons.values())
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["closed"]:
        raise SystemExit("Audit remains open; unresolved descendants must close against its original referent.")


if __name__ == "__main__":
    main()
