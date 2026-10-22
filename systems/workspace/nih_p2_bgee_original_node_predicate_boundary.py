"""E16: original-node / three-source-predicate coverage audit of full OWL RL.

Distinct from E15: E15 restricted comparison to known mapped gene->target
and target->gene pairs. Here examine EVERY triple using the three source-owned
relationship predicates if at least one endpoint belongs to ANY authenticated
original Bgee referent node. Other endpoint and direction remain unrestricted,
so additional candidate entailments are visible rather than filtered away.

An additional materialized RDF triple is NOT independently corroborated
biomedical evidence. Preserve only counts/digests of differences.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from rdflib import Graph, URIRef, RDF

from . import nih_p2_bgee_cross_engine_jena as gate
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_exhaustive_sharded_owlrl as digest

SCHEMA="nih-p2-bgee-full-owlrl-all-original-nodes-predicate-audit-v1"
SOURCE_GRAPH=34181
SOURCE_EDGES=25027
PRIOR_SCOPED_RULE_SET=100108
MAX_MATERIALIZED=1800000
PREDICATES=(four.bridge.RO_EXPRESSED,four.bridge.RO_EXPRESSES,four.GENOMIC)
SOURCE_PREDICATES_SPARQL="""SELECT ?s ?p ?o WHERE {
  VALUES ?p { <http://purl.obolibrary.org/obo/RO_0002206>
              <http://purl.obolibrary.org/obo/RO_0002292>
              <http://purl.obolibrary.org/obo/RO_0002330> }
  ?s ?p ?o .
  FILTER(isIRI(?s) && isIRI(?o))
}"""


def owner_node_universe(source_edges):
    genes={s for s,p,o in source_edges}
    targets={o for s,p,o in source_edges}
    if not genes or not targets or genes&targets:
        raise ValueError("missing or colliding native Bgee referent node classes")
    return genes,targets


def unrestricted_direct_predicate_scan(closure,source_edges):
    """Every allowed predicate with any source node, regardless of direction/pair."""
    genes,targets=owner_node_universe(source_edges)
    natives=genes|targets
    scanned=set()
    for p in PREDICATES:
        for s,o in closure.subject_objects(p):
            if isinstance(s,URIRef) and isinstance(o,URIRef) and (s in natives or o in natives):
                scanned.add((s,p,o))
    return scanned


def independent_sparql_predicate_scan(closure,source_edges):
    """Separate declarative SPARQL match for the *same* unrestricted scope."""
    genes,targets=owner_node_universe(source_edges)
    natives=genes|targets
    result=set()
    for s,p,o in closure.query(SOURCE_PREDICATES_SPARQL):
        if s in natives or o in natives:
            result.add((s,p,o))
    return result


def compare_all_source_nodes(direct,independent,expected,original_edges):
    genes,targets=owner_node_universe(original_edges)
    if direct!=independent:
        left=direct-independent
        right=independent-direct
        raise ValueError("entire original-node predicate census Jena-neutral native/SPARQL disagreement: "+
                         json.dumps({"native_only":len(left),"sparql_only":len(right)}))
    if not expected.issubset(direct):
        missing=expected-direct
        raise ValueError("previously verified real Bgee four-rule consequences now absent: "+
                         json.dumps({"missing":len(missing),
                                     "missing_SHA256":[sha256("|".join(map(str,t)).encode()).hexdigest()
                                                       for t in sorted(missing,key=lambda t:tuple(map(str,t)))[:4]]}))
    additional=direct-expected
    distribution={}
    for _,p,_ in direct:
        k=str(p)
        distribution[k]=distribution.get(k,0)+1
    novel_direction_count={
        "gene_to_native_target":0,
        "native_target_to_gene":0,
        "gene_to_other":0,
        "other_to_gene":0,
        "native_target_to_other":0,
        "other_to_native_target":0,
        "other_or_crossed":0
    }
    for s,p,o in additional:
        if s in genes and o in targets:
            novel_direction_count["gene_to_native_target"]+=1
        elif s in targets and o in genes:
            novel_direction_count["native_target_to_gene"]+=1
        elif s in genes and o not in genes|targets:
            novel_direction_count["gene_to_other"]+=1
        elif o in genes and s not in genes|targets:
            novel_direction_count["other_to_gene"]+=1
        elif s in targets and o not in genes|targets:
            novel_direction_count["native_target_to_other"]+=1
        elif o in targets and s not in genes|targets:
            novel_direction_count["other_to_native_target"]+=1
        else:
            novel_direction_count["other_or_crossed"]+=1
    if sum(novel_direction_count.values())!=len(additional):
        raise ValueError("original node extra consequence category partition not exhaustive")
    return {
        "original_qualified_gene_nodes":len(genes),
        "original_qualified_target_nodes":len(targets),
        "predeclared_source_owned_predicates":list(map(str,PREDICATES)),
        "unrestricted_original_node_predicate_triples":len(direct),
        "full_source_predicate_native_SPARQL_all_triples_equal":True,
        "previously_verified_four_source_rule_triples":len(expected),
        "previously_verified_source_rule_triples_missing":0,
        "additional_original_node_predicate_triples_not_in_four_rule_set":len(additional),
        "additional_predicate_orientations":novel_direction_count,
        "full_original_node_predicate_counts":dict(sorted(distribution.items())),
        "unrestricted_predicate_result_sha256":digest.digest_set(direct),
        "independent_unrestricted_SPARQL_result_sha256":digest.digest_set(independent),
        "additional_candidate_SHA256":digest.digest_set(additional),
        "additional_candidate_preview_hashed_only":
            sorted(sha256("|".join(map(str,t)).encode()).hexdigest() for t in additional)[:12],
        "unmatched_triples_are_exploratory_not_observed_biology":True,
        "full_owl_dl_consistency_proven":False,
        "second_independent_complete_OWL_RL_engine_verified":False,
        "official_NIH_score":False,
        "W13_other_lanes_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    for n in ("obda","owl","r2rml","ro-base","core"):
        p.add_argument("--"+n,type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report={
        "schema":SCHEMA,
        "status":"STARTED_NOT_VERIFIED",
        "source_rows_or_raw_RDF_redistributed":False,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    try:
        author={"bgee_v14_genex."+k:getattr(args,k) for k in ("obda","owl","r2rml")}
        original=gate.verified_owner_input(args.archive,author,
                           {"ro-base.owl":args.ro_base,"core.owl":args.core})
        four.original_four_source_axioms(original)
        full=Graph()
        full+=original["full_combined"]
        if len(full)!=SOURCE_GRAPH or len(original["source_edges"])!=SOURCE_EDGES:
            raise ValueError("original authenticated source baseline changed")
        baseline,_=four.full_static_source_rule_oracle(original)
        if len(baseline)!=PRIOR_SCOPED_RULE_SET:
            raise ValueError("independent previous original four-rule baseline mismatch")
        from owlrl import DeductiveClosure,OWLRL_Semantics
        start=time.monotonic()
        DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(full)
        report["owlrl_full_input_wall_seconds"]=round(time.monotonic()-start,3)
        report["whole_OWL_RL_materialized_RDF_triples"]=len(full)
        if len(full)>MAX_MATERIALIZED:
            raise ValueError("full original ontology profile output over finite bound")
        direct=unrestricted_direct_predicate_scan(full,original["source_edges"])
        independent=independent_sparql_predicate_scan(full,original["source_edges"])
        report.update(compare_all_source_nodes(direct,independent,baseline,original["source_edges"]))
        report.update({
            "authenticated_original_graph_triples":SOURCE_GRAPH,
            "authenticated_original_mapped_Bgee_triples":SOURCE_EDGES,
            "original_Bgee_zip_git_blob":
                original["archive_receipt"]["complete_original_source_git_blob_sha1"],
            "original_author_GenEx_commit":four.bridge.COMMIT,
            "original_owner_RO_commit":four.bridge.source.COMMIT,
            "full_profile_computed_by_Python_owlrl":True,
            "comparison_is_unrestricted_in_original_node_predicates_only":True,
            "source_authentication_preserved":True,
        })
        report["status"]=("ORIGINAL_NODE_PREDICATE_SET_EQUALS_FOUR_RULES"
                          if report["additional_original_node_predicate_triples_not_in_four_rule_set"]==0
                          else "ADDITIONAL_ORIGINAL_NODE_SOURCE_PREDICATE_CANDIDATES_FOUND")
    except Exception as e:
        report["status"]="FAILED_OR_SOURCE_MISMATCH_NOT_VERIFIED"
        report["failure_category"]=type(e).__name__
        report["failure_summary"]=str(e)[:250]
        raise
    finally:
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":report["status"],
        "full_materialized":report["whole_OWL_RL_materialized_RDF_triples"],
        "original_node_source_predicate_triples":
             report["unrestricted_original_node_predicate_triples"],
        "additional_outside_four_rule_set":
             report["additional_original_node_predicate_triples_not_in_four_rule_set"],
        "native_SPARQL_equal":report["full_source_predicate_native_SPARQL_all_triples_equal"],
        "NIH_scored":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
