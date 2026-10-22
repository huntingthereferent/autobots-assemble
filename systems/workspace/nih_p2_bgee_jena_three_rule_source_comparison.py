"""Whole original-source GenEx/RO/Bgee three-rule cross-engine verifier.

This is an independent-source, finite named-RDFS-plus-inverse-property proof.
It is NOT a full OWL RL/OWL DL general reasoner evaluation and does not
infer additional original measurements, clinical effectiveness or temporal
publication dates. Jena Java and Python RDFLib SPARQL are different engines.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from rdflib import Graph,URIRef,RDFS,OWL

from . import nih_p2_bgee_cross_engine_jena as first
from . import nih_p2_bgee_original_property_ancestry as ancestry
from . import nih_p2_bgee_exhaustive_sharded_owlrl as prior
from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

SCHEMA="nih-p2-original-bgee-jena-three-authenticated-rules-v1"
GENOMIC=URIRef("http://purl.obolibrary.org/obo/RO_0002330")
N_SOURCE=25027
N_TOTAL=75081
MAX_FILE_BYTES=50_000_000
CONSTRUCT="""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {
  ?gene <http://purl.obolibrary.org/obo/RO_0002206> ?place .
  ?gene <http://purl.obolibrary.org/obo/RO_0002330> ?place .
  ?place <http://purl.obolibrary.org/obo/RO_0002292> ?gene .
}
WHERE {
  <http://purl.org/genex#isExpressedIn>
       rdfs:subPropertyOf <http://purl.obolibrary.org/obo/RO_0002206> .
  <http://purl.obolibrary.org/obo/RO_0002206>
       rdfs:subPropertyOf <http://purl.obolibrary.org/obo/RO_0002330> .
  <http://purl.obolibrary.org/obo/RO_0002206>
       owl:inverseOf <http://purl.obolibrary.org/obo/RO_0002292> .
  ?gene <http://purl.org/genex#isExpressedIn> ?place .
  FILTER(isIRI(?gene) && isIRI(?place))
}"""


def original_three_source_axioms(original):
    g=original["full_combined"]
    a=(bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,bridge.RO_EXPRESSED)
    b=(bridge.RO_EXPRESSED,RDFS.subPropertyOf,GENOMIC)
    c=(bridge.RO_EXPRESSED,OWL.inverseOf,bridge.RO_EXPRESSES)
    required=(a,b,c)
    if any(t not in g for t in required):
        raise ValueError("all three original source-author owned predicate premises required")
    if len(original["source_edges"])!=N_SOURCE:
        raise ValueError("expected frozen genuine Bgee relationship inventory changed")
    return required


def full_static_source_rule_oracle(original):
    original_three_source_axioms(original)
    raw=original["source_edges"]
    manual=set()
    for s,p,o in raw:
        if p!=bridge.GENEX.isExpressedIn:
            raise ValueError("foreign predicate in source-mapped Bgee relationship")
        manual.update(((s,bridge.RO_EXPRESSED,o),
                       (s,GENOMIC,o),(o,bridge.RO_EXPRESSES,s)))
    source_sparql=set(original["full_combined"].query(CONSTRUCT).graph)
    if manual!=source_sparql:
        raise ValueError("independent source-only static SPARQL differs from finite handwritten three-rule oracle: "+
                         repr({"manual":len(manual),"sparql":len(source_sparql),
                               "missing":len(manual-source_sparql),
                               "extra":len(source_sparql-manual)}))
    if len(manual)!=N_TOTAL:
        raise ValueError("three-rule source original data set overlap/baseline changed")
    existing=original["independent"]
    extra=manual-existing
    if len(existing)!=50054 or len(extra)!=N_SOURCE or {p for s,p,o in extra}!={GENOMIC}:
        raise ValueError("genuine original hierarchical increment is not exclusively RO_0002330")
    return manual,extra


def verify_combined(original,output_file, *, expected=N_TOTAL):
    required=original_three_source_axioms(original)
    oracle,genomic=full_static_source_rule_oracle(original)
    output=Path(output_file)
    if not output.is_file() or output.stat().st_size>MAX_FILE_BYTES:
        raise ValueError("missing or oversized independent Jena RDF result")
    from .nih_p2_bgee_cross_engine_jena import inspect_jena_nt
    actual=inspect_jena_nt(output)
    only_static=oracle-actual
    only_jena=actual-oracle
    if only_static or only_jena:
        raise ValueError("third-party full-input Jena engine disagrees with independent original SPARQL: "+
                         json.dumps({"missing":len(only_static),"unexpected":len(only_jena),
                                     "missing_preview_sha256":sorted(sha256("|".join(map(str,t)).encode()).hexdigest()
                                                                   for t in only_static)[:3],
                                     "unexpected_preview_sha256":sorted(sha256("|".join(map(str,t)).encode()).hexdigest()
                                                                      for t in only_jena)[:3]},sort_keys=True))
    if len(actual)!=expected:
        raise ValueError("source original third-party Jena inference inventory changed")
    raw=original["source_edges"]
    return {
       "schema":SCHEMA,
       "source_owner_original_author_commit":bridge.COMMIT,
       "source_owner_original_RO_commit":bridge.source.COMMIT,
       "original_Bgee_author_zip_Git_blob":original["archive_receipt"]["complete_original_source_git_blob_sha1"],
       "original_source_positive_gene_expression_rows":original["source_positive_calls"],
       "original_original_source_edges":len(raw),
       "full_source_original_RO_GenEx_Bgee_graph_triples":len(original["full_combined"]),
       "original_exact_owner_axiom_premises":[list(map(str,a)) for a in required],
       "source_owner_original_three_axioms_proven":True,
       "Jena_Java_original_entire_input_three_rule_consequences":len(actual),
       "independent_static_RDFLib_SPARQL_complete_rule_consequences":len(oracle),
       "genuine_original_RO_0002330_additional_inherited_consequences":len(genomic),
       "original_expressed_in_forward_consequences":len(raw),
       "original_expresses_inverse_consequences":len(raw),
       "Jena_missing_consequences":0,
       "Jena_unexpected_consequences":0,
       "source_three_rule_actual_digest_sha256":prior.digest_set(actual),
       "independent_three_rule_static_digest_sha256":prior.digest_set(oracle),
       "original_new_hierarchy_only_digest_sha256":prior.digest_set(genomic),
       "third_party_engine": "Apache Jena GenericRuleReasoner three explicitly attested source rules",
       "full_OWL_RL_profile_executed":False,
       "independent_RDFS_and_inverse_subset_not_global_consistency":True,
       "source_observation_is_not_independent_biological_validation":True,
       "original_W13_modified":False,
       "official_NIH_benchmark":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("prepare","verify"),required=True)
    p.add_argument("--archive",required=True,type=Path)
    for n in ("obda","owl","r2rml","ro-base","core"):
        p.add_argument("--"+n,required=True,type=Path)
    p.add_argument("--input-nt",type=Path)
    p.add_argument("--jena-nt",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    authors={"bgee_v14_genex."+k:getattr(a,k) for k in ("obda","owl","r2rml")}
    original=first.verified_owner_input(a.archive,authors,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    if a.mode=="prepare":
        original_three_source_axioms(original)
        if a.input_nt is None:
            raise ValueError("original full input target required")
        print(json.dumps(first.write_input(original,a.input_nt),sort_keys=True))
    else:
        if a.jena_nt is None or a.output is None:
            raise ValueError("Jena RDF output and derived report path required")
        result=verify_combined(original,a.jena_nt)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+chr(10))
        print(json.dumps({"source_edges":result["original_original_source_edges"],
                          "jena_three_rules":result["Jena_Java_original_entire_input_three_rule_consequences"],
                          "static_three_rules":result["independent_static_RDFLib_SPARQL_complete_rule_consequences"],
                          "additional_genomic":result["genuine_original_RO_0002330_additional_inherited_consequences"],
                          "missing":result["Jena_missing_consequences"],
                          "unexpected":result["Jena_unexpected_consequences"],
                          "official_NIH":False},sort_keys=True))

if __name__=="__main__":
    main()
