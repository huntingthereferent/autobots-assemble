"""A mathematically bounded native SP80 observational-quotient test.

The operation is a finite action-labelled right-compatibility check, not an
unproved mapping from native game actions into the separate F3 A/B generators.

Let P retain rows 0..62 of the genuine 64x64 SDK frame. For a fixed, source-
recorded pair of histories h,k whose P endpoints agree, compare exact P at
each identical native-action suffix step, including every returned pour frame.
This is a necessary finite test of right congruence, not global bisimulation.

A separate genuine stage3 same-stage success/failure supplies a mathematical
counterexample to using 'all four cups visibly full' as a reward oracle.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile
import numpy as np

from .arc4_cross_archive_audit import FROZEN as ARC4_ARCHIVES, audit as verify_arc4_source
from .native_sp80_stage3_matched_outlet_audit import (
    JSON_SHA as STAGE3_JSON_SHA, NPZ_SHA as STAGE3_NPZ_SHA,
    audit as verify_stage3_source,
)
from work.arc_like_maze.math import World, align_worlds, rescale_last
from work.arc_like_maze.alignment import discover_alignment

STUDIES=(
    ("arc4-520.zip","original-row63-followup",16),
    ("arc4-521.zip","original-right-middle-transfer",16),
)
STAGE3="arc3-transition-original.zip"
PROJECTION="original 64x64 source rows 0..62, excluding row63 only"
WALL="WALL_NO_ADMITTED_SDK_TO_FINITE_F3_GENERATOR_MAP"

def require(ok,why):
    if not ok:
        raise ValueError("ARC4_MATH_ADMISSION_WALL: "+why)

def projected(frame_stack):
    arr=np.asarray(frame_stack)
    require(arr.ndim==3 and arr.shape[1:]==(64,64),
            "original SDK source frame stack dimensions changed")
    return arr[:,:63,:]

def witness_difference(a,b):
    """Earliest exact projected counterexample, never an inferred internal state."""
    left,right=projected(a),projected(b)
    if len(left)!=len(right):
        return {"kind":"FRAME_STACK_LENGTH_MISMATCH",
                "left_frames":len(left),"right_frames":len(right)}
    where=np.argwhere(left!=right)
    if not len(where):
        return None
    t,y,x=(int(v) for v in where[0])
    return {"kind":"OBSERVATIONAL_RIGHT_CONGRUENCE_COUNTEREXAMPLE",
            "first_returned_frame":t,"original_y":y,"original_x":x,
            "left_source_pixel":int(left[t,y,x]),
            "right_source_pixel":int(right[t,y,x])}

def parse_action(token):
    if token.startswith("6@"):
        x,y=(int(v) for v in token[2:].split(","))
        require(0<=x<64 and 0<=y<64,"invalid original source click")
        return 6,[x,y]
    require(token in {"1","2","3","4","5"},"non-native SDK action token")
    return int(token),None

def word(s):
    return tuple(parse_action(token) for token in s.split())

def sdk_stage4_return(archive,case,witness,step):
    return archive[f"{case}_{witness}_stage4_{step}"]

def compare_study(directory,filename,base,budget):
    with zipfile.ZipFile(directory/filename) as z:
        record=json.loads(z.read(base+".json"))
        raw=z.read(base+".npz")
    require(record["original_sdk_resets"]==budget and
            len(record["native_cases"])==budget and
            len(record["frozen_pairs"])==4,"original native source study count drift")
    by_case={(r["case"],r["witness"]):r for r in record["native_cases"]}
    require(len(by_case)==budget,"duplicate original native source case")
    records=[]
    with np.load(io.BytesIO(raw),allow_pickle=False) as archive:
        for left_name,right_name in record["frozen_pairs"]:
            for witness in ("A","B"):
                left=by_case[(left_name,witness)]
                right=by_case[(right_name,witness)]
                require(left["common_challenge"]==right["common_challenge"],
                        "distinct suffix words cannot verify right congruence")
                suffix=word(left["common_challenge"]+" 5")
                require(suffix[-1]==(5,None),"original native SDK pour absent")
                nleft=len(word(record["frozen_parent"]+" "+left["original_history"]))
                nright=len(word(record["frozen_parent"]+" "+right["original_history"]))
                left_all=word(left["original_source_word"])
                right_all=word(right["original_source_word"])
                require(left_all[nleft:]==right_all[nright:]==suffix,
                        "actual native source suffix not equal")
                start_l=sdk_stage4_return(archive,left_name,witness,nleft)
                start_r=sdk_stage4_return(archive,right_name,witness,nright)
                start_diff=witness_difference(start_l,start_r)
                comparison={
                    "paired_source_histories":[left_name,right_name],
                    "independent_original_entry_witness":witness,
                    "same_native_action_suffix":left["common_challenge"]+" 5",
                    "native_original_steps_after_matched_endpoint":len(suffix),
                    "initial_observation_equivalent":start_diff is None,
                    "initial_row63_different":bool(
                        not np.array_equal(start_l[:,63,:],start_r[:,63,:])
                    ),
                    "step_returns":[],
                    "first_projected_counterexample":None,
                    "native_source_status_pair":[
                        [left["official_level"],left["official_state"]],
                        [right["official_level"],right["official_state"]],
                    ],
                }
                require(start_diff is None and comparison["initial_row63_different"],
                        "original matched distinct-source projected endpoints lost")
                for i,(action,xy) in enumerate(suffix,1):
                    la=left["genuine_stage4_action_ledger"][nleft+i-1]
                    ra=right["genuine_stage4_action_ledger"][nright+i-1]
                    require(la["genuine_original_action"]==ra["genuine_original_action"]==action
                            and la["real_native_click_xy"]==ra["real_native_click_xy"]==xy,
                            "recorded original action suffix does not match SDK receipts")
                    a=sdk_stage4_return(archive,left_name,witness,nleft+i)
                    b=sdk_stage4_return(archive,right_name,witness,nright+i)
                    diff=witness_difference(a,b)
                    comparison["step_returns"].append({
                        "suffix_index":i,
                        "native_original_action":action,
                        "source_original_click_xy":xy,
                        "returned_frame_counts":[int(len(a)),int(len(b))],
                        "all_projected_frames_equivalent":diff is None,
                        "original_row63_differs":bool(
                            not np.array_equal(a[:,63,:],b[:,63,:])
                        ),
                        "native_sdk_level_after":[
                            la["original_sdk_level_after"],
                            ra["original_sdk_level_after"],
                        ],
                    })
                    if diff is not None and comparison["first_projected_counterexample"] is None:
                        comparison["first_projected_counterexample"]={
                            "suffix_index":i,
                            "original_sdk_action":action,
                            **diff,
                        }
                    if la["original_sdk_level_after"]!=ra["original_sdk_level_after"] or (
                        la["original_sdk_state_after"]!=ra["original_sdk_state_after"]
                    ):
                        comparison["official_sdk_counterexample"]={
                            "suffix_index":i,
                            "statuses":[
                                [la["original_sdk_level_after"],la["original_sdk_state_after"]],
                                [ra["original_sdk_level_after"],ra["original_sdk_state_after"]],
                            ],
                        }
                records.append(comparison)
    require(len(records)==8,"independent native A/B comparisons absent")
    for left_name,right_name in record["frozen_pairs"]:
        pair=[r for r in records if r["paired_source_histories"]==[left_name,right_name]]
        require(len(pair)==2 and {r["independent_original_entry_witness"] for r in pair}=={"A","B"},
                "native replay witnesses not independent A and B")
        comparison=lambda r:{k:v for k,v in r.items() if k!="independent_original_entry_witness"}
        require(comparison(pair[0])==comparison(pair[1]),
                "independent native replay witness disagreement")
    return records

def finite_field_scope_check():
    """Execute original mathematical laws, and deliberately refuse an ARC bridge."""
    w=World(3,(0,1,2))
    relabeled=World(3,(0,2,1))
    contradiction=World(3,(0,1,1))
    positive=align_worlds(w,relabeled,rescale_last)
    negative=discover_alignment(w,contradiction)
    require(positive.aligned and positive.source_count==27 and
            positive.target_count==27,"finite mathematical F3 alignment changed")
    require(negative.status=="OPEN" and negative.conflicting_words is not None,
            "finite F3 negative relation counterexample absent")
    return {
        "source":"work/arc_like_maze/math.py; work/arc_like_maze/alignment.py",
        "finite_field_dimension":3,
        "finite_field_cardinality":27,
        "positive_scope":"exact full rooted A/B transition conjugacy under rescale_last",
        "finite_model_positive":positive.aligned,
        "finite_model_negative":negative.status,
        "finite_model_counterexample_words":list(negative.conflicting_words),
        "sdk_to_F3_operator_correspondence":WALL,
    }

def run(directory):
    # Existing source-independent verification replays full original action/frame
    # ledgers and SHA256; the quotient test cannot silently trust case summaries.
    verified=[verify_arc4_source(directory/fn,base,n,js,npz)
              for fn,base,n,js,npz in ARC4_ARCHIVES]
    stage3=verify_stage3_source(directory/STAGE3)
    require(stage3["native_controls_independently_rechecked"]==8,
            "same-stage native cup counterexample evidence incomplete")
    rows={(r["case"],r["witness"]):r
          for r in stage3["original_case_source_receipts"]}
    for witness in ("A","B"):
        won=rows[("catch_left3_up5",witness)]
        lost=rows[("catch_left2_up5",witness)]
        require(won["first_four_simultaneous"]==lost["first_four_simultaneous"]==27
                and won["official_level"]==4 and lost["official_level"]==3,
                "same-stage native visible-four-cups reward counterexample drift")
    comparisons=[
        r for filename,base,budget in STUDIES
        for r in compare_study(directory,filename,base,budget)
    ]
    require(len(comparisons)==16 and
            all(x["initial_observation_equivalent"] for x in comparisons),
            "native paired histories do not satisfy initial observed relation")
    contradictions=[x for x in comparisons
                    if x["first_projected_counterexample"] or
                       x.get("official_sdk_counterexample")]
    math=finite_field_scope_check()
    return {
        "kind":"ORIGINAL_ARC4_FINITE_OBSERVATIONAL_RIGHT_CONGRUENCE",
        "question":"Does equality of the projected native frame survive identical observed native action suffixes?",
        "mathematical_relation":"h ~_P k iff P(F(h)) == P(F(k)); P=rows0..62 of original SDK",
        "native_original_verified_archives":len(verified)+1,
        "verified_native_source_resets_arc4":sum(x["native_resets"] for x in verified),
        "verified_native_source_resets_stage3_archive":50,
        "tested_matched_history_pairs_with_witnesses":len(comparisons),
        "tested_matched_common_native_action_returns":sum(
            len(x["step_returns"]) for x in comparisons),
        "full_returned_frame_equality_scope":"all real SDK frames for every tested action suffix step",
        "right_compatibility_status":"OPEN_COUNTEREXAMPLE" if contradictions
             else "BOUNDED_COMPATIBLE_ON_FINITE_TESTED_SUFFIXES",
        "counterexamples":contradictions,
        "pairwise_witnesses":comparisons,
        "independent_native_entry_labels":"A,B are SDK replay witnesses, NOT finite-field mathematical A,B generators",
        "visible_four_cups_reward_sufficiency":"REFUTED_IN_ORIGINAL_STAGE3",
        "same_stage_native_reward_counterexample":{
            "success":"catch_left3_up5, all four visual cups first full together frame27, official level4",
            "failure":"catch_left2_up5, all four visual cups first full together frame27, official level3",
            "A_B_original_sdk_replications":2,
        },
        "finite_field_math":math,
        "admission":"WALL_NO_PROVED_ACTION_MAP_FROM_SDK_TO_F3",
        "next_step":"Construct a specifically declared action/state mapping and independently check it against both systems before treating SDK movement as derived from F3 A/B operators.",
        "walls":[
            "Finite tested suffix agreement is not global right congruence or bisimulation.",
            "Projection equality does not certify equality of private game states.",
            "Original SDK levels_completed/WIN is the only gameplay success oracle.",
            "No source-grounded mapping from SDK ACTION1..6 to finite F3 A/B was supplied.",
            "Two SDK entry histories named A/B are never formal F3 generators.",
        ],
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report=run(args.directory)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("ORIGINAL_ARC4_MATH_ADMISSION "+json.dumps({
        k:v for k,v in report.items() if k not in ("pairwise_witnesses","walls")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
