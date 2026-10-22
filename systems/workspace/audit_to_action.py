"""Source-grounded audit intake and action queue. Standard library only.

Usage: python systems/workspace/audit_to_action.py INPUT.json OUTPUT.json
Input is {"findings": [{"id", "lane", "observation", "source", "kind",
"proposed_action", "verification"}]}. No GitHub writes or worker dispatch.
"""
import json
import pathlib
import sys

KINDS = {"verified_result", "defect", "candidate", "unknown", "external_boundary"}
ACTIONS = {
    "verified_result": "preserve",
    "defect": "investigate",
    "candidate": "verify",
    "unknown": "observe",
    "external_boundary": "record_boundary",
}
REQUIRED = ("id", "lane", "observation", "source", "kind")


def process(document):
    if not isinstance(document, dict) or not isinstance(document.get("findings"), list):
        raise ValueError("expected object with findings array")
    seen = set()
    result = []
    for entry in document["findings"]:
        if not isinstance(entry, dict) or any(not isinstance(entry.get(k), str) or not entry[k].strip() for k in REQUIRED):
            raise ValueError("every finding requires nonempty id, lane, observation, source, kind")
        if entry["kind"] not in KINDS:
            raise ValueError("unrecognized finding kind: " + entry["kind"])
        if entry["id"] in seen:
            raise ValueError("duplicate finding id: " + entry["id"])
        seen.add(entry["id"])
        result.append({
            **entry,
            "action": ACTIONS[entry["kind"]],
            "state": "awaiting_verification" if entry["kind"] in ("defect", "candidate") else "recorded",
            "source_status": "unverified_locator",
            "verification": entry.get("verification", ""),
            "proposed_action": entry.get("proposed_action", ""),
        })
    return {"schema": "audit-to-action/v1", "findings": result, "summary": {
        "total": len(result),
        "by_action": {action: sum(x["action"] == action for x in result) for action in sorted(set(ACTIONS.values()))},
    }}


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: audit_to_action.py INPUT.json OUTPUT.json")
    output = process(json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8")))
    pathlib.Path(argv[2]).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv)
