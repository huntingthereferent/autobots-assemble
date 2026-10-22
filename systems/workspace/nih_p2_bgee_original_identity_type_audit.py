"""E19 audit original Bgee referent OWL identity and RDF type entailments.

Independently extract EVERY owl:sameAs and rdf:type statement with an original
gene or source-target node as either endpoint, using native RDFLib traversal
and declarative SPARQL. Distinguish reflexive from nonreflexive sameAs and
owner-authored original type facts from full-profile type entailments.

No inference is admitted as a new observed gene identity or biological result.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time
from rdflib import Graph,URIRef,RDF,OWL

from . import nih_p2_bgee_cross_engine_jena as gate
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_exhaustive_sharded_owlrl as dig
from . import nih_p2_bgee_original_referent_all_predicate_inventory as e18

SCHEMA="nih-p2-e19-original-bgee-referent-type-and-sameas-audit-v1"
SOURCE_GRAPH=34181
SOURCE_EDGES=25027
MAX_CLOSURE=1800000
VALUES_SPARQL="""SELECT ?s ?p ?o WHERE {
  VALUES ?p { <http://www.w3.org/2002/07/owl#sameAs>
              <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> }
  ?s ?p ?o .
}"""
PREDICATES=(OWL.sameAs,RDF.type)


def identity_type_scope_native(g,original_edges):
    genes,targets=e18.native_nodes(original_edges)
    native=genes|targets
    scanned=set()
    for p in PREDICATES:
        for s,o in g.subject_objects(p):
            if s in native or o in native:
                scanned.add((s,p,o))
    return scanned


def identity_type_scope_sparql(g,original_edges):
    genes,targets=e18.native_nodes(original_edges)
    native=genes|targets
    return {(s,p,o) for s,p,o in g.query(VALUES_SPARQL) if s in native or o in native}


def source_class_partition(entries,source_edges):
    genes,targets=e18.native_nodes(source_edges)
    classes=Counter()
    subclass_object_sha=Counter()
    classes_by_kind={"gene_subject_type":0,"target_subject_type":0,
                     "external_subject_type_of_native_node":0}
    for s,p,o in entries:
        if p!=RDF.type:
            raise ValueError("non-type statement leaked into original source class census")
        if s in genes:
            classes_by_kind["gene_subject_type"]+=1
        elif s in targets:
            classes_by_kind["target_subject_type"]+=1
        elif o in genes|targets:
            classes_by_kind["external_subject_type_of_native_node"]+=1
        else:
            raise ValueError("RDF type statement does not touch original Bgee referent")
        # Protect the original target ID universe: publish digest only.
        key=sha256(str(o).encode()).hexdigest()
        subclass_object_sha[key]+=1
        classes[str(type(o).__name__)]+=1
    if sum(classes_by_kind.values())!=len(entries):
        raise ValueError("type scope category partition cannot reconcile")
    return classes_by_kind,classes,subclass_object_sha


def compare_identity_type(originals,full,independent,source_edges):
    if full!=independent:
        raise ValueError("E19 independent native/SPARQL sameAs/type scope mismatch: "+
                         json.dumps({"native_only":len(full-independent),
                                     "sparql_only":len(independent-full)}))
    if not originals.issubset(full):
        raise ValueError("materialized OWL RL graph lost original source type/identity statements")
    genes,targets=e18.native_nodes(source_edges)
    native=genes|targets
    full_alias={t for t in full if t[1]==OWL.sameAs}
    source_alias={t for t in originals if t[1]==OWL.sameAs}
    self_alias={t for t in full_alias if t[0]==t[2]}
    cross_alias=full_alias-self_alias
    true_self={ (n,OWL.sameAs,n) for n in native}
    self_missing=true_self-self_alias
    self_non_native=self_alias-true_self
    full_types={t for t in full if t[1]==RDF.type}
    source_types={t for t in originals if t[1]==RDF.type}
    types_added=full_types-source_types
    by_kind,node_type_counts,class_hashes=source_class_partition(full_types,source_edges)
    by_kind_added,_,class_hashes_added=source_class_partition(types_added,source_edges)
    counts=Counter()
    for s,p,o in cross_alias:
        if s in genes and o in targets:cat="gene_to_target"
        elif s in targets and o in genes:cat="target_to_gene"
        elif s in genes and o in genes:cat="gene_to_gene"
        elif s in targets and o in targets:cat="target_to_target"
        else:cat="source_to_or_from_external"
        counts[cat]+=1
    return {
        "original_gene_nodes":len(genes),
        "original_target_nodes":len(targets),
        "original_referent_nodes_total":len(native),
        "original_identity_type_triples":len(originals),
        "whole_closure_identity_type_triples":len(full),
        "source_authored_original_sameAs":len(source_alias),
        "source_authored_original_rdf_type":len(source_types),
        "whole_closure_sameAs_triples_touching_original_nodes":len(full_alias),
        "whole_closure_reflexive_sameAs":len(self_alias),
        "whole_closure_nonreflexive_sameAs":len(cross_alias),
        "original_nodes_lacking_reflexive_self_identity":len(self_missing),
        "unexpected_reflexive_subjects_outside_original_universe":len(self_non_native),
        "nonreflexive_sameAs_orientation_counts":dict(sorted(counts.items())),
        "nonreflexive_sameAs_candidate_sha256":
            sorted(sha256("|".join(map(str,t)).encode()).hexdigest() for t in cross_alias)[:16],
        "source_original_rdf_type":len(source_types),
        "full_profile_rdf_type_touching_original_nodes":len(full_types),
        "full_profile_inferred_rdf_type_touching_original_nodes":len(types_added),
        "full_profile_type_endpoints":by_kind,
        "full_profile_added_type_endpoints":by_kind_added,
        "type_object_node_kinds":dict(sorted(node_type_counts.items())),
        "distinct_full_profile_type_object_sha256":len(class_hashes),
        "distinct_new_type_object_sha256":len(class_hashes_added),
        "new_type_top_12_class_sha256_counts":
            [{"type_object_sha256":k,"count":v}
             for k,v in sorted(class_hashes_added.items(),key=lambda t:(-t[1],t[0]))[:12]],
        "source_native_type_and_identity_scan_equals_declarative_SPARQL":True,
        "identity_scope_sha256_native":dig.digest_set(full),
        "identity_scope_sha256_sparql":dig.digest_set(independent),
        "nonreflexive_identity_results_are_hypotheses_not_gene_alias_evidence":True,
        "rdf_type_statements_are_ontology_consequences_not_new_biological_observations":True,
        "independent_complete_general_OWL_RL_engine_run":False,
        "global_OWL_consistency_proven":False,
        "official_NIH_benchmark":False,
        "original_W13_or_other_NIH_lanes_modified":False,
    }


def execute(archive,author_files,ro_files):
    orig=gate.verified_owner_input(archive,author_files,ro_files)
    four.original_four_source_axioms(orig)
    source_graph=orig["full_combined"]
    edges=orig["source_edges"]
    if len(source_graph)!=SOURCE_GRAPH or len(edges)!=SOURCE_EDGES:
        raise ValueError("original authenticated source population changed")
    raw=identity_type_scope_native(source_graph,edges)
    materialized=Graph()
    materialized+=source_graph
    from owlrl import DeductiveClosure,OWLRL_Semantics
    start=time.monotonic()
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(materialized)
    elapsed=round(time.monotonic()-start,3)
    if len(materialized)>MAX_CLOSURE:
        raise ValueError("source complete OWL RL materialization exceeds frozen bound")
    native=identity_type_scope_native(materialized,edges)
    independent=identity_type_scope_sparql(materialized,edges)
    report=compare_identity_type(raw,native,independent,edges)
    report.update({
        "schema":SCHEMA,
        "original_source_graph_triples":SOURCE_GRAPH,
        "full_materialized_RDF_graph_triples":len(materialized),
        "general_OWL_RL_wall_seconds":elapsed,
        "source_owner_all_original_files_authenticated":True,
        "original_Bgee_archive_git_blob":orig["archive_receipt"]["complete_original_source_git_blob_sha1"],
        "original_author_GenEx_commit":four.bridge.COMMIT,
        "original_RO_owner_commit":four.bridge.source.COMMIT,
    })
    report["status"]=(
        "E19_NONREFLEXIVE_OR_MISSING_SELF_IDENTITY_CANDIDATES"
        if report["whole_closure_nonreflexive_sameAs"] or
           report["original_nodes_lacking_reflexive_self_identity"]
        else "E19_SOURCE_NODE_IDENTITY_ONLY_REFLEXIVE")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    for name in ("obda","owl","r2rml","ro-base","core"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    authors={"bgee_v14_genex."+name:getattr(a,name) for name in ("obda","owl","r2rml")}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    report={"schema":SCHEMA,"status":"NOT_VERIFIED","original_raw_rows_or_full_closure_redistributed":False}
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    try:
        report.update(execute(a.archive,authors,{"ro-base.owl":a.ro_base,"core.owl":a.core}))
    except Exception as e:
        report["status"]="FAILED_NOT_VERIFIED"
        report["failure_class"]=type(e).__name__
        raise
    finally:
        a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":report["status"],
        "original_referents":report["original_referent_nodes_total"],
        "self_identity":report["whole_closure_reflexive_sameAs"],
        "nonself_identity":report["whole_closure_nonreflexive_sameAs"],
        "type_statements":report["full_profile_rdf_type_touching_original_nodes"],
        "native_SPARQL_agree":report["source_native_type_and_identity_scan_equals_declarative_SPARQL"],
        "NIH_scored":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
