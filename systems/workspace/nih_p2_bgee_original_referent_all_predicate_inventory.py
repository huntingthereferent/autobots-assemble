"""E18 source-node predicate inventory of COMPLETE original Bgee full OWL RL graph.

E16 examined only three preselected RO properties. E18 discovers *all*
other RDF predicates and relationships on authentic gene/target referents.
It compares the closure to the original 34,181-triple graph and independently
enumerates every relevant triple with RDFLib native graph iteration and SPARQL.

The discovered metadata/entailments are not independent biological data.
Never retain source node names or raw source/materialized RDF statements.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time

from rdflib import Graph,URIRef,RDF,OWL
from . import nih_p2_bgee_cross_engine_jena as source
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_exhaustive_sharded_owlrl as dig

SCHEMA="nih-p2-e18-complete-original-referent-predicate-differential-v1"
MAX_GRAPH_TRIPLES=1800000
FIXED_ORIGINAL_GRAPH=34181
FIXED_SOURCE_EDGES=25027
FOUR_RULE_TOTAL=100108
SCAN_SPARQL="""SELECT ?s ?p ?o WHERE {
  ?s ?p ?o .
  FILTER(isIRI(?s) || isIRI(?o))
}"""


def native_nodes(source_edges):
    genes={s for s,p,o in source_edges}
    targets={o for s,p,o in source_edges}
    if not genes or not targets or genes&targets:
        raise ValueError("original Bgee gene/target node roles overlap or missing")
    return genes,targets


def graph_scope_native(g,source_edges):
    genes,targets=native_nodes(source_edges)
    nodes=genes|targets
    return {(s,p,o) for s,p,o in g if s in nodes or o in nodes}


def graph_scope_sparql(g,source_edges):
    genes,targets=native_nodes(source_edges)
    nodes=genes|targets
    return {(s,p,o) for s,p,o in g.query(SCAN_SPARQL)
            if s in nodes or o in nodes}


def safe_hashes(rows,limit=12):
    return sorted(sha256("|".join(map(str,t)).encode()).hexdigest()
                  for t in rows)[:limit]


def predicate_counts(rows):
    return dict(sorted(Counter(str(p) for s,p,o in rows).items()))


def orientation_counts(rows,source_edges):
    genes,targets=native_nodes(source_edges)
    nodes=genes|targets
    out=Counter()
    for s,p,o in rows:
        s_gene=s in genes
        o_gene=o in genes
        s_target=s in targets
        o_target=o in targets
        if s_gene and o_target: category="gene_to_target"
        elif s_target and o_gene: category="target_to_gene"
        elif s_gene and o_gene: category="gene_to_gene"
        elif s_target and o_target: category="target_to_target"
        elif s_gene: category="gene_to_external"
        elif o_gene: category="external_to_gene"
        elif s_target: category="target_to_external"
        elif o_target: category="external_to_target"
        else: raise ValueError("non-source triple admitted to source universe")
        out[category]+=1
    return dict(sorted(out.items()))


def compare(original_scope,closure_scope,independent_scope,source_edges,source_rules):
    if closure_scope!=independent_scope:
        missing=closure_scope-independent_scope
        extra=independent_scope-closure_scope
        raise ValueError("whole-source-node unrestricted native and SPARQL disagree "+
                         json.dumps({"native_only":len(missing),"SPARQL_only":len(extra)}))
    if not original_scope.issubset(closure_scope):
        raise ValueError("OWL RL closure lost authenticated original node triples: "+
                         str(len(original_scope-closure_scope)))
    if not source_rules.issubset(closure_scope):
        raise ValueError("prior four original-owner rule consequences absent from complete source-node closure: "+
                         str(len(source_rules-closure_scope)))
    if len(source_rules)!=FOUR_RULE_TOTAL:
        raise ValueError("original four-rule baseline differs from authenticated full-source size")
    new=closure_scope-original_scope
    beyond=closure_scope-(original_scope|source_rules)
    source_p={four.bridge.RO_EXPRESSED,four.bridge.RO_EXPRESSES,four.GENOMIC}
    outside_pred={t for t in beyond if t[1] not in source_p}
    source_pred_extra={t for t in beyond if t[1] in source_p}
    category={
        "rdf_type":sum(p==RDF.type for s,p,o in outside_pred),
        "owl_sameAs":sum(p==OWL.sameAs for s,p,o in outside_pred),
        "other_predicates":sum(p not in (RDF.type,OWL.sameAs) for s,p,o in outside_pred),
    }
    if sum(category.values())!=len(outside_pred):
        raise ValueError("source-owner subject/object inferred predicate partition mismatch")
    return {
        "original_source_gene_nodes":len(native_nodes(source_edges)[0]),
        "original_source_target_nodes":len(native_nodes(source_edges)[1]),
        "source_original_graph_touching_referents":len(original_scope),
        "whole_profile_touching_original_referents":len(closure_scope),
        "whole_profile_added_referent_touching_RDF_triples":len(new),
        "original_four_rule_source_relationship_triples":len(source_rules),
        "four_rule_source_relationships_missing":0,
        "remaining_entailments_beyond_source_plus_four_rules":len(beyond),
        "remaining_entailments_under_other_predicates":len(outside_pred),
        "remaining_entailments_under_same_three_RO_predicates":len(source_pred_extra),
        "other_predicate_classifications":category,
        "original_predicate_counts":predicate_counts(original_scope),
        "all_full_profile_source_node_predicate_counts":predicate_counts(closure_scope),
        "new_inferred_predicate_counts":predicate_counts(new),
        "beyond_original_and_four_rule_predicate_counts":predicate_counts(beyond),
        "beyond_original_and_four_rule_orientation_counts":orientation_counts(beyond,source_edges),
        "source_scope_native_equals_independent_SPARQL":True,
        "original_source_scope_sha256":dig.digest_set(original_scope),
        "whole_scope_native_sha256":dig.digest_set(closure_scope),
        "whole_scope_SPARQL_sha256":dig.digest_set(independent_scope),
        "beyond_source_and_four_rule_sha256":dig.digest_set(beyond),
        "beyond_source_and_four_rule_preview_hashed_only":safe_hashes(beyond),
        "additional_RDF_closure_statements_are_not_new_biomedical_observations":True,
        "full_profile_logic_consistency_proven":False,
        "independent_complete_OWL_RL_reasoner_confirmed":False,
        "official_NIH_benchmark":False,
        "original_W13_and_other_research_lanes_modified":False,
    }


def execute(archive,authors,ro_files):
    original=source.verified_owner_input(archive,authors,ro_files)
    four.original_four_source_axioms(original)
    raw=original["full_combined"]
    edges=original["source_edges"]
    if len(raw)!=FIXED_ORIGINAL_GRAPH or len(edges)!=FIXED_SOURCE_EDGES:
        raise ValueError("whole original Bgee/GenEx/RO input size changed")
    original_baseline,extra=four.full_static_source_rule_oracle(original)
    if len(original_baseline)!=FOUR_RULE_TOTAL:
        raise ValueError("source-owned original four-rule expected entailment count changed")
    base_scope=graph_scope_native(raw,edges)
    from owlrl import DeductiveClosure,OWLRL_Semantics
    materialized=Graph()
    materialized+=raw
    begin=time.monotonic()
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(materialized)
    elapsed=round(time.monotonic()-begin,3)
    if len(materialized)>MAX_GRAPH_TRIPLES:
        raise ValueError("full-source RDF materialized graph exceeds frozen bound")
    native=graph_scope_native(materialized,edges)
    independent=graph_scope_sparql(materialized,edges)
    result=compare(base_scope,native,independent,edges,original_baseline)
    result.update({
        "schema":SCHEMA,
        "source_original_combined_graph_triples":len(raw),
        "full_owlrl_materialized_graph_triples":len(materialized),
        "full_profile_wall_seconds":elapsed,
        "original_Bgee_source_git_blob":
             original["archive_receipt"]["complete_original_source_git_blob_sha1"],
        "original_GenEx_author_commit":four.bridge.COMMIT,
        "original_RO_owner_commit":four.bridge.source.COMMIT,
        "source_owner_whole_file_authenticated":True,
        "complete_original_full_profile_processed":True,
        "comparison_is_original_referent_unrestricted_predicate_only":True,
    })
    result["status"]=(
        "E18_REFERENT_METADATA_OR_OTHER_RELATIONSHIP_ENTAILMENTS_PRESENT"
        if result["remaining_entailments_beyond_source_plus_four_rules"] else
        "E18_ORIGINAL_REFERENTS_ONLY_SOURCE_AND_FOUR_RULE_RELATIONSHIPS")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    for name in ("obda","owl","r2rml","ro-base","core"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    authors={"bgee_v14_genex."+name:getattr(a,name) for name in ("obda","owl","r2rml")}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    report={"schema":SCHEMA,"status":"NOT_VERIFIED","source_raw_data_redistributed":False}
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    try:
        report.update(execute(a.archive,authors,{"ro-base.owl":a.ro_base,"core.owl":a.core}))
    except Exception as e:
        report["status"]="FAILED_NOT_VERIFIED"
        report["failure_type"]=type(e).__name__
        report["failure_category"]="source_integrity_or_logic_or_resource"
        raise
    finally:
        a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":report["status"],
        "source_nodes_all_predicate_triples":report["whole_profile_touching_original_referents"],
        "other_predicate_conclusions":report["remaining_entailments_under_other_predicates"],
        "scope_native_SPARQL_equal":report["source_scope_native_equals_independent_SPARQL"],
        "official_NIH":False},sort_keys=True))


if __name__=="__main__":
    main()
