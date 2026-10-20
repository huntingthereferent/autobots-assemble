"""Separate receipt witness: rebuild graph/observations without generator.apply.

Verifies a finite record and its transitions, not external source authenticity,
physical dynamics, units, or the truth of reported measurements.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

SCHEMA = "ab-world-construction-plan/v1"
RECEIPT = "ab-world-construction-receipt/v1"
DEPTH = "declared-or-reported-not-physically-authenticated"
FIELDS = {
    "introduce": {"op", "id", "state", "basis"},
    "connect": {"op", "id", "from", "to", "label", "state", "basis"},
    "revise": {"op", "entity", "id", "after", "basis"},
    "disconnect": {"op", "id", "basis"},
    "retire": {"op", "id", "basis"},
    "observe": {"op", "id", "entity", "subject", "reading", "basis"},
    "compare": {"op", "id", "observation", "expected", "basis"},
}


def checksum(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("world witness: " + reason)


def exact(value: Any, keys: set[str], reason: str) -> None:
    require(type(value) is dict and set(value) == keys, reason + " fields")


def valid_id(ident: Any) -> bool:
    return type(ident) is str and bool(ident.strip())


def observe_step(world: dict[str, Any], step: dict[str, Any], bounds: dict) -> dict:
    require(type(step) is dict and step.get("op") in FIELDS, "unknown move")
    name = step["op"]
    exact(step, FIELDS[name], name)
    basis = step["basis"]
    exact(basis, {"kind", "source"}, "basis")
    require(basis["kind"] in ("declared", "source-execution", "external-report")
            and valid_id(basis["source"]), "unattributed movement")
    ident = step["id"]
    require(valid_id(ident), "invalid identity")
    objects, relations = world["objects"], world["relations"]
    if name == "introduce":
        require(type(step["state"]) is dict and ident not in world["used_objects"], "reintroduced object")
        require(len(world["used_objects"]) < bounds["objects"], "object bound")
        world["used_objects"].append(ident)
        objects[ident] = deepcopy(step["state"])
        return {"status": "introduced"}
    if name == "connect":
        require(ident not in world["used_relations"] and
                len(world["used_relations"]) < bounds["relations"], "relation bound/reuse")
        require(valid_id(step["from"]) and valid_id(step["to"]) and
                step["from"] in objects and step["to"] in objects, "missing endpoints")
        require(valid_id(step["label"]) and type(step["state"]) is dict, "relation declaration")
        relations[ident] = {"from": step["from"], "to": step["to"],
                            "label": step["label"], "state": deepcopy(step["state"])}
        world["used_relations"].append(ident)
        return {"status": "connected"}
    if name == "revise":
        category = step["entity"]
        require(category in ("object", "relation"), "invalid revision category")
        holder = objects if category == "object" else relations
        require(ident in holder and type(step["after"]) is dict, "missing revision target")
        previous = deepcopy(holder[ident] if category == "object" else holder[ident]["state"])
        if category == "object":
            holder[ident] = deepcopy(step["after"])
        else:
            holder[ident]["state"] = deepcopy(step["after"])
        return {"status": "revised", "before": previous, "after": deepcopy(step["after"])}
    if name == "disconnect":
        require(ident in relations, "missing relation")
        relations.pop(ident)
        return {"status": "disconnected"}
    if name == "retire":
        require(ident in objects, "missing object")
        require(not any(ident == link["from"] or ident == link["to"]
                        for link in relations.values()), "dangling relation")
        del objects[ident]
        world["retired_objects"].append(ident)
        return {"status": "retired"}
    if name == "observe":
        require(ident not in world["observations"], "observation reuse")
        category = step["entity"]
        require(category in ("object", "relation"), "invalid observed entity")
        holder = objects if category == "object" else relations
        require(valid_id(step["subject"]) and step["subject"] in holder, "missing observed subject")
        require(type(step["reading"]) is dict, "invalid reading")
        world["observations"][ident] = {
            "entity": category, "subject": step["subject"],
            "reading": deepcopy(step["reading"]), "basis": deepcopy(basis)
        }
        return {"status": "recorded-not-authenticated"}
    require(name == "compare", "unknown comparison")
    require(ident not in world["comparisons"], "comparison reused")
    require(valid_id(step["observation"]) and
            step["observation"] in world["observations"], "unobserved comparison")
    require(type(step["expected"]) is dict, "invalid expectation")
    measured = deepcopy(world["observations"][step["observation"]]["reading"])
    verdict = "MATCH" if measured == step["expected"] else "DIFFERENT"
    world["comparisons"][ident] = {
        "observation": step["observation"], "expected": deepcopy(step["expected"]),
        "observed": measured, "result": verdict
    }
    return {"status": verdict}


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Independently reconstruct the record. Hashes alone are not evidence origin."""
    exact(receipt, {"schema", "plan", "root_hash", "events", "final",
                    "head_hash", "evidence_depth"}, "receipt")
    require(receipt["schema"] == RECEIPT and receipt["evidence_depth"] == DEPTH,
            "unsupported version or claimed depth")
    plan = receipt["plan"]
    exact(plan, {"schema", "referent", "limits", "steps"}, "plan")
    require(plan["schema"] == SCHEMA and valid_id(plan["referent"]), "invalid referent")
    bounds = plan["limits"]
    exact(bounds, {"objects", "relations", "steps"}, "bounds")
    require(all(type(x) is int and 1 <= x <= 10000 for x in bounds.values()), "invalid bounds")
    require(type(plan["steps"]) is list and len(plan["steps"]) <= bounds["steps"], "steps bound")
    try:
        require(len(json.dumps(plan, ensure_ascii=False, allow_nan=False).encode("utf-8")) <= 1_000_000,
                "payload byte bound")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid finite JSON") from exc
    require(type(receipt["events"]) is list and
            len(receipt["events"]) == len(plan["steps"]), "event count")
    root = checksum({"schema": SCHEMA, "referent": plan["referent"], "limits": bounds})
    require(receipt["root_hash"] == root, "wrong ancestry root")
    world = {"objects": {}, "relations": {}, "observations": {},
             "comparisons": {}, "used_objects": [], "used_relations": [],
             "retired_objects": []}
    previous = root
    for n, (step, event) in enumerate(zip(plan["steps"], receipt["events"]), 1):
        exact(event, {"index", "operation", "effect", "before_state_hash",
                      "after_state_hash", "previous_hash", "hash"}, "event")
        require(type(event["index"]) is int and event["index"] == n, "ordinal")
        require(event["operation"] == step and event["previous_hash"] == previous, "ancestry")
        require(event["before_state_hash"] == checksum(world), "pre-state")
        effect = observe_step(world, step, bounds)
        require(event["effect"] == effect, "native event disagrees with witness")
        require(event["after_state_hash"] == checksum(world), "post-state")
        unsigned = {key: value for key, value in event.items() if key != "hash"}
        require(event["hash"] == checksum(unsigned), "event content hash")
        previous = event["hash"]
    require(receipt["head_hash"] == previous, "head ancestry")
    require(receipt["final"] == world, "final state differs from witnessed moves")
    return {
        "valid": True, "steps_verified": len(plan["steps"]),
        "head_hash": previous, "objects_live": len(world["objects"]),
        "relations_live": len(world["relations"]),
        "observations_recorded": len(world["observations"]),
        "comparisons": deepcopy(world["comparisons"]),
        "external_source_authenticated": False,
        "physical_behavior_verified": False,
    }
