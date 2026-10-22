"""Source-authenticated RO inverse-property *rule probes*, not clinical evidence.

Unlike schema closure alone, this checks operational inverse-property rules on
all exact original owl:inverseOf declarations. Input assertions are deliberately
synthetic, unique identifiers and never become source-owned biomedical edges.

Three independently executable observations:
  * direct original source-pair enumeration and SHA-256 receipts;
  * RDFLib SPARQL CONSTRUCT over the unmaterialized original source and probes;
  * OWLRL_Semantics expansion of the exact full original graph plus probes.
Equal-capability STATIC SPARQL is an oracle, not an A/B superiority result.
No original source file, citation, ontology or third-party object is changed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import json

from rdflib import Graph, URIRef, RDF, OWL
from . import nih_phase2_external_obo_graph_trial as source

SCHEMA = "nih-p2-original-ro-inverse-rule-source-fixture-v1"
PROBE_BASE = "https://example.org/nih-p2-owlrl-inverse-source-fixture/"
EXPECTED_SOURCE_PAIRS = 123
MAX_PROBE_COUNT = 300
MAX_MATERIALIZED_TRIPLES = 650000
QUERY = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT { ?tail ?inverse ?head }
WHERE {
  ?forward owl:inverseOf ?inverse .
  ?head ?forward ?tail .
  FILTER(STRSTARTS(STR(?head), "https://example.org/nih-p2-owlrl-inverse-source-fixture/head/"))
  FILTER(STRSTARTS(STR(?tail), "https://example.org/nih-p2-owlrl-inverse-source-fixture/tail/"))
}"""


def source_inverse_pairs(graph):
    if not isinstance(graph,Graph):
        raise TypeError("original source-owned RDF graph required")
    return sorted({
        (str(forward),str(inverse))
        for forward,inverse in graph.subject_objects(OWL.inverseOf)
        if isinstance(forward,URIRef) and isinstance(inverse,URIRef)
        and forward!=inverse
    })


def fixture_assertions(pairs):
    if not pairs or len(pairs)>MAX_PROBE_COUNT:
        raise ValueError("frozen source inverse-pair count out of bounds")
    injected=Graph()
    expected=set()
    receipts=[]
    for i,(forward,inverse) in enumerate(pairs):
        token=sha256((forward+"|"+inverse).encode()).hexdigest()[:20]
        head=URIRef(PROBE_BASE+"head/"+str(i)+"-"+token)
        tail=URIRef(PROBE_BASE+"tail/"+str(i)+"-"+token)
        direct=(head,URIRef(forward),tail)
        implied=(tail,URIRef(inverse),head)
        injected.add(direct)
        expected.add(implied)
        receipts.append({
            "source_inverse_declaration":[forward,str(OWL.inverseOf),inverse],
            "exact_source_declaration_sha256":sha256(
                (forward+"|"+str(OWL.inverseOf)+"|"+inverse).encode()).hexdigest(),
            "synthetic_probe_triple":list(map(str,direct)),
            "independent_expected_inverse_triple":list(map(str,implied)),
        })
    if len(injected)!=len(pairs) or len(expected)!=len(pairs):
        raise ValueError("source property probes have repeated identifiers")
    return injected,expected,receipts


def oracle_sparql_source_join(original,probes):
    # RDFLib's independent, declarative SPARQL query over an *unreasoned*
    # union of the original source axioms and visibly synthetic probe facts.
    g=Graph()
    g += original
    g += probes
    return set(g.query(QUERY).graph) if False else set(g.query(QUERY))


def examine(original,*,require_123=False):
    pairs=source_inverse_pairs(original)
    if require_123 and len(pairs)!=EXPECTED_SOURCE_PAIRS:
        raise ValueError("original source inverse declaration inventory changed")
    synthetic,expected,receipts=fixture_assertions(pairs)
    before=Graph()
    before += original
    before += synthetic
    if any(item in before for item in expected):
        raise ValueError("source or synthetic fixture already contained a predicted inverse")
    expected_by_join=oracle_sparql_source_join(original,synthetic)
    if expected_by_join!=expected:
        raise ValueError("independent SPARQL join disagrees with source declaration enumeration: "+
                         repr({"source_pairs":len(expected),"oracle":len(expected_by_join),
                               "missing":len(expected-expected_by_join),
                               "unexpected":len(expected_by_join-expected)}))
    from owlrl import DeductiveClosure, OWLRL_Semantics
    materialized=Graph()
    materialized += before
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(materialized)
    if len(materialized)>MAX_MATERIALIZED_TRIPLES:
        raise ValueError("finite OWL RL graph size exceeded limit")
    missed=sorted(expected-set(materialized),key=lambda t:tuple(map(str,t)))
    if missed:
        raise ValueError("source inverse rules failed on original-owner premises: "+
                         repr([list(map(str,t)) for t in missed[:6]]))
    unmatched_forward_source=[
        r for r in receipts
        if (URIRef(r["source_inverse_declaration"][0]),
            OWL.inverseOf,
            URIRef(r["source_inverse_declaration"][2])) not in original]
    if unmatched_forward_source:
        raise ValueError("source-owner inverse proof was not asserted")
    # No observations about biological relationships can come from a
    # deliberately made-up subject or object named under PROBE_BASE.
    # Count extra statements separately so they cannot be misreported as
    # original source evidence.
    materialized_probe_triples=sum(
        isinstance(s,URIRef) and str(s).startswith(PROBE_BASE) or
        isinstance(o,URIRef) and str(o).startswith(PROBE_BASE)
        for s,p,o in materialized)
    return {
        "schema":SCHEMA,
        "original_source_rdf_triples":len(original),
        "original_named_inverse_axioms":len(pairs),
        "unique_injected_synthetic_test_assertions":len(synthetic),
        "independent_SPARQL_CONSTRUCT_source_join_predictions":len(expected_by_join),
        "OWL_RL_correct_inverse_assertions":len(expected)-len(missed),
        "OWL_RL_missing_inverse_assertions":len(missed),
        "OWL_RL_equal_to_independent_static_source_oracle":len(missed)==0,
        "original_source_fixture_source_triple_count":len(before),
        "source_plus_fixture_materialized_triples":len(materialized),
        "materialized_triples_involving_synthetic_identifiers":materialized_probe_triples,
        "original_inverse_axioms_modified":False,
        "synthetic_probe_results_are_original_biomedical_data":False,
        "source_semantic_rule_inference_not_temporal_clinical":True,
        "equal_capability_static_oracle_is_not_A_B_advantage":True,
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
        "original_source_rule_receipts":receipts,
    }


def execute(files):
    original,receipt,edges=source.admit_sources(files)
    result=examine(original,require_123=True)
    if result["original_source_rdf_triples"]!=8319:
        raise ValueError("unexpected authenticated source graph size")
    result["original_source_owner"]=source.OWNER
    result["original_source_commit"]=source.COMMIT
    result["whole_source_sha256_receipts"]=receipt
    return result


def main():
    p=argparse.ArgumentParser()
    for k in ("ro-base","core","output"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    r=execute({"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "exact_source_inverse_axioms":r["original_named_inverse_axioms"],
        "synthetic_probes":r["unique_injected_synthetic_test_assertions"],
        "original_source_SPARRQL_oracle":r["independent_SPARQL_CONSTRUCT_source_join_predictions"],
        "owlrl_correct_operational_inferences":r["OWL_RL_correct_inverse_assertions"],
        "source_data_promoted_to_biomedical_claim":False,
        "NIH_complete":False
    },sort_keys=True))

if __name__=="__main__":
    main()
