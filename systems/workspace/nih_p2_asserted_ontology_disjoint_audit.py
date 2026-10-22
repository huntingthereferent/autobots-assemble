"""Independent asserted-disjointness boundary on the pinned OBO source graph.

This is an *asserted ABox conflict scan*, NOT complete OWL satisfiability or
consistency verification. Positive fixture is synthetically added separately,
and must never be attributed to original source ontology content.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json

from rdflib import Graph, RDF, OWL, URIRef
from . import nih_phase2_external_obo_graph_trial as source

SCHEMA = "nih-p2-obo-asserted-disjointness-boundary-v1"
MAX_AXIOMS = 10000


def disjoint_pairs(graph):
    pairs = sorted({
        tuple(sorted((str(a), str(b))))
        for a, b in graph.subject_objects(OWL.disjointWith)
        if isinstance(a, URIRef) and isinstance(b, URIRef) and a != b
    })
    if not pairs or len(pairs) > MAX_AXIOMS:
        raise ValueError("source original disjoint axioms unavailable/out of bound")
    return pairs


def asserted_conflicts(graph, pairs):
    """Explicit same-individual rdf:type assertions only, no OWL entailment."""
    classes = defaultdict(set)
    for individual, klass in graph.subject_objects(RDF.type):
        if isinstance(individual, URIRef) and isinstance(klass, URIRef):
            classes[str(individual)].add(str(klass))
    # independent symmetric scan restricted to original asserted rdf:type.
    conflicts = sorted({
        (individual, a, b)
        for individual, types in classes.items()
        for a, b in pairs if a in types and b in types
    })
    return conflicts


def independently_scan(graph):
    """A distinct exact-triple join on disjoint pairs (no asserted_conflicts call)."""
    output = set()
    for a, b in graph.subject_objects(OWL.disjointWith):
        if not isinstance(a, URIRef) or not isinstance(b, URIRef) or a == b:
            continue
        for individual in graph.subjects(RDF.type, a):
            if isinstance(individual, URIRef) and (individual, RDF.type, b) in graph:
                aa, bb = sorted((str(a), str(b)))
                output.add((str(individual), aa, bb))
    return sorted(output)


def examine(graph):
    if not isinstance(graph, Graph):
        raise ValueError("RDFLib source graph required")
    pairs = disjoint_pairs(graph)
    x = asserted_conflicts(graph, pairs)
    y = independently_scan(graph)
    if x != y:
        raise ValueError("independent original asserted-class conflict join disagrees")
    first_a, first_b = pairs[0]
    # Make exactly one local hypothetical contradiction; do NOT mutate original.
    fixture = Graph()
    dummy = URIRef("urn:nih-p2:synthetic-disjoint-conflict")
    fixture.add((URIRef(first_a), OWL.disjointWith, URIRef(first_b)))
    fixture.add((dummy, RDF.type, URIRef(first_a)))
    fixture.add((dummy, RDF.type, URIRef(first_b)))
    f = asserted_conflicts(fixture, disjoint_pairs(fixture))
    if f != [(str(dummy), first_a, first_b)] or independently_scan(fixture) != f:
        raise ValueError("separate deliberate inconsistency control failed")
    return {
        "schema": SCHEMA,
        "original_graph_triple_count": len(graph),
        "original_explicit_disjoint_pairs": len(pairs),
        "original_asserted_type_conflict_count": len(x),
        "original_asserted_conflict_witnesses": [
            {"individual": who, "first_class": a, "second_class": b}
            for who, a, b in x[:20]
        ],
        "asserted_conflict_receipts_truncated": len(x) > 20,
        "separate_synthetic_control_conflicts": len(f),
        "synthetic_control_in_original_graph": False,
        "independent_exact_triple_join_agreements": True,
        "inferred_owl_conflicts_checked": False,
        "unsatisfiable_class_count": "NOT_MEASURED",
        "complete_owl_dl_consistency_checked": False,
        "clinical_implications_inferred": False,
        "historical_relation_edge_times_authenticated": False,
        "official_NIH_benchmark": False,
        "original_W13_modified": False,
    }


def execute(files):
    graph, receipts, edges = source.admit_sources(files)
    result = examine(graph)
    result["source_commit"] = source.COMMIT
    result["original_whole_file_source_receipts"] = receipts
    result["original_hierarchy_edge_count"] = len(edges)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ro-base", required=True, type=Path)
    parser.add_argument("--core", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = execute({"ro-base.owl": args.ro_base, "core.owl": args.core})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "asserted_disjoint_axioms":result["original_explicit_disjoint_pairs"],
        "asserted_source_conflicts":result["original_asserted_type_conflict_count"],
        "injected_fixture_conflict":result["separate_synthetic_control_conflicts"],
        "full_OWL_consistency":"NOT_MEASURED",
    }, sort_keys=True))


if __name__=="__main__":
    main()
