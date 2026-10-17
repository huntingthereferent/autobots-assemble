"""Find common terminal referents ONLY from domain-verified directed traces.

Do not infer a center from correlations, proximity, rank or display geometry.
Unknown stays open; dual endpoints require a witnessed reason. This is an
abstract source-reading projection, not a collector or a claim about humans.
"""
from __future__ import annotations
from collections import defaultdict, deque
from typing import Callable


def evaluate(nodes: list[str], relations: list[dict], *,
             verify_relation: Callable[[dict], bool],
             split: dict | None = None,
             verify_split: Callable[[dict], bool] | None = None) -> dict:
    if not callable(verify_relation):
        raise ValueError("native relationship verifier is required")
    if type(nodes) is not list or not 2 <= len(nodes) <= 256:
        raise ValueError("bounded participant set required")
    if any(type(x) is not str or not x or len(x)>100 for x in nodes) or len(set(nodes))!=len(nodes):
        raise ValueError("invalid native identifiers")
    if type(relations) is not list or len(relations)>4096:
        raise ValueError("bounded native relation set required")
    if split is not None:
        if (type(split) is not dict or set(split)!={"endpoints","reason","witness"}
            or type(split["endpoints"]) is not list or len(split["endpoints"])!=2
            or any(type(x) is not str or not x for x in split["endpoints"])
            or len(set(split["endpoints"]))!=2
            or type(split["reason"]) is not str or not split["reason"].strip()
            or type(split["witness"]) is not str or not split["witness"].strip()):
            raise ValueError("malformed independently explained split")
    graph=defaultdict(set)
    reverse=defaultdict(set)
    seen=set()
    for edge in relations:
        if type(edge) is not dict or set(edge)!={"from","to","witness","kind"}:
            raise ValueError("invalid native edge")
        a,b=edge["from"],edge["to"]
        if (a not in nodes or b not in nodes or a==b or
            edge["kind"]!="continues_toward" or
            type(edge["witness"]) is not str or not edge["witness"] or
            (a,b) in seen):
            raise ValueError("invalid or duplicate directed relationship")
        if verify_relation(edge) is not True:
            raise ValueError("source-native witness rejected relationship")
        seen.add((a,b))
        graph[a].add(b)
        reverse[b].add(a)
    endpoints=sorted(n for n in nodes if not graph[n])
    reachable={}
    for end in endpoints:
        visited={end}
        queue=deque([end])
        while queue:
            current=queue.popleft()
            for prev in reverse[current]:
                if prev not in visited:
                    visited.add(prev)
                    queue.append(prev)
        reachable[end]=visited
    every=set(nodes)
    state="OPEN"
    focus=[]
    reason=None
    if relations and len(endpoints)==1 and reachable[endpoints[0]]==every and split is None:
        state="ONE_OBSERVED"
        focus=endpoints
    elif relations and len(endpoints)==2 and all(
        n in reachable[endpoints[0]] or n in reachable[endpoints[1]] for n in nodes):
        if (type(split) is dict and set(split)=={"endpoints","reason","witness"}
            and type(split["endpoints"]) is list
            and set(split["endpoints"])==set(endpoints)
            and len(split["endpoints"])==2
            and type(split["reason"]) is str and split["reason"].strip()
            and type(split["witness"]) is str and split["witness"].strip()
            and callable(verify_split) and verify_split(split) is True):
            state="TWO_WITNESSED"
            focus=endpoints
            reason=split["reason"]
    return {"status":state,"focus":focus,"candidate_endpoints":endpoints,
            "unresolved":sorted(every-set().union(*reachable.values())) if reachable else sorted(every),
            "witnessed_relations":len(seen),
            "split_reason":reason,
            "scope":"Only accepted, domain-native continues_toward relations; other data cannot be silently linked."}
