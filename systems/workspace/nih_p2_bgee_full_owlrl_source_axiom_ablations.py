"""E17: test four original ontology premise removals using complete graph OWL RL.

Separate from finite selected-rule Jena ablations. Alternative source schema
paths may reintroduce logical consequences; retain any differences as evidence.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from rdflib import Graph

from . import nih_p2_bgee_cross_engine_jena as gate
from . import nih_p2_bgee_jena_four_rule_source_comparison as four
from . import nih_p2_bgee_full_owlrl_source_comparison as profile
from . import nih_p2_bgee_exhaustive_sharded_owlrl as digest

SCHEMA="nih-p2-lane-c-four-full-profile-source-ablations-v1"
SOURCE_GRAPH_SIZE=34181
SOURCE_EDGES=25027
MAX_CLOSURE=1800000

def independent_copy_without(original, axiom):
    if axiom not in original:
        raise ValueError("authenticated original premise absent")
    copied=Graph()
    copied+=original
    copied.remove(axiom)
    if axiom in copied or axiom not in original or len(copied)!=len(original)-1:
        raise ValueError("ablation changed unexpected statements or original source")
    return copied

def categories(rows, original_edges):
    genes={s for s,p,o in original_edges}
    targets={o for s,p,o in original_edges}
    counts=dict(forward=0,forward_genomic=0,reverse=0,reverse_genomic=0)
    for s,p,o in rows:
        if s in genes and o in targets and p==four.bridge.RO_EXPRESSED:
            counts["forward"]+=1
        elif s in genes and o in targets and p==four.GENOMIC:
            counts["forward_genomic"]+=1
        elif s in targets and o in genes and p==four.bridge.RO_EXPRESSES:
            counts["reverse"]+=1
        elif s in targets and o in genes and p==four.GENOMIC:
            counts["reverse_genomic"]+=1
        else:
            raise ValueError("off-scope predicate or direction in consequence set")
    return counts

def difference(expected, observed, source_edges):
    missing=expected-observed
    extra=observed-expected
    return {
        "selected_four_rule_oracle_total":len(expected),
        "general_full_owlrl_observed_total":len(observed),
        "selected_four_rule_expected_by_direction":categories(expected,source_edges),
        "general_full_owlrl_observed_by_direction":categories(observed,source_edges),
        "missing_selected_rule_consequences":len(missing),
        "additional_full_profile_consequences":len(extra),
        "expected_sha256":digest.digest_set(expected),
        "observed_sha256":digest.digest_set(observed),
        "missing_preview_sha256":sorted(sha256("|".join(map(str,t)).encode()).hexdigest() for t in missing)[:12],
        "additional_preview_sha256":sorted(sha256("|".join(map(str,t)).encode()).hexdigest() for t in extra)[:12],
        "equal_scoped_sets":not missing and not extra,
    }

def write(path, data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(data,sort_keys=True,indent=2)+"\n"
    if len(content.encode())>250000:
        raise ValueError("derived-only source-evidence report exceeds cap")
    path.write_text(content,encoding="utf-8")

def run(original, output):
    source=original["full_combined"]
    edges=original["source_edges"]
    axioms=four.original_four_source_axioms(original)
    if len(source)!=SOURCE_GRAPH_SIZE or len(edges)!=SOURCE_EDGES:
        raise ValueError("whole-source frozen input identity/count changed")
    original_hash=digest.digest_set(source)
    report={
        "schema":SCHEMA,
        "status":"STARTED_NOT_VERIFIED",
        "original_source_graph_triples":len(source),
        "original_source_mapped_edges":len(edges),
        "original_full_graph_sha256":original_hash,
        "original_Bgee_author_data_git_blob":original["archive_receipt"]["complete_original_source_git_blob_sha1"],
        "original_GenEx_author_commit":four.bridge.COMMIT,
        "original_RO_commit":four.bridge.source.COMMIT,
        "full_OWL_DL_consistency_proven":False,
        "second_independent_complete_OWL_RL_engine_run":False,
        "medical_or_NIH_scoring_claim":False,
        "original_W13_or_other_lanes_modified":False,
        "modes":{},
    }
    write(output,report)
    started=time.monotonic()
    try:
        from owlrl import DeductiveClosure,OWLRL_Semantics
        for mode,index in four.PREMISE_MODES.items():
            selected_rule_expected,by_rule=four.independently_infer_with_removed_premise(source,axioms,mode)
            copy=independent_copy_without(source,axioms[index])
            tick=time.monotonic()
            DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(copy)
            seconds=round(time.monotonic()-tick,3)
            if len(copy)>MAX_CLOSURE:
                raise ValueError("general full profile materialization exceeded finite cap")
            observed=profile.select_target(copy,edges)
            result=difference(selected_rule_expected,observed,edges)
            result.update({
                "removed_exact_authenticated_axiom":list(map(str,axioms[index])),
                "original_source_unchanged":True,
                "source_rule_static_oracle_categories":by_rule,
                "full_graph_materialized_triples":len(copy),
                "materialization_wall_seconds":seconds,
            })
            report["modes"][mode]=result
            report["modes_measured"]=len(report["modes"])
            write(output,report)
            if digest.digest_set(source)!=original_hash:
                raise ValueError("the original source graph changed across an ablation")
        report["all_four_full_profile_modes_measured"]=True
        report["all_four_equal_to_selected_rule_controls"]=all(
            x["equal_scoped_sets"] for x in report["modes"].values())
        report["status"]=(
            "VERIFIED_COMPLETED_ABLATIONS_EQUAL_SCOPED_SETS"
            if report["all_four_equal_to_selected_rule_controls"]
            else "VERIFIED_COMPLETED_ABLATIONS_WITH_LOGICAL_DIFFERENCES")
    except Exception as error:
        report["status"]="FAILED_OR_INCOMPLETE_NOT_VERIFIED"
        report["failure_class"]=type(error).__name__
        report["failure_message"]=str(error)[:220]
        raise
    finally:
        report["elapsed_study_wall_seconds"]=round(time.monotonic()-started,3)
        write(output,report)
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",type=Path,required=True)
    for name in ("obda","owl","r2rml","ro-base","core"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    authors={"bgee_v14_genex."+name:getattr(a,name) for name in ("obda","owl","r2rml")}
    original=gate.verified_owner_input(a.archive,authors,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    result=run(original,a.output)
    print(json.dumps({"status":result["status"],"modes":{k:v["general_full_owlrl_observed_total"] for k,v in result["modes"].items()},
                      "source_rule_equals_full_profile":result["all_four_equal_to_selected_rule_controls"],
                      "official_NIH_scored":False},sort_keys=True))

if __name__=="__main__":
    main()
