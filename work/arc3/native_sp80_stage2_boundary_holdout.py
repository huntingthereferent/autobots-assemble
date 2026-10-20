"""Original SP80 stage1->2 heldout neighboring controls of two real SDK witnesses.

Source observed on previous independent native run #39318735025:
A: F2 L0 U3 => actual level2, 2/2;
B: F2 L2 U3 => actual level2, 2/2;
F2 L3 U3, F0 L0 U3, F3 L0 U3 => genuine level1 negatives.
These are bounds, not discovered hidden puzzle physics.

Freeze exact witnesses and new nearby conditions (L1, F1/3, U2/4,
source click order, commits before final), execute with real
arc_agi.Arcade NORMAL native resets and preserve ALL obs.frame arrays,
actual source levels and states, native action/click provenance.
Never call a game win from any visible color or frame count.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

CLICK={"F":"6@24,37","L":"6@32,25","U":"6@12,17"}
def w(f,l,u,order="FLU",commits=False):
    counts=dict(zip("FLU",(f,l,u)))
    a=[]
    for k in order:
        a.append(CLICK[k]);a.extend(["4"]*counts[k])
        if commits:a.append("5")
    if not commits:a.append("5")
    return " ".join(a)

FIXED=(
 ("witness_A_F2L0U3",w(2,0,3)),
 ("witness_B_F2L2U3",w(2,2,3)),
 ("neighbor_L1_F2U3",w(2,1,3)),
 ("neighbor_L3_F2U3",w(2,3,3)),
 ("neighbor_F1_L0_U3",w(1,0,3)),
 ("neighbor_F1_L2_U3",w(1,2,3)),
 ("neighbor_F3_L0_U3",w(3,0,3)),
 ("neighbor_F3_L2_U3",w(3,2,3)),
 ("neighbor_U2_F2L0",w(2,0,2)),
 ("neighbor_U2_F2L2",w(2,2,2)),
 ("neighbor_U4_F2L0",w(2,0,4)),
 ("neighbor_U4_F2L2",w(2,2,4)),
 ("order_ULF_A",w(2,0,3,"ULF")),
 ("order_ULF_B",w(2,2,3,"ULF")),
 ("order_LUF_A",w(2,0,3,"LUF")),
 ("order_LUF_B",w(2,2,3,"LUF")),
 ("order_FUL_A",w(2,0,3,"FUL")),
 ("order_FUL_B",w(2,2,3,"FUL")),
 ("commit_each_A",w(2,0,3,commits=True)),
 ("commit_each_B",w(2,2,3,commits=True)),
 ("click_last_lower_A","6@24,37 4 4 6@12,17 4 4 4 6@32,25 5"),
 ("click_last_first_A","6@12,17 4 4 4 6@32,25 6@24,37 4 4 5"),
)
RESETS=2
assert len(FIXED)==22 and len({n for n,_ in FIXED})==22
assert all(parse_plan(word)[-1][0]==5 and
    all(action!=6 or xy is not None for action,xy in parse_plan(word))
    for _,word in FIXED)

def extract(trial,raw):
    rows=[]
    for event in trial["real_sdk_observation_ledger"]:
        if event["phase"]!="context":continue
        idx=event["phase_action_number"]
        stack=raw.get("context_"+str(idx))
        if stack is None:
            rows.append({"step":idx,"native_action":event["native_action_id"],
                "disposition":"UNKNOWN_SOURCE_FULL_FRAME"});continue
        pre=raw["entry_6"][-1] if idx==1 else raw["context_"+str(idx-1)][-1]
        cur=stack[-1]
        y,x=np.nonzero(pre==9)
        bbox=([int(x.min()),int(y.min()),int(x.max()),int(y.max())]
              if len(x) else None)
        rows.append({
            "context_sdk_step":idx,
            "original_native_action":event["native_action_id"],
            "source_clicked_xy":event["native_click_xy"],
            "true_source_clicked_preimage_color":event["actual_native_pre_click_pixel"],
            "pre_image_original_hash":hash_frame(pre),
            "source_actual_selected_color9_pre_bbox":bbox,
            "official_sdk_level_after":event["original_source_level_after"],
            "official_sdk_state_after":event["original_source_state_after"],
            "original_sdk_returned_image_count":len(stack),
            "true_source_original_post_hash":hash_frame(cur),
        })
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,arrays=[],{}
    for name,word in FIXED:
        for rep in range(RESETS):
            trial,raw=one(name,word,rep)
            trial["new_native_level2_boundary_observations"]=extract(trial,raw)
            trials.append(trial)
            for k,v in raw.items():
                arrays[f"{name}_rep{rep}_{k}"]=v
    per={}
    for name,word in FIXED:
        group=[t for t in trials if t["name"]==name]
        per[name]={
           "prospective_source_word":word,
           "actual_SDK_level":[t["original_last_source_level"] for t in group],
           "actual_SDK_state":[t["original_last_source_state"] for t in group],
           "genuine_source_level2_or_win":[t["native_level2_or_win"] for t in group],
           "native_disposition":[t["actual_source_disposition"] for t in group],
           "full_native_final_hash":[t["source_original_final_frame_hash"] for t in group],
           "real_native_action_count":[t["actual_native_calls"] for t in group],
           "actual_source_action_observations":[t["new_native_level2_boundary_observations"] for t in group]
        }
    output={
      "kind":"ORIGINAL_SP80_SOURCE_LEVEL1_TO2_BOUNDARY_HELDOUT",
      "source_precommitted_action_programs":FIXED,
      "real_original_reset_trials_per_program":RESETS,
      "actual_genuine_native_original_games":len(trials),
      "genuine_sdk_actions":sum(t["actual_native_calls"] for t in trials),
      "original_native_level2_or_win_trials":sum(int(t["native_level2_or_win"]) for t in trials),
      "native_sdk_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
      "per_original_program":per,
      "complete_unfiltered_native_source_trial_records":trials,
      "boundary":"ONLY authentic SDK levels_completed>=2 or GameState.WIN labels level2. Native full obs.frame stacks unmodified, all click data true, no extrapolation of goal or F3 math laws.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_STAGE2_BOUNDARY "+json.dumps({
        k:v for k,v in output.items() if k not in
        ("per_original_program","complete_unfiltered_native_source_trial_records")
    },sort_keys=True))
    print("SP80_STAGE2_BOUNDARY_SUMMARY "+json.dumps({
        k:{"levels":v["actual_SDK_level"],"states":v["actual_SDK_state"],
            "sha":v["full_native_final_hash"]}
        for k,v in per.items()
    },sort_keys=True))
    if len(trials)!=len(FIXED)*RESETS:raise AssertionError("Incomplete native trials")
if __name__=="__main__":main()
