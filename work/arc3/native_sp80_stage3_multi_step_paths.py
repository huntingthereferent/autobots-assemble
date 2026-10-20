"""Source-directed stage3 bar-routing controls on authentic Arcade.NORMAL SP80.

Original source run #39471887855 measured 3-pixel shifts and a grouped
stage3 middle pair. The 172-reset follow-up #39473607332 established that
single-step beam candidates did not reach SDK level4. THIS trial changes
the intervention: move observed middle pair by multiple native steps,
then shift one or both lower right bands. Screen flow is a hypothesis,
never an asserted source physics engine or official goal predicate.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_stage3_source_guided_search import feedback
from .native_sp80_multi_select import parse_plan

def middle(n):
    return "6@10,30 "+" ".join(["4"]*n)
FROZEN=(
    ("mid_right2",middle(2)+" 5"),
    ("mid_right3",middle(3)+" 5"),
    ("mid_right4",middle(4)+" 5"),
    ("mid_right2_lower_left1",middle(2)+" 6@46,33 3 5"),
    ("mid_right3_lower_left1",middle(3)+" 6@46,33 3 5"),
    ("mid_right4_lower_left1",middle(4)+" 6@46,33 3 5"),
    ("mid_right3_lower_left2",middle(3)+" 6@46,33 3 3 5"),
    ("mid_right4_lower_left2",middle(4)+" 6@46,33 3 3 5"),
    ("mid_right3_bottom_left1",middle(3)+" 6@40,42 3 5"),
    ("mid_right4_bottom_left1",middle(4)+" 6@40,42 3 5"),
    ("mid_right3_bottom_left2",middle(3)+" 6@40,42 3 3 5"),
    ("mid_right4_bottom_left2",middle(4)+" 6@40,42 3 3 5"),
    ("mid_right3_lower_bottom_left1",middle(3)+" 6@46,33 3 6@40,42 3 5"),
    ("mid_right4_lower_bottom_left1",middle(4)+" 6@46,33 3 6@40,42 3 5"),
    ("mid_right3_upper_right_down2",middle(3)+" 6@40,18 2 2 5"),
    ("mid_right3_upper_right_down3",middle(3)+" 6@40,18 2 2 2 5"),
    ("mid_right3_selected_left1_lowerleft1",middle(3)+" 6@20,18 3 6@46,33 3 5"),
    ("mid_right4_selected_left1_lowerleft1",middle(4)+" 6@20,18 3 6@46,33 3 5"),
    # Follow-up, frozen from the actual first-pass source bin-3-vs-bin-4 contrast.
    ("mid3_bottom_right1",middle(3)+" 6@40,42 4 5"),
    ("mid4_bottom_right1",middle(4)+" 6@40,42 4 5"),
    ("mid3_bottom_right2",middle(3)+" 6@40,42 4 4 5"),
    ("mid4_bottom_right2",middle(4)+" 6@40,42 4 4 5"),
    ("mid3_bottom_right3",middle(3)+" 6@40,42 4 4 4 5"),
    ("mid4_bottom_right3",middle(4)+" 6@40,42 4 4 4 5"),
    ("mid3_bottom_up1",middle(3)+" 6@40,42 1 5"),
    ("mid3_bottom_up2",middle(3)+" 6@40,42 1 1 5"),
    ("mid3_bottom_down1",middle(3)+" 6@40,42 2 5"),
    ("mid3_bottom_down2",middle(3)+" 6@40,42 2 2 5"),
    ("mid3_bottom_left3",middle(3)+" 6@40,42 3 3 3 5"),
    ("mid4_bottom_left3",middle(4)+" 6@40,42 3 3 3 5"),
    ("mid3_bottom_right1_lowerleft1",middle(3)+" 6@40,42 4 6@46,33 3 5"),
    ("mid4_bottom_right1_lowerleft1",middle(4)+" 6@40,42 4 6@46,33 3 5"),
    ("mid3_bottom_right1_lowerleft2",middle(3)+" 6@40,42 4 6@46,33 3 3 5"),
    ("mid3_bottom_right2_lowerleft1",middle(3)+" 6@40,42 4 4 6@46,33 3 5"),
    ("mid3_bottom_up_right1",middle(3)+" 6@40,42 1 4 5"),
    ("mid3_bottom_down_right1",middle(3)+" 6@40,42 2 4 5"),
    ("mid3_bottom_up_left2",middle(3)+" 6@40,42 1 3 3 5"),
    ("mid3_bottom_down_left2",middle(3)+" 6@40,42 2 3 3 5"),
    ("mid4_bottom_up_right1",middle(4)+" 6@40,42 1 4 5"),
    ("mid4_bottom_down_right1",middle(4)+" 6@40,42 2 4 5"),
    ("mid3_bottom_right1_upperdown2",middle(3)+" 6@40,42 4 6@40,18 2 2 5"),
    ("mid3_bottom_right1_upperleft2",middle(3)+" 6@40,42 4 6@40,18 3 3 5"),
    ("mid3_bottom_right1_selectedleft1",middle(3)+" 6@40,42 4 6@20,18 3 5"),
    ("mid3_bottom_right1_selectedright1",middle(3)+" 6@40,42 4 6@20,18 4 5"),
)
assert len(FROZEN)==len(set(n for n,_ in FROZEN))==44
assert all(parse_plan(s)[-1][0]==5 for _,s in FROZEN)

def compact(row):
    return [{k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
            for e in row["full_original_sdk_action_events"]]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    records=[];raw_data={};sha=set()
    for name,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            row,frames=real_trial(witness,entry,name,word)
            sha.add(row["original_verified_stage3_root"]["original_source_sha256"])
            last=frames.get("stage3_"+str(len(parse_plan(word))))
            observed=feedback(frames["entry2_11"][-1],last) if last is not None else None
            entry_record={
                "control":name,"witness":witness,"native_word":word,
                "original_sdk_official_last_level":row["official_original_final_level"],
                "original_sdk_official_last_state":row["official_original_final_state"],
                "authentic_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "native_disposition":row["trial_disposition"],
                "observed_only_source_pour_effect":observed,
                "true_original_sdk_actions":compact(row),
            }
            records.append(entry_record)
            for k,arr in frames.items():raw_data["%s_%s_%s"%(name,witness,k)]=arr
            print("ORIGINAL_SP80_MULTI_STEP_SOURCE_RESULT "+json.dumps({
                k:v for k,v in entry_record.items() if k!="true_original_sdk_actions"
            },sort_keys=True),flush=True)
    if len(records)!=88 or len(sha)!=1:
        raise AssertionError("Missing independent original SDK witness or root disagreement")
    summary={
       "kind":"ACTUAL_ORIGINAL_SP80_STAGE3_MULTI_STEP_SOURCE_PATH_CONTROLS",
       "source_antecedents":[39463571663,39471887855,39473607332],
       "prospective_actual_native_words":FROZEN,
       "genuine_independently_reset_original_sdk_games":len(records),
       "source_verified_stage3_root_hash":next(iter(sha)),
       "source_native_official_level4_or_WIN_count":sum(int(r["authentic_sdk_level4_or_WIN"]) for r in records),
       "original_sdk_level_counts":dict(Counter(str(r["original_sdk_official_last_level"]) for r in records)),
       "source_original_winners":[{"witness":r["witness"],"native_word":r["native_word"],
            "original_level":r["original_sdk_official_last_level"]}
            for r in records if r["authentic_sdk_level4_or_WIN"]],
       "all_original_source_sdk_records":records,
       "boundary":"Visual palette11->13 group transitions are source pixel feedback, not asserted hidden goal or physics. Only official SDK levels>=4 or WIN support game advancement. Original SDK returned frame arrays preserved in NPZ; other lanes and rights untouched."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_data)
    print("ORIGINAL_SP80_MULTI_STEP_SUMMARY "+json.dumps({k:v for k,v in summary.items()
         if k not in ("all_original_source_sdk_records","prospective_actual_native_words")},sort_keys=True),flush=True)
if __name__=="__main__":main()
