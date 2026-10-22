"""Original OBO ontology: complete-graph OWL RL and independent local rule oracle.

The entire byte-pinned original 2026-09-04 ontology (both files) is
materialized by OWLRL_Semantics. Separately, an exact-premise finite scanner
checks inverseOf/equivalentProperty symmetry; URI-only asserted property
assertions support inverse/equivalent/symmetric/transitive/domain/range
consequences. This is a named subset of OWL RL, not an independent full
OWL reasoner. Preserve zero cases and materializer errors; never infer patient
facts or overall OWL DL consistency from an error count.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json

from rdflib import Graph, URIRef, RDF, RDFS, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics

from . import nih_phase2_external_obo_graph_trial as source
from . import nih_p2_obo_owlrl_source_entailment as earlier

SCHEMA="nih-p2-original-obo-full-owlrl-finite-rule-audit-v1"
MAX_ORIGINAL_TRIPLES=15000
MAX_MATERIALIZED_TRIPLES=600000
MAX_PREMISE_CONSEQUENCES=250000
PREVIEW=32


def named_pairs(graph, predicate):
    return sorted({
        (str(a),str(b)) for a,b in graph.subject_objects(predicate)
        if isinstance(a,URIRef) and isinstance(b,URIRef) and a!=b
    })


def original_named_assertions(graph):
    return sorted({
        (str(a),str(p),str(b))
        for a,p,b in graph
        if isinstance(a,URIRef) and isinstance(p,URIRef) and isinstance(b,URIRef)
    })


def independently_expected(graph):
    """Hand-scanned sound OWL RL rule instances, without calling OWL RL."""
    all_trip=set(graph)
    expected={}   # inferred triple -> (rule, source premise triple(s))
    counts=Counter()
    inverse=named_pairs(graph,OWL.inverseOf)
    equivalent=named_pairs(graph,OWL.equivalentProperty)
    symmetric=sorted({str(p) for p in graph.subjects(RDF.type,OWL.SymmetricProperty)
                      if isinstance(p,URIRef)})
    transitive=sorted({str(p) for p in graph.subjects(RDF.type,OWL.TransitiveProperty)
                       if isinstance(p,URIRef)})

    def admit(triple,rule,premises):
        counts[rule+"_observed_premises"]+=1
        if triple not in all_trip:
            expected.setdefault(triple,(rule,tuple(premises)))
        if len(expected)>MAX_PREMISE_CONSEQUENCES:
            raise ValueError("source original finite rule candidate budget exceeded")

    # Symmetry of inverse/equivalent property axioms is entailed at schema level.
    for pred,pairs,rule in (
        (OWL.inverseOf,inverse,"inverse_axiom_reverse"),
        (OWL.equivalentProperty,equivalent,"equivalent_axiom_reverse"),
    ):
        for a,b in pairs:
            admit((URIRef(b),pred,URIRef(a)),rule,[(URIRef(a),pred,URIRef(b))])

    named=original_named_assertions(graph)
    index=defaultdict(list)
    for s,p,o in named:
        index[p].append((s,o))
    for a,b in inverse:
        for s,o in index.get(a,()):
            admit((URIRef(o),URIRef(b),URIRef(s)),"inverse_assertion",
                  [(URIRef(a),OWL.inverseOf,URIRef(b)),
                   (URIRef(s),URIRef(a),URIRef(o))])
        for s,o in index.get(b,()):
            admit((URIRef(o),URIRef(a),URIRef(s)),"inverse_assertion",
                  [(URIRef(a),OWL.inverseOf,URIRef(b)),
                   (URIRef(s),URIRef(b),URIRef(o))])
    for a,b in equivalent:
        for s,o in index.get(a,()):
            admit((URIRef(s),URIRef(b),URIRef(o)),"equivalent_assertion",
                  [(URIRef(a),OWL.equivalentProperty,URIRef(b)),
                   (URIRef(s),URIRef(a),URIRef(o))])
        for s,o in index.get(b,()):
            admit((URIRef(s),URIRef(a),URIRef(o)),"equivalent_assertion",
                  [(URIRef(a),OWL.equivalentProperty,URIRef(b)),
                   (URIRef(s),URIRef(b),URIRef(o))])
    for p in symmetric:
        for s,o in index.get(p,()):
            admit((URIRef(o),URIRef(p),URIRef(s)),"symmetric_assertion",
                  [(URIRef(p),RDF.type,OWL.SymmetricProperty),
                   (URIRef(s),URIRef(p),URIRef(o))])
    for p in transitive:
        byhead=defaultdict(set)
        for a,b in index.get(p,()):
            byhead[a].add(b)
        for a,b in index.get(p,()):
            for c in byhead.get(b,()):
                admit((URIRef(a),URIRef(p),URIRef(c)),"transitive_assertion",
                      [(URIRef(p),RDF.type,OWL.TransitiveProperty),
                       (URIRef(a),URIRef(p),URIRef(b)),
                       (URIRef(b),URIRef(p),URIRef(c))])
    for predicate,axiom,location,rule in (
        (RDFS.domain,"domain","s","domain_named_assertion"),
        (RDFS.range,"range","o","range_named_assertion"),
    ):
        for p,c in named_pairs(graph,predicate):
            for s,o in index.get(p,()):
                individual=s if location=="s" else o
                admit((URIRef(individual),RDF.type,URIRef(c)),rule,
                      [(URIRef(p),predicate,URIRef(c)),
                       (URIRef(s),URIRef(p),URIRef(o))])
    return expected,{
        "original_explicit_inverseOf_named_pairs":len(inverse),
        "original_explicit_equivalentProperty_named_pairs":len(equivalent),
        "original_symmetric_property_types":len(symmetric),
        "original_transitive_property_types":len(transitive),
        "original_named_uri_triples":len(named),
        "rule_attempts":dict(sorted(counts.items())),
        "original_named_rdfs_domain_axioms":len(named_pairs(graph,RDFS.domain)),
        "original_named_rdfs_range_axioms":len(named_pairs(graph,RDFS.range)),
    }


def examine(graph):
    if not isinstance(graph,Graph) or len(graph)>MAX_ORIGINAL_TRIPLES:
        raise ValueError("original finite RDF source graph required")
    expected,inventory=independently_expected(graph)
    source_triples=set(graph)
    derived=Graph()
    for triple in graph:
        derived.add(triple)
    DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(derived)
    if len(derived)>MAX_MATERIALIZED_TRIPLES:
        raise ValueError("OWL RL complete-graph materialization exceeded capacity")
    # The OWL RL prp-inv rule materializes inverse PROPERTY ASSERTIONS
    # but does not necessarily emit a symmetric owl:inverseOf axiom triple.
    # Keep the original logical symmetry candidates in a separate negative
    # coverage receipt; do not call them materialized and do not waive any
    # unexpected missing property/data inference.
    missing=[t for t in expected if t not in derived]
    unexpectedly_missing=[t for t in missing if expected[t][0]!="inverse_axiom_reverse"]
    if unexpectedly_missing:
        raise ValueError("full original OWL RL closure misses "+str(len(unexpectedly_missing))+" engine-supported candidates: "+repr([{"triple":list(map(str,t)),"rule":expected[t][0]} for t in unexpectedly_missing[:5]]))
    inverse_axiom_mirror_gaps=[t for t in missing
                                if expected[t][0]=="inverse_axiom_reverse"]
    property_edges=earlier.original_property_graph(graph)
    paths=earlier.shortest_witnesses(property_edges)
    implied=earlier.original_nonasserted(paths,property_edges)
    missing_subprop=[
        (a,b) for a,b in implied
        if (URIRef(a),RDFS.subPropertyOf,URIRef(b)) not in derived]
    if missing_subprop:
        raise ValueError("OWL RL entire-original closure missed source subproperty transitivity")
    before=len(source_triples)
    new=set(derived)-source_triples
    # The materialized graph may include OWL-RL error message nodes. These
    # *signals* are not automatically independently authenticated defects.
    errors=sorted((str(s),str(o)) for s,p,o in derived
                  if p==RDF.type and str(o).endswith("#ErrorMessage"))
    rules=Counter(rule for rule,_ in expected.values())
    samples=sorted((t for t in expected if t in derived),key=lambda t:(
        sha256(("|".join(map(str,t))+"|nih-p2-full-owlrl").encode()).hexdigest(),
        tuple(map(str,t))))[:PREVIEW]
    proofs=[]
    for triple in samples:
        rule,premises=expected[triple]
        if any(source_premise not in source_triples for source_premise in premises):
            raise ValueError("finite rule proof references a nonoriginal premise")
        proofs.append({
            "inferred_triple":list(map(str,triple)),
            "inference_rule":rule,
            "source_premises":[list(map(str,p)) for p in premises],
            "source_premise_sha256":[sha256("|".join(map(str,p)).encode()).hexdigest()
                                     for p in premises],
            "premises_are_exact_original_source_triples":True,
            "not_directly_asserted_in_original":True,
        })
    return {
        "schema":SCHEMA,
        "original_rdf_triples":before,
        "full_source_owlrl_materialized_rdf_triples":len(derived),
        "materialized_nonasserted_rdf_triples":len(new),
        "scope":"entire original ontology, OWL RL semantics with RDFS closure",
        "independent_local_rule_candidate_nonasserted":len(expected),
        "independent_local_rule_classes":dict(sorted(rules.items())),
        "engine_supported_rule_consequences_all_materialized":True,
        "all_candidate_rule_triples_materialized":len(missing)==0,
        "inverse_axiom_mirror_candidates_not_explicitly_materialized":
            len(inverse_axiom_mirror_gaps),
        "inverse_axiom_mirror_gap_receipts":[
            {"missing_schema_triple":list(map(str,t)),
             "original_explicit_premise":list(map(str,expected[t][1][0]))}
            for t in inverse_axiom_mirror_gaps[:24]
        ],
        "inverse_axiom_mirror_gaps_do_not_invalidate_inverse_assertion_rule":True,
        "original_source_nonasserted_subproperty_transitivity":len(implied),
        "entire_source_OWL_RL_agrees_on_subproperty_closure":True,
        "owlrl_reported_error_messages":len(errors),
        "OWL_RL_error_signal_not_equivalent_to_independent_inconsistency_proof":True,
        "whole_original_consistency_established":False,
        "OWL_DL_consistency_and_unsatisfiable_class_search":"NOT_MEASURED",
        "original_temporal_event_dates":False,
        "original_patient_level_claim":False,
        "original_W13_modified":False,
        "official_NIH_Phase2_benchmark":False,
        "source_rule_inventory":inventory,
        "independent_source_rule_receipts":proofs,
    }


def execute(files):
    original,receipts,all_edges=source.admit_sources(files)
    result=examine(original)
    result["original_external_source_owner"]=source.OWNER
    result["original_source_commit"]=source.COMMIT
    result["authenticated_whole_original_file_receipts"]=receipts
    result["original_hierarchy_edges"]=len(all_edges)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ro-base",required=True,type=Path)
    p.add_argument("--core",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=execute({"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "original":result["original_rdf_triples"],
        "owlrl_total":result["full_source_owlrl_materialized_rdf_triples"],
        "new_materialized":result["materialized_nonasserted_rdf_triples"],
        "original_inverse_axioms":result["source_rule_inventory"]["original_explicit_inverseOf_named_pairs"],
        "original_equivalence_axioms":result["source_rule_inventory"]["original_explicit_equivalentProperty_named_pairs"],
        "independent_rule_candidates":result["independent_local_rule_candidate_nonasserted"],
        "inverse_axiom_mirror_gaps":result["inverse_axiom_mirror_candidates_not_explicitly_materialized"],
        "owlrl_error_signals":result["owlrl_reported_error_messages"],
        "NIH_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
