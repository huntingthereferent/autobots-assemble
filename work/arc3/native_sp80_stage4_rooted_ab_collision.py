"""Original SP80 rooted A/B collision test, with independent exact F3 calibration.

Two different *native* histories, right-left (RL) and left-right (LR),
return to the exact same full visible 64x64 original SDK source before
a common next action. Earlier native artifact #12594180466 verified:
both pre-pour BLAKE2b16 ae687e1565f7c888212c03ba8bdf6145;
both actual subsequent ACTION5 32-frame stack
ac12fe4d3123aa7e5d9473a45a67d20a.
Precommit distinct COMMON SDK next-action words and ask if an equal
visible root collides or splits in true next state and returned frames.

The separate original F3-48 A/B theorem distinguishes FULL-STATE
conjugacy from ORIGIN-PRESERVING conjugacy; verify a sample of its exact
certificates without claiming a mapping of six SP80 actions to F3 labels.
Only original native levels_completed>=5/WIN counts as progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE, read_pour
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame
from ..arc_like_maze.window_combined import CombinedWorld,classify_pair,rooted_conflict

COMMON=BASE+" 6@15,48"
HISTORIES={"RL":"4 3 6@18,36","LR":"3 4 6@18,36"}
FUTURES={
 "pour":"5",
 "up_pour":"1 5",
 "down_pour":"2 5",
 "left_pour":"3 5",
 "right_pour":"4 5",
 "select_middle_pour":"6@15,48 5",
 "select_upper_pour":"6@34,21 5",
 "twice_pour":"5 5",
}
EXPECTED_VISIBLE="ae687e1565f7c888212c03ba8bdf6145"
EXPECTED_NATIVE_POUR="ac12fe4d3123aa7e5d9473a45a67d20a"
assert len(HISTORIES)==2 and len(FUTURES)==8 and len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(COMMON+" "+hist))==25 for hist in HISTORIES.values())
assert all(parse_plan(future)[-1][0]==5 for future in FUTURES.values())
assert all(all(a!=6 or xy is not None for a,xy in parse_plan(future))
           for future in FUTURES.values())

def f3_calibration():
    cert=[]
    for support in (0,1,2,3):
        left=CombinedWorld(support,0,1,0)
        right=CombinedWorld(support,0,1,1)
        relation=classify_pair(left,right)
        pair={"support":support,"status":relation.status,
              "root_preserving":relation.root_preserving,
              "obstruction_word":relation.obstruction_word}
        if support in (0,3):
            assert relation.status=="ALL_DEPTH_FULL_STATE_NONROOT_CONJUGACY"
            witness=rooted_conflict(left,right)
            assert witness is not None
            wa,wb,collision,ra,rb=witness
            assert left.apply((0,0,0),wa)==left.apply((0,0,0),wb)==collision
            assert right.apply((0,0,0),wa)==ra
            assert right.apply((0,0,0),wb)==rb and ra!=rb
            pair["rooted_collision"]={"source_words":[wa,wb],
                  "same_source_state":collision,"distinct_target_states":[ra,rb]}
        else:
            assert relation.status=="INEQUIVALENT_ACTION_WORD"
            assert relation.obstruction_word=="ABABAB"
            pair["fixed_ABABAB_counts"]=[
                left.fixed_word("ABABAB"),right.fixed_word("ABABAB")]
            assert pair["fixed_ABABAB_counts"][0]!=pair["fixed_ABABAB_counts"][1]
        cert.append(pair)
    return cert

def one(case,hist,entry_name,entry_word,future):
    program=COMMON+" "+HISTORIES[hist]+" "+future
    pivot=len(parse_plan(COMMON+" "+HISTORIES[hist]))
    n=len(parse_plan(program))
    sdk,stacks=run_case(case,entry_name,entry_word,program)
    root=stacks["entry3_34"][-1]
    pre=stacks[f"stage4_{pivot}"][-1]
    predigest=hash_frame(pre)
    if predigest!=EXPECTED_VISIBLE:
        raise AssertionError("Authentic source root changed: "+predigest)
    tail=[]
    for i in range(pivot+1,n+1):
        key=f"stage4_{i}"
        if key not in stacks:break
        source_stack=stacks[key]
        rec=next(r for r in sdk["genuine_original_stage4_action_ledger"]
                 if r["index"]==i)
        tail.append({"native_action_index":i,
           "actual_action":rec["genuine_original_action"],
           "actual_click":rec["real_native_click_xy"],
           "public_sdk_level":rec["original_sdk_level_after"],
           "public_sdk_state":rec["original_sdk_state_after"],
           "native_returned_stack_blake2b16":__hash_array(source_stack),
           "native_returned_last_frame_blake2b16":hash_frame(source_stack[-1]),
           "native_returned_frame_count":len(source_stack)})
    if len(tail)!=len(parse_plan(future)) and not sdk["official_original_level5_or_WIN"]:
        raise AssertionError("Expected full native continuation missing")
    measured=[]
    for i in range(pivot+1,pivot+len(tail)+1):
        if parse_plan(program)[i-1][0]!=5:continue
        previous=stacks[f"stage4_{i-1}"][-1]
        info=read_pour(root,previous,stacks[f"stage4_{i}"])
        measured.append({"native_action_index":i,
           "full_four_source_frames":info["same_sdk_frame_full_four_cups"],
           "source_cup_max":info["max_original_cup_palette13"]})
    return ({
       "history":hist,"independent_stage1_entry":entry_name,
       "future":future,"real_stage4_action_word":program,
       "native_visible_prepour_root":predigest,
       "true_official_level":sdk["true_original_sdk_final_level"],
       "true_official_state":sdk["true_original_sdk_final_state"],
       "original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
       "real_native_next_actions":tail,
       "real_native_pour_source":measured,
       "true_native_original_stage4_ledger":sdk["genuine_original_stage4_action_ledger"],
       "actual_original_sdk_entry_receipts":sdk["full_native_stage4_entry_receipts"],
       "marked_root_not_hidden_state":"Equal 64x64 source images do not prove equality of unknown private full state."
    },{key:value for key,value in stacks.items()
        if key=="entry3_34" or key.startswith("stage4_"+str(pivot)) or
           (key.startswith("stage4_") and int(key.rsplit("_",1)[-1])>pivot)})

def __hash_array(a):
    from hashlib import blake2b
    return blake2b(np.asarray(a).tobytes(),digest_size=16).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    theory=f3_calibration()
    records=[];pairs=[];arrays={}
    for future, suffix in FUTURES.items():
        for witness,entry in STAGE1_WITNESSES:
            pair={}
            for h in ("RL","LR"):
                row,stacks=one(future,h,witness,entry,suffix)
                pair[h]=row;records.append(row)
                for phase,stack in stacks.items():
                    arrays[f"{future}_{h}_{witness}_{phase}"]=stack
            a,b=pair["RL"],pair["LR"]
            assert a["native_visible_prepour_root"]==b["native_visible_prepour_root"]
            minlen=min(len(a["real_native_next_actions"]),
                       len(b["real_native_next_actions"]))
            split=next((i for i in range(minlen)
                if a["real_native_next_actions"][i]!=b["real_native_next_actions"][i]),None)
            if split is None and len(a["real_native_next_actions"])!=len(b["real_native_next_actions"]):
                split=minlen
            matched={
              "frozen_followup":future,"source_entry_witness":witness,
              "same_full_original_visible_root":True,
              "same_official_state":(a["true_official_level"],a["true_official_state"])==
                                    (b["true_official_level"],b["true_official_state"]),
              "native_followup_frame_word_equal":split is None,
              "first_distinct_followup_native_action_index":split,
              "original_level5_or_WIN_RL":a["original_level5_or_WIN"],
              "original_level5_or_WIN_LR":b["original_level5_or_WIN"]}
            pairs.append(matched)
            print("SP80_ROOTED_AB_FORK "+json.dumps(matched,sort_keys=True),flush=True)
    if len(records)!=32 or len(pairs)!=16:
        raise AssertionError("Paired original SDK native source programs missing")
    for future in FUTURES:
        x,y=[p for p in pairs if p["frozen_followup"]==future]
        if {k:v for k,v in x.items() if k!="source_entry_witness"}!={
           k:v for k,v in y.items() if k!="source_entry_witness"}:
            raise AssertionError("Independent original stage1 witness disagreement")
    original_pour=[r for r in records if r["future"]=="pour"]
    for row in original_pour:
        if row["real_native_next_actions"][0]["native_returned_stack_blake2b16"]!=EXPECTED_NATIVE_POUR:
            raise AssertionError("Previously independently witnessed pour stack differs")
    summary={
      "kind":"ORIGINAL_NATIVE_SP80_ROOTED_AB_SOURCE_COLLISION_CONTINUATIONS",
      "mathematical_f3_48_scope_calibration":theory,
      "genuine_original_independent_sdk_games":len(records),
      "original_same_source_root_digest":EXPECTED_VISIBLE,
      "two_distinct_original_action_histories":HISTORIES,
      "no_native_f3_mapping_claim":True,
      "paired_comparisons":pairs,
      "official_level5_or_WIN":[r["future"]+"_"+r["history"]+"_"+r["independent_stage1_entry"]
           for r in records if r["original_level5_or_WIN"]],
      "sdk_level_histogram":dict(Counter(str(r["true_official_level"]) for r in records)),
      "full_genuine_native_sdk_receipts":records,
      "limitations":"F3 rooted conjugacy calibration and native observable-root collision are separate valid findings. Cannot infer hidden game state or identify SP80 as F3 family. Original canonical agent and mathematics unmodified."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_ROOTED_AB_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("full_genuine_native_sdk_receipts","paired_comparisons")
        },sort_keys=True),flush=True)
if __name__=="__main__":main()
