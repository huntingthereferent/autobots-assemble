"""Lane C E15: full OWL RL on authenticated original Bgee+GenEx+RO combined graph.

Four source-owned property rules have a separate Jena and RDFLib baseline.
This test runs general owlrl on the whole 34,181-statement original combined
graph and checks ALL direction-qualified, mapped-node target conclusions.
Not a second complete OWL RL engine, OWL DL consistency or clinical test.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from rdflib import Graph, URIRef, RDF

from . import nih_p2_bgee_cross_engine_jena as input_gate
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_exhaustive_sharded_owlrl as checksum

SCHEMA = "nih-p2-original-bgee-general-owlrl-four-rule-comparison-v1"
MAX_CLOSURE = 1800000
SOURCE_TRIPLES = 34181
SOURCE_EDGES = 25027
BASELINE = 100108


def select_target(closure, source_edges):
    """Keep also unexpected pairs within real source-mapped node universe."""
    genes = {s for s, p, o in source_edges}
    targets = {o for s, p, o in source_edges}
    forward = {four.bridge.RO_EXPRESSED, four.GENOMIC}
    backward = {four.bridge.RO_EXPRESSES, four.GENOMIC}
    triples = set()
    for predicate in forward | backward:
        for s, o in closure.subject_objects(predicate):
            if not isinstance(s, URIRef) or not isinstance(o, URIRef):
                continue
            if (predicate in forward and s in genes and o in targets) or (
                    predicate in backward and s in targets and o in genes):
                triples.add((s, predicate, o))
    return triples


def compare(observed, expected):
    missing, extra = expected - observed, observed - expected
    evidence = {
        "full_profile_scoped_triples": len(observed),
        "four_source_rule_scoped_triples": len(expected),
        "missing_four_rule_triples": len(missing),
        "additional_full_profile_triples": len(extra),
        "full_profile_target_digest_sha256": checksum.digest_set(observed),
        "source_rule_target_digest_sha256": checksum.digest_set(expected),
        "missing_sha256_first_12": sorted(
            sha256("|".join(map(str, t)).encode()).hexdigest() for t in missing)[:12],
        "additional_sha256_first_12": sorted(
            sha256("|".join(map(str, t)).encode()).hexdigest() for t in extra)[:12],
    }
    evidence["identical_target_sets"] = not missing and not extra
    return evidence


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    contents = json.dumps(data, sort_keys=True, indent=2) + "\n"
    if len(contents.encode("utf-8")) > 300000:
        raise ValueError("derived-only report size exceeded")
    path.write_text(contents, encoding="utf-8")


def run(original, report):
    four.original_four_source_axioms(original)
    graph = original["full_combined"]
    edges = original["source_edges"]
    if len(graph) != SOURCE_TRIPLES or len(edges) != SOURCE_EDGES:
        raise ValueError("original authenticated source baseline changed")
    expected, _ = four.full_static_source_rule_oracle(original)
    if len(expected) != BASELINE:
        raise ValueError("frozen independent four-rule baseline changed")
    report.update({
        "source_original_genex_author_commit": four.bridge.COMMIT,
        "source_original_RO_owner_commit": four.bridge.source.COMMIT,
        "source_original_Bgee_zip_git_blob": original["archive_receipt"][
            "complete_original_source_git_blob_sha1"],
        "source_original_triples": len(graph),
        "source_original_distinct_mapped_edges": len(edges),
        "whole_original_graph_hash_authenticated": True,
        "four_named_source_owner_axioms_verified": True,
        "entire_original_graph_full_profile_attempted": True,
    })
    full = Graph()
    full += graph
    from owlrl import DeductiveClosure, OWLRL_Semantics
    start = time.monotonic()
    DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(full)
    report["owlrl_full_graph_wall_seconds"] = round(time.monotonic() - start, 3)
    report["owlrl_materialized_all_graph_triples"] = len(full)
    if len(full) > MAX_CLOSURE:
        raise ValueError("general OWL RL closure exceeded predeclared triple cap")
    report.update(compare(select_target(full, edges), expected))
    report["owlrl_reported_error_signals"] = sum(
        str(o).endswith("#ErrorMessage") for _, o in full.subject_objects(RDF.type))
    if not report["identical_target_sets"]:
        raise ValueError("full OWL RL and four-rule scoped source baseline differ; retain discrepancy hashes")
    return report


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--archive", type=Path, required=True)
    for name in ("obda", "owl", "r2rml", "ro-base", "core"):
        cli.add_argument("--" + name, type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    report = {
        "schema": SCHEMA,
        "status": "STARTED_NOT_VERIFIED",
        "source_original_rows_or_rdf_redistributed": False,
        "general_owlrl_not_independent_second_complete_profile_engine": True,
        "full_owl_dl_consistency_proven": False,
        "clinical_data_truth_independently_validated": False,
        "official_NIH_Phase2_scored": False,
        "W13_or_other_lanes_modified": False,
    }
    write(args.output, report)
    t0 = time.monotonic()
    try:
        author = {"bgee_v14_genex." + k: getattr(args, k)
                  for k in ("obda", "owl", "r2rml")}
        ro = {"ro-base.owl": args.ro_base, "core.owl": args.core}
        original = input_gate.verified_owner_input(args.archive, author, ro)
        run(original, report)
        report["status"] = "VERIFIED_SCOPED_SET_AGREEMENT"
    except Exception as ex:
        report["status"] = "FAILED_OR_DIFFERENT_NOT_VERIFIED"
        report["failure_category"] = type(ex).__name__
        report["failure_description"] = str(ex)[:200]
        raise
    finally:
        report["total_elapsed_wall_seconds"] = round(time.monotonic() - t0, 3)
        write(args.output, report)
    print(json.dumps({"status": report["status"],
                      "full": report["full_profile_scoped_triples"],
                      "four_rule": report["four_source_rule_scoped_triples"],
                      "materialized": report["owlrl_materialized_all_graph_triples"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
