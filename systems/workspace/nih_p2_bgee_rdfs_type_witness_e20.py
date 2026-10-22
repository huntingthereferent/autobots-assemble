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

from rdflib import Graph,URIRef,RDF,RDFS,BNode
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


def residual_type_class_inventory(original_types,full_types,restricted_oracle):
    """E22: inventory actual class TERM kinds, preserving blank-node identity wall.

    RDF blank node labels generated by parsing/materialization are NOT stable
    source-owned global class identifiers. Store only group/count summaries.
    """
    if not original_types <= full_types or not restricted_oracle <= full_types:
        raise ValueError("original or independently supported type missing from full profile")
    residue=(full_types-original_types)-restricted_oracle
    byterm=Counter(c for s,p,c in residue if p==RDF.type)
    if sum(byterm.values())!=len(residue):
        raise ValueError("residual contains non-RDF-type statement")
    families=Counter()
    anonymous_counts=[]
    named=[]
    for term,count in byterm.items():
        if isinstance(term,BNode):
            families["anonymous_RDF_blank_node_class_term"]+=count
            anonymous_counts.append(count)
            continue
        cl=str(term)
        if cl.startswith("http://www.w3.org/2002/07/owl#"):
            name="OWL_vocabulary"
        elif cl.startswith("http://www.w3.org/2000/01/rdf-schema#") or cl.startswith("http://www.w3.org/1999/02/22-rdf-syntax-ns#"):
            name="RDF_RDFS_vocabulary"
        elif "purl.obolibrary.org/obo/" in cl:
            name="source_OBO_URI"
        elif "w3.org/" in cl:
            name="other_W3C_URI"
        else:
            name="other_named_class_URI"
        families[name]+=count
        named.append({"class_URI":cl,"count":count})
    if sum(families.values())!=len(residue):
        raise ValueError("type family census incomplete")
    named.sort(key=lambda x:(-x["count"],x["class_URI"]))
    # Stable aggregate of group counts; no session-random BNode identifiers.
    canonical=json.dumps({
        "named":sorted(named,key=lambda x:x["class_URI"]),
        "blank_node_class_statement_counts":sorted(anonymous_counts),
        "families":dict(sorted(families.items())),
    },sort_keys=True,separators=(",",":"))
    return {
        "original_full_profile_limited_oracle_residual_count":len(residue),
        "distinct_residual_class_terms":len(byterm),
        "distinct_anonymous_blank_node_class_terms":len(anonymous_counts),
        "anonymous_blank_node_class_statement_counts":sorted(anonymous_counts),
        "source_class_term_family_counts":dict(sorted(families.items())),
        "top_named_class_URI_counts":named[:20],
        "source_class_term_count_digest_sha256":sha256(canonical.encode()).hexdigest(),
        "anonymous_blank_node_labels_not_persistent_identifiers":True,
        "class_term_counts_are_not_inference_rule_provenance":True,
        "no_new_biological_observation":True,
        "NIH_scored":False,
    }



def original_anonymous_class_premise_census(owner_graph, original_types, full_types, restricted_oracle):
    """E23: locate each residual anonymous class term in original source premises.

    This is a source-presence and OWL schema-shape audit, not a complete rule
    provenance proof. BNode identifiers are never emitted.
    """
    from rdflib.namespace import OWL
    if not original_types.issubset(full_types) or not restricted_oracle.issubset(full_types):
        raise ValueError("source premise sets not contained in full inference")
    residual = (full_types-original_types)-restricted_oracle
    byclass=Counter(c for s,p,c in residual if p == RDF.type and isinstance(c,BNode))
    groups=Counter()
    original_present=0
    source_typed_restriction=0
    source_on_property=0
    inferred_only=0
    for term,count in byclass.items():
        outgoing=list(owner_graph.triples((term,None,None)))
        incoming=list(owner_graph.triples((None,None,term)))
        has_source=bool(outgoing or incoming)
        if has_source:original_present+=1
        else:inferred_only+=1
        restriction=(term,RDF.type,OWL.Restriction) in owner_graph
        on_property=any(owner_graph.triples((term,OWL.onProperty,None)))
        if restriction:source_typed_restriction+=1
        if on_property:source_on_property+=1
        shape=(
            "original_source_present" if has_source else "not_in_original_source",
            "direct_source_restriction" if restriction else "not_direct_source_restriction",
            "direct_source_onProperty" if on_property else "no_direct_source_onProperty",
        )
        groups[shape]+=count
    if sum(groups.values())!=sum(byclass.values()):
        raise ValueError("source anonymous class provenance census mismatch")
    return {
        "anonymous_class_terms_total":len(byclass),
        "anonymous_residual_type_statements_total":sum(byclass.values()),
        "anonymous_class_terms_present_in_original_owner_graph":original_present,
        "anonymous_class_terms_absent_from_original_owner_graph":inferred_only,
        "direct_source_owl_restriction_class_terms":source_typed_restriction,
        "direct_source_owl_onProperty_class_terms":source_on_property,
        "structural_groups":[
            {"original_source_presence":shape[0],
             "owl_restriction_declaration":shape[1],
             "owl_onProperty_declaration":shape[2],
             "residual_original_node_type_statements":groups[shape]}
            for shape in sorted(groups)
        ],
        "blank_node_labels_exported":False,
        "not_a_complete_OWL_inference_rule_proof":True,
        "source_biological_validation":False,
        "official_NIH_scored":False,
    }


def original_anonymous_constructor_fingerprint(owner_graph, original_types, full_types, restricted_oracle):
    """E24 original-graph anonymous term constructor fingerprint, not rule proof.

    Group by authored local RDF/OWL shape. Never export parser-generated BNode
    labels, original source rows or a claimed stable anonymous-class crosswalk.
    """
    from rdflib.namespace import OWL
    if not original_types <= full_types or not restricted_oracle <= full_types:
        raise ValueError("original or RDFS closure boundary changed")
    residual=(full_types-original_types)-restricted_oracle
    instances=Counter(c for s,p,c in residual if p==RDF.type and isinstance(c,BNode))
    patterns=Counter()
    counts=Counter()
    for cls,n in instances.items():
        # The input graph is original authored OWL/RDF; the materialized
        # full closure MUST NOT be used as evidence of original declarations.
        outgoing=set(p for _,p,_ in owner_graph.triples((cls,None,None)))
        incoming=set(p for _,p,_ in owner_graph.triples((None,None,cls)))
        marks={
            "restriction":(cls,RDF.type,OWL.Restriction) in owner_graph,
            "onProperty":OWL.onProperty in outgoing,
            "someValuesFrom":OWL.someValuesFrom in outgoing,
            "allValuesFrom":OWL.allValuesFrom in outgoing,
            "hasValue":OWL.hasValue in outgoing,
            "intersectionOf":OWL.intersectionOf in outgoing,
            "unionOf":OWL.unionOf in outgoing,
            "complementOf":OWL.complementOf in outgoing,
            "oneOf":OWL.oneOf in outgoing,
            "equivalentClass":OWL.equivalentClass in outgoing or OWL.equivalentClass in incoming,
            "subClassOf":RDFS.subClassOf in outgoing or RDFS.subClassOf in incoming,
            "rdfListMember":RDF.first in outgoing or RDF.rest in outgoing,
            "rdfListReference":RDF.first in incoming or RDF.rest in incoming,
            "sourceTermSeen":bool(outgoing or incoming),
        }
        sig=tuple(k for k in sorted(marks) if marks[k])
        patterns[sig]+=1
        counts[sig]+=n
    if sum(counts.values())!=sum(instances.values()):
        raise ValueError("authored constructor group accounting diverged")
    return {
        "original_anonymous_class_term_count":len(instances),
        "original_anonymous_type_statement_count":sum(instances.values()),
        "source_constructor_profiles":[
            {"original_author_predicate_features":list(sig),
             "anonymous_class_term_count":patterns[sig],
             "residual_original_node_type_statements":counts[sig]}
            for sig in sorted(patterns)
        ],
        "bnode_identifiers_or_raw_owner_triples_exported":False,
        "original_author_graph_only":True,
        "constructors_not_causal_OWL_derivation_proof":True,
        "official_NIH_scored":False,
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
    result["E22_residual_type_class_inventory"] = residual_type_class_inventory(
        source_types,all_types,witness)
    result["E23_original_anonymous_class_premises"] = original_anonymous_class_premise_census(
        src,source_types,all_types,witness)
    result["E24_anonymous_constructor_fingerprint"] = original_anonymous_constructor_fingerprint(
        src,source_types,all_types,witness)
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
