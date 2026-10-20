"""Direct Phase 2 practice reproduction with source-revision and bounded RDF inference.

Replays unchanged W13 original 13 questions and the separately tested source
chain; upgrades only two measured gaps. Neither answer is read from the gold
task: the revision relation must inspect source observations and RDF must
produce & reparse a genuine inferred triple. Two independent test oracles
validate 160 new revision and 160 multi-domain RDF movements.
"""
from __future__ import annotations

import argparse
from datetime import date,timedelta
import json
from pathlib import Path
from random import Random

from rdflib import Graph,URIRef

from . import nih_phase2_direct_reproduction as original
from . import nih_phase2_time_respecting_chain_trial as parent
from . import ab_source_revision_relation as revisions
from . import ab_bounded_rdf_source_composition as graph_inference

SCHEMA="nih-phase2-direct-revision-and-rdf-composition-trial/v1"
SEED=26021
N=160


def independent_revision_oracle(rows,*, subject,claim,known,target):
    """Standalone pairwise relation evaluator; does not call revision module."""
    old=[a for a in rows if a["predicate"]=="supports-claim"
         and a["subject"]==subject and a["object"]==claim
         and a["valid_from"]<=target<a["valid_to"] and a["known_at"]<=known]
    new=[b for b in rows if b["predicate"]=="retracts-claim"
         and b["subject"]==subject and b["object"]==claim
         and b["valid_from"]<=target<b["valid_to"] and b["known_at"]<=known]
    if not old:return "NOT_AVAILABLE"
    for o in old:
        if any(n["known_at"]==o["known_at"] for n in new)
           and not any(n["known_at"]>o["known_at"] for n in new):
            return "AMBIGUOUS"
    if any(not any(n["known_at"]>o["known_at"] for n in new) for o in old):
        return "SUPPORTED"
    return "SUPERSEDED"


def new_revision_case(i,rng):
    variation=i%8
    support_day=rng.randrange(1,7)
    revised_day=support_day+rng.randrange(1,7)
    def d(n):
        return (date(2026,1,1)+timedelta(days=n)).isoformat()
    subject="fictional-paper"
    claim="claim-"+str(rng.randrange(1000,9999))
    old=original.obs(f"support-{i}","supports-claim",claim,
        d(support_day),d(31),d(support_day),source="synthetic-journal",
        subject=subject)
    new=original.obs(f"revision-{i}","retracts-claim",claim,
        d(revised_day),d(31),d(revised_day),source="synthetic-correction",
        subject=subject)
    if variation==1:
        new["object"]="unrelated-claim"
    if variation==2:
        new["known_at"]=d(25)
    if variation==3:
        new["known_at"]=old["known_at"]
    if variation==4:
        new["subject"]="unrelated-paper"
    if variation==5:
        new["object"]="different-claim"
    if variation==6:
        old["object"]="different-claim"
    if variation==7:
        new["valid_from"]=d(25)
    rows=[old,new]
    rng.shuffle(rows)
    return rows,subject,claim,d(20),d(20)


def original_rdf_oracle(rows,pattern,known,target,subject):
    """Independent brute-force product of source events, NOT graph inference output."""
    candidates=[[r for r in rows if r["predicate"]==stage["predicate"]
                 and r["object"]==stage["object"] and r["subject"]==subject
                 and r["known_at"]<=known and r["valid_from"]<=target]
                for stage in pattern]
    return {
        (a["id"],c["id"]) for a in candidates[0]
        for b in candidates[1] for c in candidates[2]
        if len({a["id"],b["id"],c["id"]})==3
        and a["valid_from"]<b["valid_from"]<c["valid_from"]
    }


def evaluate(*, output_dir:Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    base=parent.run(output_dir=output_dir)
    if (base["original_13_case_scores"]!={"W13":8,"static":6,"cases":13}
        or base["with_bounded_generic_source_chain"]["passed"]!=11
        or base["unseen_generated"]["verified_by_independent_cartesian_oracle"]!=160):
        raise ValueError("prior actual W13/chain source benchmark changed")
    result=[]
    for case in base["original_13_case_results"]:
        updated=dict(case)
        updated["new_causal_claim"]=False
        task=case["task"]
        if task=="superseded-claim-not-current":
            r=revisions.observe(
                original.BIOMED, subject="fictional-paper",claim_object="claim-z",
                support_predicate="supports-claim",revision_predicate="retracts-claim",
                known_at="2026-01-12",target_at="2026-01-12")
            if (r["source_statement_ids_still_in_history"]!=["claim-original"]
                or r["source_revision_ids_still_in_history"]!=["claim-correction"]):
                raise ValueError("original revision source history was lost")
            updated["new_source_chain_answer"]=r["currently_supported"]
            updated["new_answer_supported"]=r["currently_supported"] is not None
            updated["evidence"]={"bounded_source_revision":r,
                                  "original_W13_still_incorrect":True}
        elif task=="rdf-property-chain-inference":
            r=graph_inference.infer(
                original.BIOMED,parent.STAGES,
                known_at="2026-01-11",target_at="2026-01-11",
                subject="fictional-cohort")
            graph=Graph().parse(data=r["rdf_graph_ntriples"],format="nt")
            if r["new_triple_count"]!=1 or len(graph)!=r["entailed_graph_triple_count"]:
                raise ValueError("actual RDF composition did not add exactly one triple")
            needed=(
                "therapy-alpha","therapy-beta"
            )
            oracle=original_rdf_oracle(
                original.BIOMED,parent.STAGES,"2026-01-11",
                "2026-01-11","fictional-cohort")
            if oracle!={needed}:
                raise ValueError("independent source brute-force path oracle differs")
            triple=(
                str(graph_inference.EX["event-"+needed[0]]),
                str(graph_inference.EX.observedBefore),
                str(graph_inference.EX["event-"+needed[1]]),
            )
            if triple not in r["actual_new_rdf_triples"] or not (
                URIRef(triple[0]),URIRef(triple[1]),URIRef(triple[2])
            ) in graph:
                raise ValueError("RDF inferred triple not actually present")
            updated["new_source_chain_answer"]=r["inference_exists"]
            updated["new_answer_supported"]=True
            updated["evidence"]={
                "actual_rdf_inferred_triples":r["actual_new_rdf_triples"],
                "original_evidence_sources":r["original_source_witnesses"],
                "graph_triple_count":r["entailed_graph_triple_count"],
                "declared_composition_rule":r["declared_rule"],
                "full_OWL_reasoning_claimed":False,
                "original_W13_still_lacks_RDF_output":True,
            }
        updated["new_pass"]=(
            updated["new_answer_supported"] and
            updated["new_source_chain_answer"]==case["expected_answer"]
        )
        result.append(updated)
    rng=Random(SEED)
    revisions_tests=[]
    for i in range(N):
        rows,subject,claim,known,target=new_revision_case(i,rng)
        out=revisions.observe(rows,subject=subject,claim_object=claim,
            support_predicate="supports-claim",revision_predicate="retracts-claim",
            known_at=known,target_at=target)
        actual=out["outcome"]
        expected=independent_revision_oracle(rows,subject=subject,claim=claim,
                                              known=known,target=target)
        if actual!=expected:raise ValueError("independent source revision oracle mismatch")
        revisions_tests.append({
            "case":i,"outcome":actual,"independent_outcome":expected,
            "source_history_retained":out["not_silently_deleted"],
        })
    rng=Random(SEED+1)
    rdf_tests=[]
    for i in range(N):
        domain,rows,pattern,known,target,subject=parent.generated_case(i,rng)
        actual=graph_inference.infer(rows,pattern,known_at=known,
            target_at=target,subject=subject)
        triples=Graph().parse(data=actual["rdf_graph_ntriples"],format="nt")
        oracle=original_rdf_oracle(rows,pattern,known,target,subject)
        actual_pairs={
            (p.split("/event-")[-1],o.split("/event-")[-1])
            for p,_,o in actual["actual_new_rdf_triples"]
        }
        if actual_pairs!=oracle or bool(oracle)!=actual["inference_exists"]:
            raise ValueError("actual RDF graph triples fail independent source-product oracle")
        if len(triples)!=actual["entailed_graph_triple_count"]:
            raise ValueError("RDF serialized graph does not include reported triples")
        rdf_tests.append({
            "case":i,"domain":domain,"matched_paths":len(oracle),
            "inference":actual["inference_exists"],
            "independent_inference":bool(oracle),
        })
    succeeded=sum(x["new_pass"] for x in result)
    if succeeded>13:raise ValueError("invalid practice task count")
    return {
        "schema":SCHEMA,
        "source":"fictional population-level practice test only",
        "original_W13":base["original_13_case_scores"],
        "source_chain_only_pass":base["with_bounded_generic_source_chain"]["passed"],
        "source_revision_and_RDF_composition_pass":succeeded,
        "source_revision_and_RDF_composition_fail":len(result)-succeeded,
        "practice_question_count":len(result),
        "questions":result,
        "unseen_revision_cases":{
            "cases":len(revisions_tests),
            "independent_oracle_cases":len(revisions_tests),
            "outcomes":{k:sum(x["outcome"]==k for x in revisions_tests)
                        for k in ("SUPPORTED","SUPERSEDED","AMBIGUOUS","NOT_AVAILABLE")},
            "rows":revisions_tests,
        },
        "unseen_RDF_cases":{
            "cases":len(rdf_tests),
            "independent_oracle_cases":len(rdf_tests),
            "positive":sum(x["inference"] for x in rdf_tests),
            "negative":sum(not x["inference"] for x in rdf_tests),
            "rows":rdf_tests,
        },
        "real_OWL_property_chain_axiom_engine_implemented":False,
        "OWL_inconsistency_check_implemented":False,
        "clinical_effectiveness_inferred":False,
        "real_historical_biomedical_KG_data_tested":False,
        "official_NIH_Phase2_shared_benchmark_used":False,
        "official_NIH_Phase2_reproduction_completed":False,
        "original_W13_temporal_python_modified":False,
        "original_W13_journal_modified":False,
        "World48_required":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    a=parser.parse_args()
    out=evaluate(output_dir=a.output_dir)
    (a.output_dir/"nih-phase2-source-revision-rdf.json").write_text(
        json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "original_W13":out["original_W13"],
        "source_chain_only_pass":out["source_chain_only_pass"],
        "augmented_pass":out["source_revision_and_RDF_composition_pass"],
        "augmented_fail":out["source_revision_and_RDF_composition_fail"],
        "revision_unseen":out["unseen_revision_cases"]["outcomes"],
        "rdf_unseen":{
            "positive":out["unseen_RDF_cases"]["positive"],
            "negative":out["unseen_RDF_cases"]["negative"],
        },
        "NIH_Phase2_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
