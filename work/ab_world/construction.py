"""A/B world construction: bounded objects, movement and source-labeled observations.

This records what was declared or reported. It does not choose domain laws,
simulate physics, or authenticate an external instrument.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

PLAN = "ab-world-construction-plan/v1"
RECEIPT = "ab-world-construction-receipt/v1"
MAX_BYTES = 1_000_000
MAX_ITEMS = 10_000
DEPTH = "declared-or-reported-not-physically-authenticated"
OPS = {
    "introduce": {"op", "id", "state", "basis"},
    "connect": {"op", "id", "from", "to", "label", "state", "basis"},
    "revise": {"op", "entity", "id", "after", "basis"},
    "disconnect": {"op", "id", "basis"},
    "retire": {"op", "id", "basis"},
    "observe": {"op", "id", "entity", "subject", "reading", "basis"},
    "compare": {"op", "id", "observation", "expected", "basis"},
}
KINDS = {"declared", "source-execution", "external-report"}


def canonical(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError("world data must be finite JSON") from exc


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def check_keys(value: Any, keys: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != keys:
        raise ValueError(label + ": wrong or missing fields")


def nonempty(value: Any, label: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(label + ": nonempty string required")


def check_basis(basis: Any) -> None:
    check_keys(basis, {"kind", "source"}, "basis")
    if basis["kind"] not in KINDS:
        raise ValueError("unknown basis kind")
    nonempty(basis["source"], "basis.source")


def check_plan(plan: Any) -> None:
    check_keys(plan, {"schema", "referent", "limits", "steps"}, "plan")
    if plan["schema"] != PLAN:
        raise ValueError("unsupported world plan")
    nonempty(plan["referent"], "referent")
    check_keys(plan["limits"], {"objects", "relations", "steps"}, "limits")
    for name, count in plan["limits"].items():
        if type(count) is not int or not 1 <= count <= MAX_ITEMS:
            raise ValueError("invalid limit: " + name)
    if type(plan["steps"]) is not list or len(plan["steps"]) > plan["limits"]["steps"]:
        raise ValueError("step limit exceeded")
    if len(canonical(plan).encode("utf-8")) > MAX_BYTES:
        raise ValueError("plan byte limit exceeded")


def empty_state() -> dict[str, Any]:
    return {"objects": {}, "relations": {}, "observations": {},
            "comparisons": {}, "used_objects": [], "used_relations": [],
            "retired_objects": []}


def _entity(state: dict[str, Any], category: str, ident: str) -> dict:
    if category not in ("object", "relation"):
        raise ValueError("entity must be object or relation")
    collection = state["objects" if category == "object" else "relations"]
    if ident not in collection:
        raise ValueError("missing " + category + ": " + ident)
    return collection[ident]


def apply(state: dict[str, Any], step: dict[str, Any], limits: dict[str, int]) -> dict:
    if type(step) is not dict or step.get("op") not in OPS:
        raise ValueError("unsupported operation")
    op = step["op"]
    check_keys(step, OPS[op], op)
    check_basis(step["basis"])
    nonempty(step["id"], "operation id")
    ident = step["id"]
    if op == "introduce":
        if type(step["state"]) is not dict:
            raise ValueError("object state must be an object")
        if ident in state["used_objects"]:
            raise ValueError("object identity reused")
        if len(state["used_objects"]) >= limits["objects"]:
            raise ValueError("object bound reached")
        state["used_objects"].append(ident)
        state["objects"][ident] = deepcopy(step["state"])
        return {"status": "introduced"}
    if op == "connect":
        if ident in state["used_relations"]:
            raise ValueError("relation identity reused")
        if len(state["used_relations"]) >= limits["relations"]:
            raise ValueError("relation bound reached")
        for end in ("from", "to"):
            nonempty(step[end], end)
            _entity(state, "object", step[end])
        nonempty(step["label"], "relation label")
        if type(step["state"]) is not dict:
            raise ValueError("relation state must be an object")
        state["used_relations"].append(ident)
        state["relations"][ident] = {
            "from": step["from"], "to": step["to"], "label": step["label"],
            "state": deepcopy(step["state"])
        }
        return {"status": "connected"}
    if op == "revise":
        target = _entity(state, step["entity"], ident)
        if type(step["after"]) is not dict:
            raise ValueError("revised state must be an object")
        before = deepcopy(target if step["entity"] == "object" else target["state"])
        if step["entity"] == "object":
            state["objects"][ident] = deepcopy(step["after"])
        else:
            target["state"] = deepcopy(step["after"])
        return {"status": "revised", "before": before, "after": deepcopy(step["after"])}
    if op == "disconnect":
        _entity(state, "relation", ident)
        del state["relations"][ident]
        return {"status": "disconnected"}
    if op == "retire":
        _entity(state, "object", ident)
        if any(ident in (rel["from"], rel["to"]) for rel in state["relations"].values()):
            raise ValueError("cannot retire an object with live relations")
        del state["objects"][ident]
        state["retired_objects"].append(ident)
        return {"status": "retired"}
    if op == "observe":
        if ident in state["observations"]:
            raise ValueError("observation identity reused")
        nonempty(step["subject"], "subject")
        _entity(state, step["entity"], step["subject"])
        if type(step["reading"]) is not dict:
            raise ValueError("reading must be an object")
        state["observations"][ident] = {
            "entity": step["entity"], "subject": step["subject"],
            "reading": deepcopy(step["reading"]), "basis": deepcopy(step["basis"])
        }
        return {"status": "recorded-not-authenticated"}
    if op == "compare":
        if ident in state["comparisons"]:
            raise ValueError("comparison identity reused")
        nonempty(step["observation"], "observation")
        if step["observation"] not in state["observations"]:
            raise ValueError("missing observation")
        if type(step["expected"]) is not dict:
            raise ValueError("expected reading must be an object")
        observed = deepcopy(state["observations"][step["observation"]]["reading"])
        result = "MATCH" if step["expected"] == observed else "DIFFERENT"
        state["comparisons"][ident] = {
            "observation": step["observation"], "expected": deepcopy(step["expected"]),
            "observed": observed, "result": result
        }
        return {"status": result}
    raise ValueError("unreachable operation")


def run_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Execute a finite record of declared/reported moves, not physical dynamics."""
    check_plan(plan)
    plan = deepcopy(plan)
    state = empty_state()
    root = digest({"schema": PLAN, "referent": plan["referent"], "limits": plan["limits"]})
    previous = root
    events = []
    for index, step in enumerate(plan["steps"], 1):
        before = digest(state)
        outcome = apply(state, step, plan["limits"])
        event = {
            "index": index, "operation": step, "effect": outcome,
            "before_state_hash": before, "after_state_hash": digest(state),
            "previous_hash": previous
        }
        event["hash"] = digest(event)
        previous = event["hash"]
        events.append(event)
    return {
        "schema": RECEIPT, "plan": plan, "root_hash": root,
        "events": events, "final": state, "head_hash": previous,
        "evidence_depth": DEPTH
    }


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _bad_constant(value: str) -> None:
    raise ValueError("nonfinite JSON number: " + value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_strict_object, parse_constant=_bad_constant)


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B bounded construction record")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", type=Path, help="JSON operations to execute")
    group.add_argument("--verify", type=Path, help="receipt to verify independently")
    args = parser.parse_args()
    if args.plan:
        result = run_plan(load_json(args.plan))
    else:
        from work.ab_world.verify_construction import verify_receipt
        result = verify_receipt(load_json(args.verify))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
