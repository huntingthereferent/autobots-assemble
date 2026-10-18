"""Read repository-native provenance records without upgrading claims to proof.

Adapters:
* protocols/core/provenance-link.schema.json (cross-layer link records)
* protocols/core/trace.schema.json (traversal touch records)
* runtime/journal.py JSONL SUBMISSION/EVENT format (workstation handoffs)

This is a constrained projection of those existing contracts. Source references
remain references; SHA256 checks input integrity only, not authorship or truth.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

MAX_BYTES = 4_000_000
MAX_ITEMS = 2_000
MAX_TEXT = 2_048

class ProvenanceError(ValueError):
    """Invalid or contradictory structural provenance input."""

def _object_no_dupes(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ProvenanceError("duplicate JSON object key: " + k)
        obj[k] = v
    return obj

def _read(path: str | Path) -> tuple[str, bytes]:
    p = Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size > MAX_BYTES:
        raise ProvenanceError("source file absent, symlinked or over size limit")
    b = p.read_bytes()
    if len(b) > MAX_BYTES:
        raise ProvenanceError("source byte limit exceeded")
    try:
        return p.name, b
    except (UnicodeError, ValueError) as exc:
        raise ProvenanceError("source name invalid") from exc

def _parse(line: str, label: str):
    try:
        return json.loads(line, object_pairs_hook=_object_no_dupes,
                          parse_constant=lambda x: (_ for _ in ()).throw(
                              ProvenanceError("nonfinite JSON number in " + label)))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProvenanceError("invalid JSON in " + label) from exc

def _text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT:
        raise ProvenanceError(field + " must be a bounded nonempty string")
    return value

def _str_array(row, field: str) -> list[str]:
    arr = row.get(field, [])
    if not isinstance(arr, list) or len(arr) > MAX_ITEMS:
        raise ProvenanceError(field + " must be a bounded array")
    for x in arr:
        _text(x, field + " item")
    return arr

def _id(value, field: str) -> str:
    return _text(value, field)

def load_document(path: str | Path | None = None,
                  *, journal: str | Path | None = None) -> dict:
    """Return a scope-preserving graph from existing core records and journal."""
    if path is None and journal is None:
        raise ProvenanceError("provide a provenance document or workstation journal")
    if path is None:
        doc = {"schema_version": 1, "provenance_links": [], "traces": []}
        sources = []
    else:
        name, raw = _read(path)
        doc = _parse(raw.decode("utf-8"), name)
        sources = [{"name": name, "sha256": sha256(raw).hexdigest(),
                    "scope": "supplied local provenance document"}]
    if not isinstance(doc, dict) or type(doc.get("schema_version")) is not int or doc["schema_version"] != 1:
        raise ProvenanceError("expected provenance document schema_version 1")
    links, traces = doc.get("provenance_links", []), doc.get("traces", [])
    if (not isinstance(links, list) or not isinstance(traces, list) or
        len(links) + len(traces) > MAX_ITEMS):
        raise ProvenanceError("bounded provenance_links and traces arrays required")
    journal_rows = []
    if journal is not None:
        name, raw = _read(journal)
        journal_rows = [
            _parse(line, f"{name}:{i}") for i, line in
            enumerate(raw.decode("utf-8").splitlines(), 1) if line.strip()
        ]
        if len(journal_rows) > MAX_ITEMS:
            raise ProvenanceError("journal event count limit exceeded")
        sources.append({"name": name, "sha256": sha256(raw).hexdigest(),
                        "scope": "supplied local runtime journal"})
    return build_graph(links, traces, journal_rows, sources=sources)

def build_graph(links: list, traces: list, journal_rows: list,
                *, sources: list | None = None) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    warnings: list[str] = []
    seen_prov, seen_trace, seen_events, seen_handoffs = set(), set(), set(), set()
    pending_parents: list[tuple[str, str]] = []

    def node(identity, label, kind, source_ref=""):
        _id(identity, "node identifier")
        _text(label, "node label")
        if identity not in nodes:
            nodes[identity] = {"id": identity, "label": label, "kind": kind,
                               "source_ref": source_ref}
        elif nodes[identity]["label"] != label or nodes[identity]["kind"] != kind:
            raise ProvenanceError("conflicting node identity: " + identity)
        return identity

    def edge(identity, start, end, relation, *, scope, evidence=None, boundaries=None,
             invalidated=None, survived=None, details=None, state="reported"):
        edges.append({"id": _id(identity, "edge ID"), "from": start, "to": end,
                      "relation": _text(relation, "relation"), "scope": scope,
                      "evidence_refs": list(evidence or []),
                      "boundaries": list(boundaries or []),
                      "invalidated": list(invalidated or []), "survived": list(survived or []),
                      "details": dict(details or {}), "state": state})

    for raw in links:
        if not isinstance(raw, dict) or type(raw.get("schema_version")) is not int or raw["schema_version"] != 1:
            raise ProvenanceError("cross-layer link schema_version 1 required")
        ident = _id(raw.get("provenance_id"), "provenance_id")
        if ident in seen_prov:
            raise ProvenanceError("duplicate provenance_id: " + ident)
        seen_prov.add(ident)
        ends = []
        for side in ("from", "to"):
            record = raw.get(side)
            if not isinstance(record, dict) or set(record) - {"layer", "ref", "kind"}:
                raise ProvenanceError("invalid cross-layer endpoint " + side)
            layer = _text(record.get("layer"), "endpoint layer")
            ref = _text(record.get("ref"), "endpoint ref")
            key = "ref:" + json.dumps([layer, ref], ensure_ascii=False)
            ends.append(node(key, ref, "referent", layer + ":" + ref))
        evidence, invalidated = _str_array(raw, "evidence_refs"), _str_array(raw, "invalidated")
        boundaries = _str_array(raw, "boundaries")
        survived = _str_array(raw, "survived")
        state = "contested" if invalidated else ("referenced" if evidence else "unresolved")
        if not evidence:
            warnings.append("link " + ident + " contains no evidence references")
        if invalidated:
            warnings.append("link " + ident + " includes invalidated relations: " + ", ".join(invalidated))
        edge("prov:" + ident, *ends, _text(raw.get("relation"), "relation"),
             scope="provenance", evidence=evidence, boundaries=boundaries,
             invalidated=invalidated, survived=survived,
             details={"transformation": raw.get("transformation", ""),
                      "observed_at": raw.get("observed_at", "")}, state=state)

    for raw in traces:
        if not isinstance(raw, dict) or type(raw.get("schema_version")) is not int or raw["schema_version"] != 1:
            raise ProvenanceError("traversal trace schema_version 1 required")
        ident = _id(raw.get("trace_id"), "trace_id")
        if ident in seen_trace:
            raise ProvenanceError("duplicate trace_id: " + ident)
        seen_trace.add(ident)
        _text(raw.get("touched_at"), "touched_at")
        _text(raw.get("surface_kind"), "surface_kind")
        _text(raw.get("locator"), "locator")
        before = _text(raw.get("referent_before"), "referent_before")
        after = raw.get("referent_after")
        if after is not None:
            after = _text(after, "referent_after")
        start = node("referent:" + before, before, "referent")
        if after is None:
            target = node("unresolved:" + ident, "Unresolved continuation", "unresolved")
        else:
            target = node("referent:" + after, after, "referent")
        evidence = _str_array(raw, "evidence_refs")
        unresolved = _str_array(raw, "unresolved")
        if after is None or unresolved:
            warnings.append("trace " + ident + " has an unresolved continuation or boundary")
        edge("trace:" + ident, start, target, _text(raw.get("relation"), "relation"),
             scope="trace", evidence=evidence, boundaries=unresolved,
             details={"touched_at": raw["touched_at"], "surface_kind": raw["surface_kind"],
                      "locator": raw["locator"], "what_changed": raw.get("what_changed", "")},
             state="unresolved" if after is None or unresolved else "reported")

    for num, raw in enumerate(journal_rows, 1):
        if not isinstance(raw, dict) or raw.get("record_type") not in ("SUBMISSION", "EVENT"):
            raise ProvenanceError("invalid workstation journal record at row " + str(num))
        if raw["record_type"] == "SUBMISSION":
            h = raw.get("handoff")
            if not isinstance(h, dict):
                raise ProvenanceError("submission missing handoff")
            hid = _id(h.get("handoff_id"), "handoff_id")
            if hid in seen_handoffs:
                raise ProvenanceError("duplicate handoff ID: " + hid)
            seen_handoffs.add(hid)
            hnode = node("handoff:" + hid, _text(h.get("referent"), "handoff referent"),
                         "handoff", hid)
            event = raw.get("event")
        else:
            event = raw.get("event")
        if not isinstance(event, dict):
            raise ProvenanceError("workstation event missing")
        event_id = _id(event.get("event_id"), "event_id")
        hid = _id(event.get("handoff_id"), "event handoff_id")
        if event_id in seen_events:
            raise ProvenanceError("duplicate native event ID: " + event_id)
        seen_events.add(event_id)
        kind = _text(event.get("event_type"), "event type")
        if raw["record_type"] == "SUBMISSION" and kind != "CREATED":
            raise ProvenanceError("workstation SUBMISSION requires CREATED event")
        evnode = node("event:" + event_id, kind, "event", event_id)
        edge("event-of:" + event_id, "handoff:" + hid, evnode, "recorded_event",
             scope="workstation", state="reported")
        parents = event.get("parents", [])
        if not isinstance(parents, list):
            raise ProvenanceError("event parents must be an array")
        for parent in parents:
            pending_parents.append((_id(parent, "parent event ID"), event_id))
        evidence = event.get("evidence", [])
        if not isinstance(evidence, list):
            raise ProvenanceError("event evidence must be an array")
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                raise ProvenanceError("invalid native evidence carrier")
            evref = item.get("ref")
            if evref:
                er = _text(evref, "evidence ref")
                key = node("evidence:" + er, er, "evidence_reference", er)
                edge(f"event-evidence:{event_id}:{index}", evnode, key,
                     "cites_evidence_reference", scope="workstation",
                     evidence=[er], boundaries=[str(item.get("depth","reported"))],
                     state="referenced")
            else:
                warnings.append("event " + event_id + " reported evidence without a source reference")
    for h in sorted({e["from"][len("handoff:"):] for e in edges
                     if e["id"].startswith("event-of:") and e["from"].startswith("handoff:")}
                    - seen_handoffs):
        node("handoff:" + h, "Missing submission " + h, "unresolved")
        warnings.append("event references handoff absent from supplied journal: " + h)
    for parent, child in pending_parents:
        if parent not in seen_events:
            warnings.append("event " + child + " points to absent parent " + parent)
            node("unresolved-parent:" + parent, "Missing event " + parent, "unresolved")
            edge("parent-missing:" + parent + ":" + child, "unresolved-parent:" + parent,
                 "event:" + child, "unresolved_parent", scope="workstation",
                 state="unresolved")
        else:
            edge("parent:" + parent + ":" + child, "event:" + parent, "event:" + child,
                 "precedes", scope="workstation")
    if len(nodes) > MAX_ITEMS * 4 or len(edges) > MAX_ITEMS * 5:
        raise ProvenanceError("graph size limit exceeded")
    return {"schema_version": 1,
            "kind": "ab-provenance/graph-v1",
            "sources": sources or [],
            "nodes": sorted(nodes.values(), key=lambda n: n["id"]),
            "edges": sorted(edges, key=lambda e: e["id"]),
            "warnings": sorted(set(warnings)),
            "assertion_boundary": "Source references and labels are not independent verification. This is a projection of supplied local records."}

def graph_summary(graph: dict) -> dict:
    return {"sources": len(graph["sources"]), "nodes": len(graph["nodes"]),
            "relations": len(graph["edges"]),
            "unresolved": sum(e["state"]=="unresolved" for e in graph["edges"]),
            "contested": sum(e["state"]=="contested" for e in graph["edges"]),
            "warnings": len(graph["warnings"]),
            "independently_verified_by_this_tool": False}
