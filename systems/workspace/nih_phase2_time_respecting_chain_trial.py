"""Phase 2 continuation: direct benchmark + new generic bounded chain operation.

The original W13 Python still runs unchanged in the separate 13-case trial.
Only its three unsupported longitudinal answers are separately constructed
from the same *declared source observations* with evidence path witnesses.
An independently coded Cartesian-product oracle checks each path result;
new generated case orderings are not the original golden examples.
"""
from __future__ import annotations

import argparse
from datetime import date,timedelta
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random

from . import nih_phase2_direct_reproduction as prior
from . import ab_time_respecting_source_chain as chain

SCHEMA="nih-phase2-direct-generic-chain-reproduction/v1"
STAGES=[
    {"predicate":"receives-therapy","object":"alpha"},
    {"predicate":"response","object":"inadequate"},
    {"predicate":"receives-therapy","object":"beta"},
]
SURVEILLANCE_STAGES=[
    {"predicate":"variant-status","object":"variant-a"},
    {"predicate":"signal","object":"rising"},
    {"predicate":"variant-status","object":"variant-b"},
]
SEED=26020
UNSEEN=160


def oracle(rows,stages,known,target,subject=None):
    """Independent exhaustive verifier: full Cartesian product, no tree walker."""
    pool=[
        tuple(r for r in rows if r["predicate"]==stage["predicate"]
              and r["object"]==stage["object"])
        for stage in stages
    ]
    accepted=[]
    for combination in product(*pool):
        if subject is not None and any(r["subject"]!=subject for r in combination):
            continue
        if len(set(r["subject"] for r in combination))!=1:
            continue
        if len(set(r["id"] for r in combination))!=len(combination):
            continue
        if any(r["known_at"]>known or r["valid_from"]>target for r in combination):
            continue
        starts=[r["valid_from"] for r in combination]
        if any(a>=b for a,b in zip(starts,starts[1:])):
            continue
        accepted.append(tuple(r["id"] for r in combination))
    return sorted(accepted)


def independent_check(rows,pattern,known,target,source_report,subject=None):
    expected=oracle(rows,pattern,known,target,subject=subject)
    actual=sorted(tuple(r["evidence_ids"]) for r in source_report["witnesses"])
    if actual!=expected:
        raise ValueError("independent Cartesian oracle disagrees with chain source paths")
    if source_report["path_exists"]!=bool(expected):
        raise ValueError("source-chain path answer disagrees with independent oracle")
    if any(tuple(sorted(w["event_starts"]))!=tuple(w["event_starts"])
           for w in source_report["witnesses"]):
        raise ValueError("source event movement not ordered")
    if source_report["causal_conclusion"] is not False:
        raise ValueError("source path cannot promote causality")
    return {"expected_path_ids":[list(x) for x in expected],
            "cross_checked":True}


def _d(i):
    return (date(2026,1,1)+timedelta(days=i)).isoformat()


def generated_case(index,rng):
    """Novel variable subjects, dates, evidence availability and orderings."""
    key="surveillance" if index%2 else "care"
    pattern=SURVEILLANCE_STAGES if key=="surveillance" else STAGES
    subject="fictional-region" if key=="surveillance" else "fictional-cohort"
    other="other-region" if key=="surveillance" else "other-cohort"
    stamps=[rng.randrange(1,20) for _ in range(3)]
    knowns=[min(26,stamps[i]+rng.randrange(0,8)) for i in range(3)]
    rows=[]
    for k,(stage,t,seen) in enumerate(zip(pattern,stamps,knowns)):
        rows.append(prior.obs(
            f"generated-{index}-{k}",stage["predicate"],stage["object"],
            _d(t),_d(31),_d(seen),source=f"synthetic-generated-{key}",
            subject=subject))
    # Decoy full path with a separate subject: never join across subjects.
    for k,(stage,t) in enumerate(zip(pattern,(3,6,9))):
        rows.append(prior.obs(
            f"decoy-{index}-{k}",stage["predicate"],stage["object"],
            _d(t),_d(31),_d(t),source=f"synthetic-decoy-{key}",subject=other))
    # Same-token noise cannot create a path by jumping between subjects.
    rows.append(prior.obs(
        f"noise-{index}","irrelevant","neutral",
        _d(rng.randrange(1,20)),_d(31),_d(1),
        source="synthetic-noise",subject=subject))
    rng.shuffle(rows)
    known=_d(rng.randrange(1,30))
    target=_d(rng.randrange(1,30))
    return key,rows,pattern,known,target,subject


def run(*, output_dir:Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    direct=prior.trial(output_dir=output_dir)
    if (direct["scored_cases"]!=13 or direct["native_pass"]!=8
            or direct["native_fail"]!=5
            or direct["phase2_reproduced_in_full"] is not False):
        raise ValueError("original W13 direct baseline unexpectedly changed")
    output=[]
    for item in direct["cases"]:
        task=next(t for t in prior.TASKS if t["id"]==item["task"])
        if task["kind"]=="derived":
            # Use the actual original benchmark's known/target values. These
            # historical events can expire before target, unlike snapshot IDs.
            observed=chain.observe(prior.BIOMED,STAGES,
                known_at=task["known"],target_at=task["target"],
                subject="fictional-cohort")
            checked=independent_check(
                prior.BIOMED,STAGES,task["known"],task["target"],observed,
                subject="fictional-cohort")
            answer=observed["path_exists"]
            supported=True
            provenance={
                "chain_source_schema":observed["schema"],
                "witness_paths":observed["witnesses"],
                "independent_path_ids":checked["expected_path_ids"],
                "original_W13_emitted_Python_still_lacks_this_output":True,
            }
        else:
            answer=item["native_answer"]
            supported=item["native_supported"]
            provenance={
                "source":"unchanged-original-W13-Python" if task["kind"]=="fact"
                         else "native-output-unavailable",
            }
        output.append({
            "task":task["id"],"kind":task["kind"],"expected_answer":task["expected"],
            "original_native_answer":item["native_answer"],
            "new_source_chain_answer":answer,
            "new_answer_supported":supported,
            "new_pass":answer is not None and answer==task["expected"],
            "original_native_pass":item["native_pass"],
            "original_static_pass":item["static_pass"],
            "evidence":provenance,
        })
    rng=Random(SEED)
    unseen=[]
    for i in range(UNSEEN):
        domain,rows,pattern,known,target,subject=generated_case(i,rng)
        witnessed=chain.observe(rows,pattern,
            known_at=known,target_at=target,subject=subject)
        independent=independent_check(
            rows,pattern,known,target,witnessed,subject=subject)
        unseen.append({
            "index":i,"domain":domain,"knowledge_at":known,
            "event_target_at":target,
            "answer":witnessed["path_exists"],
            "independent_answer":bool(independent["expected_path_ids"]),
            "witness_path_ids":[r["evidence_ids"] for r in witnessed["witnesses"]],
        })
    enhanced_pass=sum(r["new_pass"] for r in output)
    by_kind={
        k:{"cases":sum(r["kind"]==k for r in output),
           "original_pass":sum(r["kind"]==k and r["original_native_pass"] for r in output),
           "new_pass":sum(r["kind"]==k and r["new_pass"] for r in output)}
        for k in ("fact","derived","rdf")
    }
    return {
        "schema":SCHEMA,
        "original_engine_sha256":direct["original_engine_sha256"],
        "original_direct_trial_schema":direct["schema"],
        "original_13_case_scores":{"W13":direct["native_pass"],
            "static":direct["static_pass"],"cases":direct["scored_cases"]},
        "with_bounded_generic_source_chain":{"passed":enhanced_pass,
            "cases":len(output),"improved_by":enhanced_pass-direct["native_pass"]},
        "by_kind":by_kind,
        "original_13_case_results":output,
        "unseen_generated":{"seed":SEED,"cases":UNSEEN,
            "verified_by_independent_cartesian_oracle":UNSEEN,
            "positive_cases":sum(x["answer"] for x in unseen),
            "negative_cases":sum(not x["answer"] for x in unseen),
            "source_observations_sha256":sha256(
                json.dumps(unseen,sort_keys=True).encode()).hexdigest(),
            "cases_detail":unseen},
        "longitudinal_observation_supported":True,
        "causal_therapy_change_inferred":False,
        "biomedical_OWL_property_chain_supported":False,
        "research_evidence_supersession_supported":False,
        "clinical_event_valid_at_authenticated":False,
        "original_native_W13_engine_changed":False,
        "original_W13_journal_modified":False,
        "World48_required":False,
        "official_Phase2_shared_dataset_used":False,
        "Phase2_fully_reproduced":False,
        "source_mode":"fictional-synthetic-population-level",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    report=run(output_dir=a.output_dir)
    f=a.output_dir/"nih-phase2-time-respecting-chain.json"
    f.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "original":report["original_13_case_scores"],
        "augmented":report["with_bounded_generic_source_chain"],
        "by_kind":report["by_kind"],
        "unseen":{
            k:v for k,v in report["unseen_generated"].items()
            if k!="cases_detail"},
        "Phase2_fully_reproduced":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
