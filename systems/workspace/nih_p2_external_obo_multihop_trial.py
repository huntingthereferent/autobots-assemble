"""Direct original OBO external graph trial: bounded A/B multihop vs RDFLib SPARQL+.

Re-execute the same fixed original external ontology benchmark, including
its *actual misses*; do not invent a new easier benchmark. Every new positive
must contain an original URI-by-URI provenance path verified against a
separately reconstructed RDF source-edge index. Compare all 402 x 3-cutoff
cases to the independent SPARQL+ reasoner; preserve any remaining mismatch.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from . import nih_phase2_external_obo_graph_trial as original
from . import ab_finite_original_uri_multihop as traversal

SCHEMA="nih-p2-original-obo-finite-multihop-v1"
HOP_LIMIT=6


def corroborate(path, originals, *, known, target):
    edges=path["source_witness_edges"]
    nodes=path["source_witness_uris"]
    if not path["path_exists"]:
        if edges or nodes or path["path_hops"] is not None:
            raise ValueError("negative source result promoted to positive receipt")
        return True
    if len(edges)!=path["path_hops"] or len(nodes)!=len(edges)+1:
        raise ValueError("original-source path length inconsistent")
    if nodes[0]!=path["start"] or nodes[-1]!=path["end"]:
        raise ValueError("original-source endpoint mismatch")
    for i,edge in enumerate(edges):
        exact=(edge["source_subject"],edge["source_predicate"],
               edge["source_object"])
        if exact!=(nodes[i],path["predicate"],nodes[i+1]):
            raise ValueError("source edge directions or predicate changed")
        key=original.digest("|".join(exact).encode("utf8"))
        if edge["source_relation_sha256"]!=key:
            raise ValueError("unrecognized source relationship SHA-256")
        if key not in originals:
            raise ValueError("newly constructed relationship not present in original")
        source=originals[key]
        if (source["s"],source["p"],source["o"])!=exact:
            raise ValueError("false original relationship")
        if (source["known_at"]!=edge["hypothetical_known_at"] or
                source["valid_from"]!=edge["hypothetical_valid_from"] or
                source["valid_to"]!=edge["hypothetical_valid_to"]):
            raise ValueError("original source time overlay changed")
        if not (source["known_at"]<=known and
                source["valid_from"]<=target<source["valid_to"]):
            raise ValueError("path uses future-unavailable or expired original source")
    if len(set(nodes))!=len(nodes):
        raise ValueError("source witness includes repeated URI/cycle")
    return True


def execute(files):
    # Keep previous external 402-case benchmark and its stronger RDF reasoner
    # as the fixed independent oracle, not as hand-authored easier targets.
    control=original.execute(files)
    g,source_hashes,edges=original.admit_sources(files)
    rows=original.overlay(edges)
    index={r["source_relation_sha256"]:r for r in rows}
    if len(index)!=len(rows):
        raise ValueError("original graph edge keys not distinct")
    answers=[]
    for case in control["cases"]:
        result=traversal.traverse(
            rows,start=case["source_subject"],end=case["source_object"],
            predicate=case["source_predicate"],
            known_at=case["test_known_at_synthetic"],
            target_at=case["test_target_at_synthetic"],max_hops=HOP_LIMIT)
        corroborate(result,index,
            known=case["test_known_at_synthetic"],
            target=case["test_target_at_synthetic"])
        expected=case["independent_RDF_temporal_property_path_plus"]
        answers.append({
            "source_domain":case["source_domain"],
            "source_path_category":case["source_path_category"],
            "original_subject_uri":case["source_subject"],
            "original_object_uri":case["source_object"],
            "source_predicate_uri":case["source_predicate"],
            "hypothetical_known_at":case["test_known_at_synthetic"],
            "hypothetical_target_at":case["test_target_at_synthetic"],
            "old_AB_exact_two_hop":case["AB_two_hop"],
            "new_AB_finite_multihop":result["path_exists"],
            "independent_RDFLib_SPARQL_plus_temporal":expected,
            "independent_static_SPARQL_plus":case["full_external_graph_static_RDF_property_path_plus"],
            "agrees_with_independent_temporal_SPARQL":
                result["path_exists"]==expected,
            "path_hops":result["path_hops"],
            "exhaustive_within_declared_6_hop_bound":True,
            "source_path_uri_witness":result["source_witness_uris"],
            "original_source_edge_receipts":result["source_witness_edges"],
            "static_reachability_without_time":case["full_external_graph_static_RDF_property_path_plus"],
            "original_historical_edge_publication_authenticated":False,
        })
    regained=[
        x for x in answers if x["source_path_category"]=="three-hop-without-shorter"
        and x["independent_RDFLib_SPARQL_plus_temporal"]
        and not x["old_AB_exact_two_hop"] and x["new_AB_finite_multihop"]
    ]
    last_cutoff=original.CUTOFFS[-1]
    last=[x for x in answers if x["hypothetical_known_at"]==last_cutoff]
    still=[x for x in answers if not x["agrees_with_independent_temporal_SPARQL"]]
    if len(answers)!=control["scored_cases"]:
        raise ValueError("external source benchmark silently changed size")
    return {
        "schema":SCHEMA,
        "original_external_source_commit":original.COMMIT,
        "original_source_whole_sha256":source_hashes,
        "original_source_rdf_triples":len(g),
        "original_hierarchy_edges":len(edges),
        "source_original_rdf_bodies_copied":False,
        "source_original_publication_clocks_known":False,
        "time_labels_are_synthetic":True,
        "original_external_benchmark_cases":control["scored_cases"],
        "original_static_future_leakage_cases":control["static_future_leakage_cases"],
        "original_two_hop_exact_oracle_mismatches":control["scored_cases"]-
            control["AB_equals_independent_exact_two_hop_cases"],
        "previously_exposed_three_hop_only_static_reachable_misses":
            control["static_reasoner_reachable_three_hop_AB_misses"],
        "finite_hop_bound":HOP_LIMIT,
        "recovered_real_source_longer_temporal_paths":len(regained),
        "recovered_real_source_longer_temporal_paths_at_latest_cutoff":
            sum(x["hypothetical_known_at"]==last_cutoff for x in regained),
        "latest_cutoff_source_cases":len(last),
        "latest_cutoff_multihop_temporal_vs_SPARQL_matches":
            sum(x["agrees_with_independent_temporal_SPARQL"] for x in last),
        "all_multihop_temporal_vs_SPARQL_matches":
            sum(x["agrees_with_independent_temporal_SPARQL"] for x in answers),
        "unresolved_or_out_of_scope_spaql_reachability_cases":len(still),
        "unresolved_source_cases":[{
            "start":x["original_subject_uri"],"end":x["original_object_uri"],
            "test_date":x["hypothetical_known_at"],
            "source_path_category":x["source_path_category"],
        } for x in still],
        "witnessed_path_length_histogram":dict(Counter(
            str(x["path_hops"]) for x in answers if x["new_AB_finite_multihop"])),
        "original_W13_emitted_temporal_python_modified":False,
        "original_W13_journal_modified":False,
        "World48_required":False,
        "full_OWL_reasoning_implemented":False,
        "real_clinical_temporal_validity_inferred":False,
        "official_NIH_Phase2_benchmark_reproduced":False,
        "cases":answers,
    }


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ro-base",required=True,type=Path)
    a.add_argument("--core",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    opts=a.parse_args()
    result=execute({"ro-base.owl":opts.ro_base,"core.owl":opts.core})
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "cases":result["original_external_benchmark_cases"],
        "external_longer_source_paths_recovered":
            result["recovered_real_source_longer_temporal_paths"],
        "latest_cutoff_longer_source_paths_recovered":
            result["recovered_real_source_longer_temporal_paths_at_latest_cutoff"],
        "multihop_matches_independent_SPARQL":
            result["all_multihop_temporal_vs_SPARQL_matches"],
        "remaining_path_mismatches":
            result["unresolved_or_out_of_scope_spaql_reachability_cases"],
        "original_W13_modified":False,
        "NIH_Phase2_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
