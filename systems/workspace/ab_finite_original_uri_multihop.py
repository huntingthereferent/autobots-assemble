"""Finite A/B original-source URI relationship traversal (no invented world rules).

Search real subject/object graph edges for a SOURCE-WITNESSED simple path.
Available source relationships retain their original SHA-256 and provenance;
the known/valid dates are optional, expressly test-owned *overlays*, not an
original ontology publication timestamp. Search is breadth-first up to a
researcher-specified finite hop bound, with a strict expansion budget.
A false result proves no qualifying path only *within the declared bound*.
A budget breach errors: never pretend incomplete exploration is a negative.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import date
import re

SCHEMA="ab-finite-original-uri-multihop/v1"
SHA=re.compile(r"[0-9a-f]{64}\Z")
DATE=re.compile(r"\d{4}-\d{2}-\d{2}\Z")
MAX_EDGES=2500
MAX_HOPS=6
MAX_EXPANSIONS=30000


def canonical_day(d):
    if type(d) is not str or DATE.fullmatch(d) is None:
        raise ValueError("source time must be canonical calendar day")
    try:
        if date.fromisoformat(d).isoformat()!=d:
            raise ValueError("noncanonical source day")
    except ValueError as exc:
        raise ValueError("unavailable/invalid source calendar day") from exc
    return d


def validate(rows,*,start,end,predicate,known_at,target_at,max_hops):
    if type(rows) is not list or len(rows)>MAX_EDGES:
        raise ValueError("bounded external source relationship list required")
    for x in (start,end,predicate):
        if type(x) is not str or not x.startswith(("http://","https://")) or len(x)>512:
            raise ValueError("bounded full original-source URI required")
    if start==end:
        raise ValueError("reflexive paths not admitted without explicit source")
    if type(max_hops) is not int or not 1<=max_hops<=MAX_HOPS:
        raise ValueError("hop bound must be finite and 1..6")
    known=canonical_day(known_at)
    target=canonical_day(target_at)
    seen=set()
    for row in rows:
        if type(row) is not dict or set(row)!={
            "s","p","o","domain","known_at","valid_from","valid_to","source_relation_sha256"
        }:
            raise ValueError("exact original-source relation and test-clock shape required")
        if (not all(type(row[k]) is str and row[k].startswith(("http://","https://"))
                    for k in ("s","p","o")) or
                type(row["domain"]) is not str or
                row["domain"] not in ("relation-types","biological-classes") or
                type(row["source_relation_sha256"]) is not str or
                SHA.fullmatch(row["source_relation_sha256"]) is None):
            raise ValueError("original URI, source type or fingerprint invalid")
        for k in ("known_at","valid_from","valid_to"):
            canonical_day(row[k])
        if row["valid_from"]>=row["valid_to"]:
            raise ValueError("invalid temporal overlay interval")
        signature=(row["s"],row["p"],row["o"])
        if signature in seen:
            raise ValueError("duplicated observed original source edge")
        seen.add(signature)
    return known,target


def traverse(rows,*,start,end,predicate,known_at,target_at,max_hops=6):
    known,target=validate(rows,start=start,end=end,predicate=predicate,
                          known_at=known_at,target_at=target_at,max_hops=max_hops)
    adjacency=defaultdict(list)
    for row in rows:
        if (row["p"]==predicate and row["known_at"]<=known
                and row["valid_from"]<=target<row["valid_to"]):
            adjacency[row["s"]].append(row)
    for edges in adjacency.values():
        edges.sort(key=lambda r:(r["o"],r["source_relation_sha256"]))
    frontier=deque([(start,(start,),())])
    expansions=0
    while frontier:
        node,nodes,edges=frontier.popleft()
        if len(edges)>=max_hops:
            continue
        for edge in adjacency.get(node,()):
            expansions+=1
            if expansions>MAX_EXPANSIONS:
                raise ValueError("finite traversal capacity exceeded, no negative inferred")
            nxt=edge["o"]
            if nxt in nodes:
                continue
            path=edges+(edge,)
            path_nodes=nodes+(nxt,)
            if nxt==end:
                receipt=[{
                    "source_subject":r["s"],"source_predicate":r["p"],
                    "source_object":r["o"],
                    "source_relation_sha256":r["source_relation_sha256"],
                    "source_domain":r["domain"],
                    "hypothetical_known_at":r["known_at"],
                    "hypothetical_valid_from":r["valid_from"],
                    "hypothetical_valid_to":r["valid_to"],
                } for r in path]
                return {
                    "schema":SCHEMA,"start":start,"end":end,
                    "predicate":predicate,"known_at":known,"target_at":target,
                    "hop_bound":max_hops,"path_exists":True,
                    "source_witness_uris":list(path_nodes),
                    "source_witness_edges":receipt,
                    "path_hops":len(path),
                    "examined_source_edge_extensions":expansions,
                    "exhaustive_within_hop_bound":True,
                    "unbounded_reachability_proved":False,
                    "original_edge_publication_time_authenticated":False,
                    "clinical_causality_inferred":False,
                }
            frontier.append((nxt,path_nodes,path))
    return {
        "schema":SCHEMA,"start":start,"end":end,
        "predicate":predicate,"known_at":known,"target_at":target,
        "hop_bound":max_hops,"path_exists":False,
        "source_witness_uris":[],"source_witness_edges":[],
        "path_hops":None,
        "examined_source_edge_extensions":expansions,
        "exhaustive_within_hop_bound":True,
        "unbounded_reachability_proved":False,
        "original_edge_publication_time_authenticated":False,
        "clinical_causality_inferred":False,
    }
