"""Bounded backward ancestry query over independently supplied source relationships.

Traversal runs over the recorded edges. It does NOT infer missing provenance,
change an unresolved edge into a successful handoff, or authenticate a witness.
"""
from __future__ import annotations
from collections import defaultdict, deque
from .model import ProvenanceError, MAX_ITEMS

def ancestors(graph:dict, target:str, *, max_hops:int=32) -> dict:
    if type(max_hops) is not int or not 1 <= max_hops <= 128:
        raise ProvenanceError("ancestry hop limit must be an integer between 1 and 128")
    nodes={n["id"]:n for n in graph["nodes"]}
    if target in nodes:
        nodeid=target
    else:
        labels=[n["id"] for n in nodes.values() if n["label"]==target]
        if len(labels)!=1:
            raise ProvenanceError(
                "ancestry target not found or ambiguous; use exact ID from inspect --graph")
        nodeid=labels[0]
    upstream=defaultdict(list)
    for e in graph["edges"]:
        upstream[e["to"]].append(e)
    for records in upstream.values():
        records.sort(key=lambda e:e["id"])
    pending=deque([(nodeid,0)])
    visited={nodeid}
    selected={}
    clipped=[]
    while pending:
        here,depth=pending.popleft()
        if depth>=max_hops:
            if upstream.get(here):
                clipped.append(here)
            continue
        for e in upstream.get(here,[]):
            selected[e["id"]]=e
            parent=e["from"]
            if parent not in nodes:
                # A malformed or incomplete document is never repaired into proof.
                raise ProvenanceError("upstream relationship has no source node: "+parent)
            if parent not in visited:
                visited.add(parent)
                pending.append((parent,depth+1))
        if len(selected)>MAX_ITEMS*5:
            raise ProvenanceError("ancestry relation budget exceeded")
    edges=sorted(selected.values(),key=lambda e:e["id"])
    included=[nodes[k] for k in sorted(visited)]
    unresolved=[e["id"] for e in edges if e["state"]=="unresolved"]
    contested=[e["id"] for e in edges if e["state"]=="contested"]
    return {
        "schema_version":1, "kind":"ab-provenance/ancestry-v1",
        "target":nodeid,"maximum_hops":max_hops,
        "truncated":bool(clipped),"truncated_at":sorted(set(clipped)),
        "sources":graph["sources"],"nodes":included,"edges":edges,
        "unresolved_edges":unresolved,"contested_edges":contested,
        "warnings":sorted(set(
            ["Ancestry bounded at hop limit; upstream record may be missing."] if clipped else []
        )),
        "assertion_boundary":"Reachable records are source assertions, not independent witness acceptance."
    }
