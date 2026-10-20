"""Finite A/B same-relation biomedical source-path witness.

Source relation direction is retained. A direct held-out biomedical assertion
is NOT inferred merely because a network path exists: these are link-
prediction PROXY scores, never clinical efficacy claims.

This adapter indexes original multi-relational source triples in memory and
performs explicitly bounded 2-3 hop source joins for a declared predicate,
preserving exact intermediate entities. No hidden test labels or dates.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256

SCHEMA="ab-heldout-biomedical-same-relation-path/v1"
MAX_SOURCE_ROWS=600000
MAX_DEGREE=20000
MAX_SCAN=100000


def edge_hash(head,rel,tail):
    return sha256((head+"\t"+rel+"\t"+tail).encode()).hexdigest()


def build(rows):
    if type(rows) is not list or len(rows)>MAX_SOURCE_ROWS:
        raise ValueError("finite original biomedical source triples required")
    by_relation=defaultdict(lambda:defaultdict(set))
    reverse=defaultdict(lambda:defaultdict(set))
    seen=set()
    for triple in rows:
        if (type(triple) is not tuple or len(triple)!=3 or
            any(type(v) is not str or not v or len(v)>256 or "\n" in v or "\t" in v
                for v in triple)):
            raise ValueError("malformed exact biomedical source triple")
        if triple in seen:
            raise ValueError("duplicate original biomedical source triple")
        seen.add(triple)
        a,p,b=triple
        by_relation[p][a].add(b)
        reverse[p][b].add(a)
    for p,subjects in by_relation.items():
        if any(len(neighbors)>MAX_DEGREE for neighbors in subjects.values()):
            raise ValueError("source relation expansion has unbounded degree")
    return {"forward":by_relation,"reverse":reverse,
            "original_source_edge_count":len(rows),
            "original_source_relation_counts":{
                p:sum(len(v) for v in by_relation[p].values()) for p in by_relation
            }}


def witness(index,*,head,relation,tail,max_hops=3):
    if type(max_hops) is not int or max_hops not in (2,3):
        raise ValueError("researcher-declared 2 or 3 hop source path required")
    if any(type(k) is not str or not k for k in (head,relation,tail)):
        raise ValueError("exact source query identity required")
    forward=index["forward"].get(relation,{})
    backward=index["reverse"].get(relation,{})
    first=forward.get(head,set())
    ending=backward.get(tail,set())
    if tail in first:
        # Direct source edge is not a novel inferred held-out path.
        return {
            "schema":SCHEMA, "path_exists":False, "source_path_nodes":[],
            "source_edge_sha256":[], "source_path_hops":None,
            "direct_training_edge_exists":True,"exhaustive_within_bound":True,
        }
    middle=sorted(first & ending-{head,tail})
    if middle:
        nodes=[head,middle[0],tail]
    elif max_hops==3:
        nodes=None
        scanned=0
        for b in sorted(first):
            if b in (head,tail):continue
            neighbors=forward.get(b,set())
            scanned+=len(neighbors)
            if scanned>MAX_SCAN:
                raise ValueError("bounded source join exceeded scan capacity")
            for c in sorted(neighbors & ending):
                if c not in (head,tail,b):
                    nodes=[head,b,c,tail]
                    break
            if nodes:break
    else:
        nodes=None
    if nodes is None:
        return {
            "schema":SCHEMA,"path_exists":False,"source_path_nodes":[],
            "source_edge_sha256":[],"source_path_hops":None,
            "direct_training_edge_exists":False,"exhaustive_within_bound":True,
        }
    return {
        "schema":SCHEMA,
        "path_exists":True,
        "source_path_nodes":nodes,
        "source_edge_sha256":[edge_hash(a,relation,b)
                              for a,b in zip(nodes,nodes[1:])],
        "source_path_hops":len(nodes)-1,
        "direct_training_edge_exists":False,
        "exhaustive_within_bound":True,
        "source_path_as_biomedical_truth":False,
    }
