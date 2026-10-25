"""Finite audit tree. An audit owns its referent and every descendant.

No global latest-main target, automatic reopening, or implicit workflow dispatch.
Evidence is tied to an explicitly admitted workflow run and commit.
"""
from __future__ import annotations
import json
from pathlib import Path

SCHEMA = "tracework/bounded-audit/v1"
STATES = {"open", "passed", "blocked"}
KINDS = {"check", "workflow", "repair", "audit"}


def validate(audit):
    if audit.get("schema") != SCHEMA or not audit.get("id") or not audit.get("referent"):
        raise ValueError("audit requires immutable id and referent")
    nodes = audit.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("audit requires bounded work")
    by_id = {}
    for n in nodes:
        key = n.get("id")
        if not isinstance(key, str) or not key or key in by_id:
            raise ValueError("duplicate or missing node id")
        if n.get("kind") not in KINDS or n.get("state") not in STATES:
            raise ValueError("invalid node kind or state")
        if not n.get("requirement"):
            raise ValueError("node needs an explicit acceptance requirement")
        by_id[key] = n
    root = audit["id"]
    for n in nodes:
        parent = n.get("parent")
        if parent != root and parent not in by_id:
            raise ValueError("orphaned audit work")
        if parent == n["id"]:
            raise ValueError("self parent")
        seen = {n["id"]}
        while parent != root:
            if parent in seen:
                raise ValueError("cycle in audit ancestry")
            seen.add(parent)
            parent = by_id[parent]["parent"]
    return by_id


def assess(audit):
    by_id = validate(audit)
    results = {}
    def visit(key):
        if key in results:
            return results[key]
        node = by_id[key]
        children = [x["id"] for x in audit["nodes"] if x.get("parent") == key]
        child_results = [visit(c) for c in children]
        children_pass = all(child_results)
        evidence = node.get("evidence") or {}
        valid = evidence.get("verified") is True and bool(evidence.get("source"))
        if node["kind"] == "workflow":
            valid = (valid and bool(evidence.get("run_id")) and
                     bool(evidence.get("head_sha")) and
                     evidence.get("conclusion") == "success")
        results[key] = node["state"] == "passed" and valid and children_pass
        return results[key]
    roots = [x["id"] for x in audit["nodes"] if x.get("parent") == audit["id"]]
    root_results = [visit(k) for k in roots]
    complete = bool(roots) and all(root_results)
    # Every node must be accounted for, not only the successful branches.
    complete = complete and len(results) == len(by_id)
    return {"audit_id": audit["id"], "referent": audit["referent"],
            "closed": audit.get("state") == "closed" and complete,
            "ready_to_close": complete, "nodes": results}


def add_child(audit, child):
    if audit.get("state") != "open":
        raise ValueError("closed audits are immutable; open a new audit")
    copy = json.loads(json.dumps(audit))
    copy["nodes"].append(child)
    validate(copy)
    return copy


def close(audit):
    if audit.get("state") != "open" or not assess(audit)["ready_to_close"]:
        raise ValueError("unresolved or already closed audit")
    copy = json.loads(json.dumps(audit))
    copy["state"] = "closed"
    return copy


def load(path):
    audit = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(audit)
    return audit
