"""Original-only RO inverse assertion census; no synthetic inputs enter evidence.

Checks whether the two SHA-256-pinned ontology files *actually assert*
subject/predicate/object facts using any source-owned owl:inverseOf predicates.
Separately checks that any finite, named original-source consequences agree
between a handwritten join, RDFLib SPARQL, and OWL RL entire-graph closure.
A zero original-instance result is evidence about this *ontology source*, not
a statement that the predicates lack real biomedical applications elsewhere.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from rdflib import Graph, OWL, URIRef, Literal, BNode
from . import nih_phase2_external_obo_graph_trial as source
from . import nih_p2_ro_inverse_rule_original_source_probe as previous

SCHEMA="nih-p2-ro-original-inverse-property-assertion-census-v1"
PINNED_INVERSE_DECLARATIONS=123
MAX_MATERIALIZED_TRIPLES=650000
MAX_DIRECT_MATCHES=10000
PREVIEW=24

SOURCE_QUERY = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT { ?object ?reverse ?subject }
WHERE {
  {
    ?predicate owl:inverseOf ?reverse .
    ?subject ?predicate ?object .
  }
  UNION
  {
    ?reverse owl:inverseOf ?predicate .
    ?subject ?predicate ?object .
  }
  FILTER(isIRI(?subject) && isIRI(?object))
}"""


def raw_source_matches(graph, pairs):
    """All assertions whose predicate is either side of an original inverse axiom."""
    property_ids={URIRef(p) for pair in pairs for p in pair}
    direct={
        (s,p,o)
        for p in property_ids for s,_,o in graph.triples((None,p,None))
    }
    if len(direct)>MAX_DIRECT_MATCHES:
        raise ValueError("source-owned original predicate facts over finite cap")
    return direct


def independent_inverse_join(graph,pairs):
    """Finite two-way join, never runs OWL RL or uses inferred triples."""
    result=set()
    witnesses={}
    for left,right in pairs:
        for forward,reverse in ((left,right),(right,left)):
            for s,_,o in graph.triples((None,URIRef(forward),None)):
                if not isinstance(s,URIRef) or not isinstance(o,URIRef):
                    continue
                new=(o,URIRef(reverse),s)
                asserted=(s,URIRef(forward),o)
                result.add(new)
                witnesses.setdefault(new,(
                    (URIRef(left),OWL.inverseOf,URIRef(right)),asserted))
    return result,witnesses


def examine(original, *, expected_original_count=None):
    if not isinstance(original,Graph):
        raise TypeError("an original RDF Graph is required")
    pairs=previous.source_inverse_pairs(original)
    if expected_original_count is not None and len(pairs)!=expected_original_count:
        raise ValueError("original inverse-pair source inventory changed")
    matches=raw_source_matches(original,pairs)
    kind=Counter()
    for s,p,o in matches:
        if isinstance(s,URIRef) and isinstance(o,URIRef):
            kind["named_original_subject_object"]+=1
        elif isinstance(o,Literal):
            kind["literal_object_not_valid_named_inverse_target"]+=1
        elif isinstance(s,BNode) or isinstance(o,BNode):
            kind["blank_node_not_named_ground_source_fact"]+=1
        else:
            kind["other_non_named_original_assertion"]+=1
    inferred,proofs=independent_inverse_join(original,pairs)
    static=set(original.query(SOURCE_QUERY).graph)
    if inferred!=static:
        raise ValueError("independent original-only RDFLib SPARQL join disagreed: "+
                         repr({"hand":len(inferred),"sparql":len(static),
                               "hand_only":len(inferred-static),
                               "sparql_only":len(static-inferred)}))
    for consequence,(inverse_axiom,assertion) in proofs.items():
        if inverse_axiom not in original or assertion not in original:
            raise ValueError("original-only source inverse witness was fabricated")
        if any(isinstance(node,URIRef) and str(node).startswith(previous.PROBE_BASE)
               for node in (consequence[0],consequence[2])):
            raise ValueError("synthetic data leaked into an original-only census")
    from owlrl import DeductiveClosure, OWLRL_Semantics
    full=Graph()
    full+=original
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(full)
    if len(full)>MAX_MATERIALIZED_TRIPLES:
        raise ValueError("source-only OWL RL closure outside predeclared size bound")
    misses=inferred-set(full)
    if misses:
        raise ValueError("whole-source OWL RL missed independently established original assertions: "+
                         repr([list(map(str,t)) for t in list(misses)[:5]]))
    new=inferred-set(original)
    receipts=[]
    for result in sorted(inferred,key=lambda t:tuple(map(str,t)))[:PREVIEW]:
        axi,assertion=proofs[result]
        receipts.append({
            "inverse_axiom":list(map(str,axi)),
            "original_assertion":list(map(str,assertion)),
            "implied_inverse_assertion":list(map(str,result)),
            "inverse_axiom_source_sha256":sha256("|".join(map(str,axi)).encode()).hexdigest(),
            "original_assertion_source_sha256":sha256("|".join(map(str,assertion)).encode()).hexdigest(),
            "not_originally_asserted":result not in original,
        })
    return {
        "schema":SCHEMA,
        "source_rdf_triples":len(original),
        "source_named_inverse_axiom_declarations":len(pairs),
        "original_source_predicate_assertions_using_either_inverse_side":len(matches),
        "original_source_named_subject_object_assertions":kind["named_original_subject_object"],
        "original_source_non_named_assertion_counts":{
            key:count for key,count in sorted(kind.items())
            if key!="named_original_subject_object"},
        "independent_original_source_inverse_predictions":len(inferred),
        "independent_original_only_SPARQL_CONSTRUCT_predictions":len(static),
        "new_nonasserted_inverse_relationships_from_original_sources":len(new),
        "whole_original_OWL_RL_agrees_on_source_inverse_predictions":True,
        "original_source_inverse_comparison_has_positive_cases":bool(inferred),
        "source_only_inverse_inference_agreement_is_vacuous":not bool(inferred),
        "whole_original_OWL_RL_total_triples":len(full),
        "inverse_predictions_only_tested_on_original_assertions":True,
        "audit_injected_no_additional_assertions":True,
        "original_input_authenticated_by_whole_file_SHA256":False,
        "absence_of_ground_instance_assertions_is_not_an_absence_of_applications":True,
        "static_oracle_also_has_full_source_axioms":True,
        "medical_treatment_efficacy_inferred":False,
        "original_patient_level_records_used":False,
        "source_ownership_or_clinical_valid_at_authenticated":False,
        "official_NIH_benchmark":False,
        "original_W13_modified":False,
        "source_original_witnesses":receipts,
        "source_receipts_truncated":len(inferred)>PREVIEW,
    }


def execute(files):
    original,source_receipts,hierarchy=source.admit_sources(files)
    x=examine(original,expected_original_count=PINNED_INVERSE_DECLARATIONS)
    if x["source_rdf_triples"]!=8319:
        raise ValueError("original source graph triple count changed")
    x["original_external_owner"]=source.OWNER
    x["original_source_commit"]=source.COMMIT
    x["whole_source_SHA256"]=source_receipts
    x["original_input_authenticated_by_whole_file_SHA256"]=True
    return x


def main():
    parser=argparse.ArgumentParser()
    for name in ("ro-base","core","output"):
        parser.add_argument("--"+name,required=True,type=Path)
    a=parser.parse_args()
    result=execute({"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "source_inverse_axioms":result["source_named_inverse_axiom_declarations"],
        "source_direct_predicate_assertions":result["original_source_predicate_assertions_using_either_inverse_side"],
        "source_named_assertions":result["original_source_named_subject_object_assertions"],
        "original_source_inverse_predictions":result["independent_original_source_inverse_predictions"],
        "new_nonasserted_original_inverse_facts":result["new_nonasserted_inverse_relationships_from_original_sources"],
        "source_only_OWL_RL_agreement":result["whole_original_OWL_RL_agrees_on_source_inverse_predictions"],
        "NIH_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
