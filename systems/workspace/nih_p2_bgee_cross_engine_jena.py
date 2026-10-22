"""Apache Jena alternative rule engine vs owner-authenticated whole Bgee+RO graph.

Runs *all* original source triples through an alternative Java RDF inference
engine, rather than repeatedly sampling OWL RL. Jena checks only the two
author-owned entailment rules and NOT the complete OWL RL ontology profile.

prepare: verify six original source files, construct the entire original
          source RO+GenEx+Bgee graph, export ephemeral N-Triples for Java.
verify:  parse Java engine inferred N-Triples; independently reconstruct all
         original source edges via direct joins AND SQLite; compare exact
         forward/inverse triple sets to a separate RDFLib SPARQL oracle.
No full original data graph is uploaded; only a digest/count evidence report.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from rdflib import Graph,URIRef,OWL,RDFS
from . import nih_p2_original_bgee_real_expression_join as bgee
from . import nih_p2_bgee_exhaustive_sharded_owlrl as baseline
from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

SCHEMA="nih-p2-cross-engine-jena-original-bgee-full-input-v1"
ORIGINAL_EDGES=25027
RULE_CONSEQUENCES=50054
MAX_JENA_OUTPUT_LINES=150000
MAX_DATA_GRAPH_TRIPLES=90000
EVIDENCE_PREVIEW=20


def verified_owner_input(archive,authors,ro_files):
    authenticated=bridge.examine(authors,ro_files)
    rows,archive_receipt=bgee.source_tables(archive)
    direct,events=bgee.keyed_join(rows)
    sql,sql_rows=bgee.independent_sqlite_join(rows)
    if direct!=sql:
        raise ValueError("original owner source gene-expression join differs from independent SQL")
    edges=baseline.original_join_graph(direct)
    ontology=Graph().parse(data=Path(authors["bgee_v14_genex.owl"]).read_bytes(),format="turtle")
    ro,ro_hashes,_=bridge.source.admit_sources(ro_files)
    sub,inverse=baseline.source_axioms(ontology,ro)
    explicit=baseline.direct_entailed(edges)
    independent=baseline.static_sparql_oracle(edges,sub,inverse)
    if explicit!=independent:
        raise ValueError("whole original RDFLib SPARQL original-only rule comparator disagrees")
    if not edges or len(edges)>MAX_DATA_GRAPH_TRIPLES or len(explicit)!=2*len(edges):
        raise ValueError("original data source outside declared size and uniqueness bounds")
    all_input=Graph()
    all_input += ontology
    all_input += ro
    for t in edges:
        all_input.add(t)
    if len(all_input)>MAX_DATA_GRAPH_TRIPLES:
        raise ValueError("original full combined RDF input graph exceeds bound")
    return {
        "author":authenticated,
        "original_ro_receipts":ro_hashes,
        "archive_receipt":archive_receipt,
        "source_positive_calls":events.get("source_positive_expression_rows",0),
        "source_joined_calls":events.get("joined_positive_rows",0),
        "missing_genes":events.get("unmatched_gene",0),
        "missing_conditions":events.get("unmatched_condition",0),
        "source_anatomy_edges":len(direct["anatomy"]),
        "source_condition_edges":len(direct["expression_condition"]),
        "source_sql_join_distinct_records":sql_rows,
        "source_edges":edges,
        "independent":independent,
        "full_combined":all_input,
        "r2rml_two_owner_mappings":len(authenticated["author_R2RML_mappings"]),
    }


def write_input(original,output):
    output.parent.mkdir(parents=True,exist_ok=True)
    original["full_combined"].serialize(destination=str(output),format="nt")
    return {
        "full_source_input_rdf_triples":len(original["full_combined"]),
        "whole_original_input_ntriples_sha256":sha256(output.read_bytes()).hexdigest(),
        "whole_input_contains_original_RO":True,
        "whole_input_contains_original_GenEx":True,
        "whole_input_contains_all_25027_Bgee_edges":len(original["source_edges"])==ORIGINAL_EDGES,
    }


def independent_rule_set_comparison(observed,oracle):
    lost=oracle-observed
    extras=observed-oracle
    if lost or extras:
        raise ValueError("independent Jena RDF rules and original source static comparator disagree: "
                        +json.dumps({
                            "missing":len(lost),"unexpected":len(extras),
                            "missing_preview":[list(map(str,t)) for t in sorted(lost,key=baseline.source_sort_key)[:3]],
                            "unexpected_preview":[list(map(str,t)) for t in sorted(extras,key=baseline.source_sort_key)[:3]],
                        },sort_keys=True))
    return baseline.digest_set(observed)


def verify(original,jena_nt):
    """Strict exact equality with the full independent source-only oracle."""
    if not Path(jena_nt).exists() or Path(jena_nt).stat().st_size>MAX_JENA_OUTPUT_LINES*350:
        raise ValueError("missing or unreasonable Jena alternative reasoner output size")
    if Path(jena_nt).read_bytes().count(b"\n")>MAX_JENA_OUTPUT_LINES:
        raise ValueError("Jena output exceeds finite independent comparison cap")
    jena=Graph()
    jena.parse(str(jena_nt),format="nt")
    observed=set(jena)
    oracle=original["independent"]
    # Keep *unexpected* conclusions as counterexamples rather than
    # silently filtering or treating them as model superiority.
    jena_digest=independent_rule_set_comparison(observed,oracle)
    edges=original["source_edges"]
    if len(edges)!=ORIGINAL_EDGES or len(observed)!=RULE_CONSEQUENCES:
        raise ValueError("original source baseline unexpected count")
    hashes=sorted(sha256("|".join(map(str,t)).encode()).hexdigest()
                  for t in observed)[:EVIDENCE_PREVIEW]
    return {
        "schema":SCHEMA,
        "original_external_author_commit":bridge.COMMIT,
        "original_relation_ontology_commit":bridge.source.COMMIT,
        "original_author_data_Git_blob":original["archive_receipt"]["complete_original_source_git_blob_sha1"],
        "original_owner_mapping_count":original["r2rml_two_owner_mappings"],
        "original_source_positive_expression_calls":original["source_positive_calls"],
        "original_joined_expression_calls":original["source_joined_calls"],
        "original_missing_genes":original["missing_genes"],
        "original_missing_conditions":original["missing_conditions"],
        "original_gene_anatomy_edges":original["source_anatomy_edges"],
        "original_gene_condition_edges":original["source_condition_edges"],
        "all_genuine_source_mapped_relationships":len(edges),
        "independent_SQL_source_join_records":original["source_sql_join_distinct_records"],
        "full_original_combined_input_graph_triples":len(original["full_combined"]),
        "full_original_RO_and_GenEx_and_Bgee_input_used":True,
        "original_source_ontology_schema_axiom_count":2,
        "independent_SPARQL_expected_consequences":len(oracle),
        "Apache_Jena_entire_original_input_rule_consequences":len(observed),
        "Apache_Jena_missing_source_consequences":0,
        "Apache_Jena_unexpected_source_consequences":0,
        "entire_original_source_input_rules_agree_with_independent_Python_SPARQL":True,
        "independent_source_rule_consequences_sha256":baseline.digest_set(oracle),
        "Jena_rule_consequences_sha256":jena_digest,
        "preview_consequence_SHA256_only":hashes,
        "Jena_rule_engine": "Apache Jena GenericRuleReasoner forward rule engine; only two pinned source-owned rules",
        "full_RO_OWL_RL_ontology_materialization":False,
        "entire_RO_GenEx_Bgee_general_OWL_RL_reasoner_comparison":False,
        "independent_equal_rule_capability_not_model_lift":True,
        "source_ground_biomedical_relation_not_clinical_efficacy":True,
        "clinical_valid_at_and_first_public_time":"NOT_MEASURED",
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("prepare","verify"),required=True)
    ap.add_argument("--archive",type=Path,required=True)
    for n in ("obda","owl","r2rml","ro-base","core"):
        ap.add_argument("--"+n,type=Path,required=True)
    ap.add_argument("--input-nt",type=Path)
    ap.add_argument("--jena-nt",type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    author={"bgee_v14_genex."+k:getattr(a,k) for k in ("obda","owl","r2rml")}
    original=verified_owner_input(a.archive,author,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    if a.mode=="prepare":
        if a.input_nt is None:
            raise ValueError("preflight needs ephemeral all-original N-Triples destination")
        print(json.dumps(write_input(original,a.input_nt),sort_keys=True))
    else:
        if a.jena_nt is None or a.output is None:
            raise ValueError("source comparison needs exact Jena output and evidence destination")
        evidence=verify(original,a.jena_nt)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(evidence,indent=2,sort_keys=True)+chr(10))
        print(json.dumps({
            "source_relationships":evidence["all_genuine_source_mapped_relationships"],
            "jena_independent_rules":evidence["Apache_Jena_entire_original_input_rule_consequences"],
            "static_rules":evidence["independent_SPARQL_expected_consequences"],
            "missing":evidence["Apache_Jena_missing_source_consequences"],
            "unexpected":evidence["Apache_Jena_unexpected_source_consequences"],
            "official_NIH":False},sort_keys=True))

if __name__=="__main__":
    main()
