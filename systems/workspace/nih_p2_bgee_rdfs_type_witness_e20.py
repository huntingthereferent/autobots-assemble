"""E20 independent source-owned RDFS type witness audit on authentic Bgee nodes.

The entire original GenEx/Bgee/RO graph is authenticated before comparison.
Reproduce a *limited* set of rdf:type inferences without calling OWL RL:
source-authored rdf:type, source schema rdfs:domain/range, source RDFS
subPropertyOf ancestry and rdfs:subClassOf ancestry, applied to original
source triples and independently verified four-rule gene-expression edges.

This is a conservative explanation audit. Report all unexplained rdf:type
statements as residual candidates; never call them unsupported biological
phenotypes or assume domain/range accounts for the entire OWL RL closure.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path
import time

from rdflib import Graph,URIRef,RDF,RDFS
from . import nih_p2_bgee_cross_engine_jena as source
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_original_identity_type_audit as e19
from . import nih_p2_bgee_exhaustive_sharded_owlrl as receipts

SCHEMA="nih-p2-e20-original-source-domain-range-type-witness-v1"
FULL_INPUT=34181
ORIGINAL_EDGES=25027
MAX_CLOSURE=1800000
MAX_INDEPENDENT_TYPES=150000

def direct_owner_schema(graph):
    """Only original owner RDFS axiom triples; no reasoner-generated schema."""
    out={}
    for predicate in (RDFS.subPropertyOf,RDFS.subClassOf,RDFS.domain,RDFS.range):
        native={(s,o) for s,o in graph.subject_objects(predicate)
                if isinstance(s,URIRef) and isinstance(o,URIRef)}
        query="""SELECT ?s ?o WHERE { ?s <%s> ?o
                   FILTER(isIRI(?s) && isIRI(?o)) }""" % str(predicate)
        sparql=set(graph.query(query))
        if native!=sparql:
            raise ValueError("owner original schema native/SPARQL disagreement: "+str(predicate))
        out[str(predicate)]=native
    return out


def reachability(links):
    adj=defaultdict(set)
    for a,b in links:
        adj[a].add(b)
    result={}
    def closure(node):
        if node not in result:
            todo=list(adj.get(node,()))
            seen={node}
            while todo:
                next_node=todo.pop()
                if next_node not in seen:
                    seen.add(next_node)
                    todo.extend(adj.get(next_node,()))
            result[node]=seen
        return result[node]
    return closure


def explicit_rdfs_type_oracle(original_graph, four_consequences, native_nodes, schema):
    """Independent finite RDFS support; no invocation of owlrl."""
    props=reachability(schema[str(RDFS.subPropertyOf)])
    classes=reachability(schema[str(RDFS.subClassOf)])
    domains=defaultdict(set)
    ranges=defaultdict(set)
    for predicate,cls in schema[str(RDFS.domain)]:
        domains[predicate].add(cls)
    for predicate,cls in schema[str(RDFS.range)]:
        ranges[predicate].add(cls)
    source_edges=set(original_graph)|set(four_consequences)
    out=set()
    support=Counter()
    for s,p,o in source_edges:
        if p==RDF.type and s in native_nodes and isinstance(o,URIRef):
            for c in classes(o):
                candidate=(s,RDF.type,c)
                if candidate not in out:
                    out.add(candidate)
                    support["source_asserted_type_and_original_class_ancestry"]+=1
        if not isinstance(p,URIRef):
            continue
        for parent in props(p):
            if s in native_nodes:
                for c in domains.get(parent,()):
                    for ancestor in classes(c):
                        candidate=(s,RDF.type,ancestor)
                        if candidate not in out:
                            out.add(candidate)
                            support["original_property_domain_witness"]+=1
            if o in native_nodes and isinstance(o,URIRef):
                for c in ranges.get(parent,()):
                    for ancestor in classes(c):
                        candidate=(o,RDF.type,ancestor)
                        if candidate not in out:
                            out.add(candidate)
                            support["original_property_range_witness"]+=1
    if len(out)>MAX_INDEPENDENT_TYPES:
        raise ValueError("RDFS limited original type oracle exceeds finite bound")
    return out,dict(support),{"source_facts_considered":len(source_edges),
                              "direct_source_schema_sizes":{key:len(v) for key,v in schema.items()}}


def compare_types(original_types, full_types, oracle, support, provenance):
    if not original_types.issubset(full_types):
        raise ValueError("original owner RDF types disappeared from OWL RL closure")
    missing=oracle-full_types
    if missing:
        raise ValueError("authenticated RDFS domain/range/subclass candidate missing from full OWL RL: "+
                         json.dumps({"count":len(missing),
                                     "sample_sha256":sorted(sha256("|".join(map(str,t)).encode()).hexdigest()
                                                            for t in missing)[:8]}))
    if not original_types.issubset(oracle):
        raise ValueError("source asserted native rdf:type not in limited original RDFS oracle")
    inferred=full_types-original_types
    explained=inferred & oracle
    residual=inferred-oracle
    return {
        "original_source_asserted_native_rdf_type":len(original_types),
        "general_OWL_RL_total_original_node_rdf_type":len(full_types),
        "general_OWL_RL_inferred_original_node_rdf_type":len(inferred),
        "limited_source_RDFS_supported_type_statements":len(oracle),
        "independently_RDFS_supported_inferred_type_statements":len(explained),
        "full_profile_type_residual_not_justified_by_this_limited_oracle":len(residual),
        "original_RDFS_candidate_missing_from_full_profile":0,
        "original_source_type_entirely_preserved":True,
        "source_schema_native_SPARQL_exact_equality":True,
        "limited_source_witness_counts_first_support":dict(sorted(support.items())),
        "original_schema_and_sources_summary":provenance,
        "RDFS_explained_inferred_sha256":receipts.digest_set(explained),
        "RDFS_unexplained_candidate_sha256":receipts.digest_set(residual),
        "RDFS_unexplained_candidate_first_12_SHA256":sorted(
            sha256("|".join(map(str,t)).encode()).hexdigest() for t in residual)[:12],
        "residual_is_not_independent_biomedical_discovery":True,
        "source_domain_range_oracle_not_full_OWL_RL":True,
        "independent_complete_OWL_RL_reasoner_verified":False,
        "global_OWL_consistency_proven":False,
        "official_NIH_scored":False,
        "other_NIH_W13_lanes_modified":False,
    }


def original_role_type_partition(original_types, full_types, oracle, gene_nodes, target_nodes):
    """E21 diagnostic: partition original-node type consequences by source role.

    This classifies *subjects*, not OWL inference rules or biology. Gene/target
    roles come exclusively from authenticated Bgee original mapping edges.
    """
    if gene_nodes & target_nodes:
        raise ValueError("original mapped gene and target scopes overlap")
    native = gene_nodes | target_nodes
    if any(s not in native or p != RDF.type for s, p, o in full_types | original_types | oracle):
        raise ValueError("unmapped subject or predicate leaked into source role audit")
    if not original_types <= full_types:
        raise ValueError("source owner type missing from full closure")
    if not oracle <= full_types:
        raise ValueError("restricted source RDFS witness absent from full closure")
    inferred = full_types - original_types
    supported = inferred & oracle
    residual = inferred - oracle
    buckets = {}
    for name, subjects in (("original_gene_role", gene_nodes), ("original_target_role", target_nodes)):
        own = {t for t in original_types if t[0] in subjects}
        this_inferred = {t for t in inferred if t[0] in subjects}
        yes = this_inferred & supported
        no = this_inferred & residual
        if len(yes) + len(no) != len(this_inferred):
            raise ValueError("source role RDFS partition did not reconcile")
        buckets[name] = {
            "original_source_node_count": len(subjects),
            "source_authored_type_statements": len(own),
            "full_profile_inferred_type_statements": len(this_inferred),
            "limited_RDFS_supported_inferred": len(yes),
            "remaining_not_explained_by_limited_RDFS": len(no),
            "remaining_subject_statement_sha256": receipts.digest_set(no),
        }
    for field, expected in (
        ("source_authored_type_statements", len(original_types)),
        ("full_profile_inferred_type_statements", len(inferred)),
        ("limited_RDFS_supported_inferred", len(supported)),
        ("remaining_not_explained_by_limited_RDFS", len(residual)),
    ):
        if sum(item[field] for item in buckets.values()) != expected:
            raise ValueError("original subject-role type totals do not reconcile")
    return {
        "role_partition": buckets,
        "gene_target_roles_are_original_source_observations": True,
        "role_diagnostic_is_not_full_OWL_rule_provenance": True,
        "new_biological_type_annotations_inferred": False,
        "official_NIH_result": False,
    }


def execute(archive,owner_files,ro_files):
    original=source.verified_owner_input(archive,owner_files,ro_files)
    four.original_four_source_axioms(original)
    src=original["full_combined"]
    edges=original["source_edges"]
    if len(src)!=FULL_INPUT or len(edges)!=ORIGINAL_EDGES:
        raise ValueError("whole-file authenticated original graph or Bgee edges changed")
    rules,_=four.full_static_source_rule_oracle(original)
    schema=direct_owner_schema(src)
    genes={s for s,p,o in edges}
    targets={o for s,p,o in edges}
    nodes=genes|targets
    witness,support,provenance=explicit_rdfs_type_oracle(src,rules,nodes,schema)
    before=e19.identity_type_scope_native(src,edges)
    source_types={t for t in before if t[1]==RDF.type}
    closure=Graph()
    closure+=src
    from owlrl import DeductiveClosure,OWLRL_Semantics
    begin=time.monotonic()
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(closure)
    seconds=round(time.monotonic()-begin,3)
    if len(closure)>MAX_CLOSURE:
        raise ValueError("source graph full OWL RL materialization exceeds bound")
    all_types={t for t in e19.identity_type_scope_native(closure,edges) if t[1]==RDF.type}
    independent={t for t in e19.identity_type_scope_sparql(closure,edges) if t[1]==RDF.type}
    if all_types!=independent:
        raise ValueError("whole original node RDF type native and declarative SPARQL scans disagree")
    result=compare_types(source_types,all_types,witness,support,provenance)
    result["E21_original_subject_role_partition"] = original_role_type_partition(
        source_types,all_types,witness,genes,targets)
    result.update({
        "schema":SCHEMA,
        "status":"COMPLETED_SOURCE_RDFS_TYPE_WITNESS_PARTITION",
        "source_owner_full_input_triples":len(src),
        "source_owner_mapped_Bgee_edges":len(edges),
        "original_native_gene_nodes":len(genes),
        "original_native_target_nodes":len(targets),
        "full_OWL_RL_graph_triples":len(closure),
        "full_OWL_RL_wall_seconds":seconds,
        "all_original_owner_files_hash_authenticated":True,
        "original_Bgee_archive_git_blob":original["archive_receipt"]["complete_original_source_git_blob_sha1"],
        "original_GenEx_author_commit":four.bridge.COMMIT,
        "original_RO_owner_commit":four.bridge.source.COMMIT,
        "RDF_type_native_full_scan_equals_declarative_SPARQL":True,
    })
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    for n in ("obda","owl","r2rml","ro-base","core"):
        p.add_argument("--"+n,type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    files={"bgee_v14_genex."+name:getattr(a,name) for name in ("obda","owl","r2rml")}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result={"schema":SCHEMA,"status":"NOT_YET_SOURCE_VERIFIED"}
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    try:
        result=execute(a.archive,files,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    except Exception as e:
        result["status"]="FAILED_OR_INCOMPLETE_NOT_SOURCE_VERIFIED"
        result["failure_class"]=type(e).__name__
        raise
    finally:
        a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":result["status"],
        "inferred_types":result["general_OWL_RL_inferred_original_node_rdf_type"],
        "source_RDFS_supported_inferred":result["independently_RDFS_supported_inferred_type_statements"],
        "residual_not_independently_explained":result["full_profile_type_residual_not_justified_by_this_limited_oracle"],
        "original_source_asserted":result["original_source_asserted_native_rdf_type"],
        "NIH_scored":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
