"""Original RO subproperty transitivity: source-owned entailed, nonasserted axioms.

This measures sound OWL RL / RDFS schema-rule inferences, not merely SPARQL
reachability, and is not global OWL consistency. Independent finite path BFS
and RDFLib transitive_objects verify *all* eligible source relation endpoints.
A separately installed OWL RL reasoner must infer each frozen selected
nonasserted subproperty triple from ONLY its exact original source witness.
All materialized examples retain exact original edge receipts.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from hashlib import sha256
import json
from pathlib import Path

from rdflib import Graph, RDFS, URIRef
from . import nih_phase2_external_obo_graph_trial as original

SCHEMA = "nih-p2-original-obo-owlrl-subproperty-entailment-v1"
MAX_EDGES = 2500
MAX_TOTAL_REACHABLE = 120000
SAMPLE = 24


def original_property_graph(graph):
    """Source-asserted, forward-only named property hierarchy."""
    edges = {
        (str(a), str(b))
        for a, b in graph.subject_objects(RDFS.subPropertyOf)
        if isinstance(a, URIRef) and isinstance(b, URIRef) and a != b
    }
    if not 400 <= len(edges) <= MAX_EDGES:
        raise ValueError("original named relation hierarchy outside frozen bound")
    return edges


def shortest_witnesses(edges):
    """Cycle-safe independent BFS; returns paths, not inferred graph statements."""
    if type(edges) is not set:
        raise ValueError("source-owner exact asserted pairs required")
    adj=defaultdict(set)
    for a,b in edges:
        if not isinstance(a,str) or not isinstance(b,str) or not a or not b:
            raise ValueError("malformed original relation pair")
        adj[a].add(b)
    results={}
    for start in sorted(adj):
        paths={start:(start,)}
        frontier=deque([start])
        while frontier:
            current=frontier.popleft()
            for nxt in sorted(adj.get(current,())):
                if nxt in paths:
                    continue
                paths[nxt]=paths[current]+(nxt,)
                frontier.append(nxt)
        results[start]=paths
    return results


def original_nonasserted(witnesses,edges):
    derived = {
        (start,end): list(path)
        for start,paths in witnesses.items()
        for end,path in paths.items()
        if start != end and len(path)>=3 and (start,end) not in edges
    }
    if len(derived)>MAX_TOTAL_REACHABLE:
        raise ValueError("finite original source closure bound exceeded")
    return derived


def oracle_all_reachable(graph,edges,witnesses):
    """Independent RDFLib built-in triple traversal, no custom BFS reused."""
    oracle=Graph()
    for a,b in edges:
        oracle.add((URIRef(a),RDFS.subPropertyOf,URIRef(b)))
    for start,path_map in witnesses.items():
        actual={str(node) for node in
                oracle.transitive_objects(URIRef(start),RDFS.subPropertyOf)
                if isinstance(node,URIRef)}
        if actual!=set(path_map):
            raise ValueError("original RDFLib property source closure disagrees")
    return True


def materialized_by_owlrl(path):
    """Source-only minimal chain; independent OWL RL semantic engine."""
    from owlrl import DeductiveClosure, OWLRL_Semantics
    if len(path)<3 or len(set(path))!=len(path):
        raise ValueError("nontrivial cycle-free original source witness required")
    source_graph=Graph()
    for a,b in zip(path,path[1:]):
        source_graph.add((URIRef(a),RDFS.subPropertyOf,URIRef(b)))
    inferred=(URIRef(path[0]),RDFS.subPropertyOf,URIRef(path[-1]))
    if inferred in source_graph:
        raise ValueError("selected source triple was already direct")
    DeductiveClosure(OWLRL_Semantics).expand(source_graph)
    if inferred not in source_graph:
        raise ValueError("independent OWL RL engine did not entail transitive source hierarchy")
    return True


def execute(files):
    graph,source_receipts,all_hierarchy=original.admit_sources(files)
    edges=original_property_graph(graph)
    paths=shortest_witnesses(edges)
    derived=original_nonasserted(paths,edges)
    if not derived:
        raise ValueError("no original relation hierarchy entails new nonasserted triples")
    oracle_all_reachable(graph,edges,paths)
    # Source-independent ranking: deterministic frozen SHA-256 of original URI
    # pairs; no scoring/selection based on whether OWL RL proves selected fact.
    selected=sorted(derived, key=lambda t:(
        sha256((t[0]+"|"+t[1]+"|20261022-original-owlrl").encode()).hexdigest(),t))[:SAMPLE]
    if len(selected)<SAMPLE:
        raise ValueError("insufficient original nonasserted transitive relation pairs")
    sampled=[]
    for a,b in selected:
        witness=derived[(a,b)]
        if not materialized_by_owlrl(witness):
            raise ValueError("source axiom OWL RL reasoner witness missing")
        receipts=[sha256((left+"|"+str(RDFS.subPropertyOf)+"|"+right).encode()).hexdigest()
                  for left,right in zip(witness,witness[1:])]
        for left,right in zip(witness,witness[1:]):
            if (URIRef(left),RDFS.subPropertyOf,URIRef(right)) not in graph:
                raise ValueError("source edge receipt fabricated")
        sampled.append({
            "inferred_subject":a,"inferred_object":b,
            "inferred_predicate":str(RDFS.subPropertyOf),
            "not_explicitly_asserted_in_source":True,
            "source_edge_count":len(witness)-1,
            "original_witness_nodes":witness,
            "original_source_edge_sha256":receipts,
            "independent_owlrl_materialized_entailment":True,
        })
    return {
        "schema":SCHEMA,
        "external_owner":original.OWNER,
        "original_commit":original.COMMIT,
        "verified_whole_original_source_files":source_receipts,
        "original_source_rdf_triples":len(graph),
        "original_source_hierarchy_edges":len(all_hierarchy),
        "original_explicit_named_subproperty_pairs":len(edges),
        "nonasserted_subproperty_triples_entailed_by_transitivity":len(derived),
        "inference_profile":"transitive rdfs:subPropertyOf, OWLRL_Semantics independent materialization on source-minimal witness chains",
        "independent_full_source_RDFLib_property_closure_agreement":True,
        "selected_source_owned_nonasserted_entailments":len(sampled),
        "original_source_all_selected_OWL_RL_entailments_verified":True,
        "full_ontology_OWL_RL_closure_executed":False,
        "original_ontology_is_consistent":"NOT_MEASURED",
        "original_schema_inference_not_clinical_event_inference":True,
        "real_original_edge_publication_time_authenticated":False,
        "synthetic_example_used_for_source_entailment_count":False,
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
        "selected_receipts":sampled,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ro-base",required=True,type=Path)
    p.add_argument("--core",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    r=execute({"ro-base.owl":args.ro_base,"core.owl":args.core})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "original_explicit_subproperty":r["original_explicit_named_subproperty_pairs"],
        "nonasserted_entailed_subproperty":r["nonasserted_subproperty_triples_entailed_by_transitivity"],
        "source_owned_OWL_RL_checks":r["selected_source_owned_nonasserted_entailments"],
        "independent_full_static_oracle":r["independent_full_source_RDFLib_property_closure_agreement"],
        "NIH_complete":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
