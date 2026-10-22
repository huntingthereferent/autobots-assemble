"""Pinned original OBO RDFS-subclass inherited disjointness inspection.

Checks an explicit finite RDFS subclass expansion of URI-typed individuals,
not general OWL DL satisfiability or materialized inferred existential class
assertions. One source-owned path expansion and an independent RDFLib
transitive-objects oracle must agree. Original ontology and deliberately
inconsistent controls stay separate.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
import json

from rdflib import Graph, OWL, RDF, RDFS, URIRef

from . import nih_phase2_external_obo_graph_trial as source
from . import nih_p2_asserted_ontology_disjoint_audit as direct

SCHEMA = "nih-p2-obo-original-inherited-rdfs-disjointness/v1"
MAX_DIRECT_SUBCLASS_EDGES = 5000
MAX_NAMED_TYPE_ASSERTIONS = 20000
MAX_EXPANSIONS = 300000


def index_subclasses(graph):
    """Only direct named-class rdfs:subClassOf edges, child -> parent."""
    relations=defaultdict(set)
    edges=set()
    for child, parent in graph.subject_objects(RDFS.subClassOf):
        if not isinstance(child, URIRef) or not isinstance(parent, URIRef):
            continue
        a,b=str(child),str(parent)
        if a==b:continue
        relations[a].add(b)
        edges.add((a,b))
    if len(edges)>MAX_DIRECT_SUBCLASS_EDGES:
        raise ValueError("source named subclass graph exceeds bound")
    return relations, edges


def up_to_root(root, index, *, remaining):
    """Finite BFS: only explicit named classes, never inferred OWL axioms."""
    found={root}
    queue=deque([root])
    work=0
    while queue:
        node=queue.popleft()
        for parent in sorted(index.get(node,())):
            work+=1
            if work>remaining:
                raise ValueError("bounded source subclass traversal exhausted")
            if parent not in found:
                found.add(parent)
                queue.append(parent)
    return found,work


def original_named_type_assertions(graph):
    result=set()
    for entity, klass in graph.subject_objects(RDF.type):
        if isinstance(entity, URIRef) and isinstance(klass, URIRef):
            result.add((str(entity),str(klass)))
    if len(result)>MAX_NAMED_TYPE_ASSERTIONS:
        raise ValueError("named original assertions exceed budget")
    return sorted(result)


def examine(graph):
    if not isinstance(graph, Graph):
        raise ValueError("source RDF graph required")
    pairs=direct.disjoint_pairs(graph)
    edges_by_child, edges=index_subclasses(graph)
    asserted=original_named_type_assertions(graph)
    by_entity=defaultdict(set)
    for entity,klass in asserted:
        by_entity[entity].add(klass)
    class_set={klass for _,klass in asserted}
    memo={}
    used=0
    for klass in sorted(class_set):
        reach,count=up_to_root(klass,edges_by_child,remaining=MAX_EXPANSIONS-used)
        used+=count
        memo[klass]=reach
    expanded={}
    new_count=0
    for entity,raw_types in by_entity.items():
        actual=set().union(*(memo[t] for t in raw_types))
        expanded[entity]=actual
        new_count+=len(actual-raw_types)
    computed=sorted((entity,a,b)
                    for entity,t in expanded.items()
                    for a,b in pairs if a in t and b in t)
    # Separate RDFLib's native property-traversal implementation over original
    # source axioms; never read the constructed computed ancestor results.
    oracle={}
    for klass in sorted(class_set):
        oracle[klass]={str(v) for v in
                       graph.transitive_objects(URIRef(klass),RDFS.subClassOf)
                       if isinstance(v,URIRef)}
    independent=sorted((entity,a,b)
                       for entity,raw_types in by_entity.items()
                       for a,b in pairs
                       if a in set().union(*(oracle[t] for t in raw_types))
                       and b in set().union(*(oracle[t] for t in raw_types)))
    if computed!=independent:
        raise ValueError("independent RDFLib original subclass oracle disagrees")
    direct_count=len(direct.asserted_conflicts(graph,pairs))
    if len(computed)<direct_count:
        raise ValueError("subclass expansion lost directly asserted conflict")
    return {
        "schema":SCHEMA,
        "source_rdf_triples":len(graph),
        "original_explicit_disjoint_pairs":len(pairs),
        "original_named_subclass_edges":len(edges),
        "original_named_type_assertions":len(asserted),
        "original_named_typed_individuals":len(by_entity),
        "additional_rdfs_superclass_type_bindings":new_count,
        "direct_only_asserted_disjointness_conflicts":direct_count,
        "source_inherited_rdfs_disjointness_conflicts":len(computed),
        "conflict_receipts":[{"subject":e,"source_or_inherited_a":a,
                              "source_or_inherited_b":b}
                             for e,a,b in computed[:40]],
        "conflict_receipts_truncated":len(computed)>40,
        "independent_RDFLib_subclass_oracle_agreement":True,
        "inherited_source_assertions_are_clinical_truth":False,
        "synthetic_fixture_added_to_original":False,
        "blank_node_class_restrictions_reasoned_over":False,
        "owl_equivalentClass_and_inverse_rules_processed":False,
        "full_OWL_RL_materialization_claimed":False,
        "unsatisfiable_class_count":"NOT_MEASURED",
        "full_OWL_DL_consistency_verified":False,
        "original_history_known_at_authenticated":False,
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
    }


def execute(files):
    graph,receipts,edges=source.admit_sources(files)
    result=examine(graph)
    result["original_external_ontology_source_commit"]=source.COMMIT
    result["original_source_file_receipts"]=receipts
    result["original_hierarchy_edge_count"]=len(edges)
    return result


def main():
    p=argparse.ArgumentParser()
    for opt in ("ro-base","core","output"):
        p.add_argument("--"+opt,required=True,type=Path)
    a=p.parse_args()
    result=execute({"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "original_named_subclass_edges":result["original_named_subclass_edges"],
        "additional_inherited_class_assertions":result["additional_rdfs_superclass_type_bindings"],
        "direct_disjointness_conflicts":result["direct_only_asserted_disjointness_conflicts"],
        "inherited_disjointness_conflicts":result["source_inherited_rdfs_disjointness_conflicts"],
        "independent_RDFLib_oracle_matches":result["independent_RDFLib_subclass_oracle_agreement"],
        "full_OWL_consistency":"NOT_MEASURED"},sort_keys=True))


if __name__=="__main__":
    main()
