"""Bounded RDF two-hop relationship composition from original source witnesses.

Build actual RDF asserted relations for a separately validated chronological
source path and infer a new RDF triple by an explicitly declared two-hop
property-composition rule. This is RDF graph inference, NOT full OWL 2 RL,
OWL propertyChainAxiom compliance, clinical entailment or logical-consistency
checking. Every added relation has a source witness; the graph is executable,
not merely displayed text.
"""
from __future__ import annotations

from hashlib import sha256
from rdflib import Graph, Namespace, RDF, Literal
from rdflib.namespace import XSD

from .ab_time_respecting_source_chain import observe as chains, token

SCHEMA="ab-bounded-two-hop-rdf-source-composition/v1"
EX=Namespace("https://example.org/ab-nih-phase2-source-inference/")
MAX_TRIPLES=1024


def infer(observations, stages, *, known_at, target_at, subject=None):
    if len(stages)!=3:
        raise ValueError("this bounded RDF two-hop experiment requires 3 declared stages")
    source=chains(observations,stages,known_at=known_at,target_at=target_at,
                  subject=subject)
    g=Graph()
    g.bind("ab",EX)
    path_receipts=[]
    for w in source["witnesses"]:
        a,b,c = [EX["event-"+token(x)] for x in w["evidence_ids"]]
        # Assertions exist because the preceding native source-chain witness
        # independently verified the exact chronology, subject and known-at.
        g.add((a,RDF.type,EX.SourceEvent))
        g.add((b,RDF.type,EX.SourceEvent))
        g.add((c,RDF.type,EX.SourceEvent))
        g.add((a,EX.observedThen,b))
        g.add((b,EX.observedThen,c))
        for node, day, ref in zip((a,b,c), w["event_starts"],w["source_references"]):
            g.add((node,EX.eventStart,Literal(day,datatype=XSD.date)))
            g.add((node,EX.originalSource,EX["source-"+token(ref)]))
        path_receipts.append({
            "premise_ids":w["evidence_ids"],
            "asserted_edge_a_b":[str(a),str(EX.observedThen),str(b)],
            "asserted_edge_b_c":[str(b),str(EX.observedThen),str(c)],
            "proposed_inference":[str(a),str(EX.observedBefore),str(c)],
            "source_references":w["source_references"],
        })
    if len(g)>MAX_TRIPLES:
        raise ValueError("RDF bounded graph exceeds source contract")
    base=set(g)
    additions=set()
    for a,_,b in g.triples((None,EX.observedThen,None)):
        for _,_,c in g.triples((b,EX.observedThen,None)):
            additions.add((a,EX.observedBefore,c))
    # Applying a declared RDF relation composition law is real graph work,
    # but is narrower than OWL reasoner compliance.
    for triple in additions:
        g.add(triple)
    if len(g)>MAX_TRIPLES:
        raise ValueError("inferred RDF graph exceeds source contract")
    added=sorted((tuple(map(str,t)) for t in additions-base))
    graph_bytes=g.serialize(format="nt", encoding="utf-8")
    return {
        "schema":SCHEMA,
        "declared_rule":"observedThen(x,y) AND observedThen(y,z) => observedBefore(x,z)",
        "asserted_source_path_count":len(source["witnesses"]),
        "actual_new_rdf_triples":added,
        "inference_exists":bool(added),
        "original_source_witnesses":path_receipts,
        "base_graph_triple_count":len(base),
        "entailed_graph_triple_count":len(g),
        "new_triple_count":len(added),
        "inferred_graph_nt_sha256":sha256(graph_bytes).hexdigest(),
        "rdf_graph_ntriples":graph_bytes.decode("utf-8"),
        "source_chain_schema":source["schema"],
        "original_W13_temporal_engine_modified":False,
        "actual_owl_property_chain_axiom_evaluated":False,
        "owl_unsatisfiable_classes_measured":False,
        "clinical_causality_entailment":False,
    }
