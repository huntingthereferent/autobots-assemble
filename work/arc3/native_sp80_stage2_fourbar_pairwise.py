"""Original SP80: genuine native level2 four-bar small-motion pairwise test.

The source-native stage2 coordinate-click inventory verified individual
ACTION6 selection of all four colored bars and actual one-step ACTION4
movement even for the bars near the right screen edge. Do not assume
that earlier level0/1 puzzle predicates transfer to source stage2.

This is a prospectively frozen balanced pairwise four-bar intervention:
27 orthogonal strength-2 source-native combinations over (-1,0,+1)
single ACTION3/4 movements for observed bars U,M,L,B, plus nine
independent extreme/context controls. Each word is executed on TWO
fresh original SP80 game resets, one through source level1->2
witness A and one through genuinely different verified witness B.
All ACTION6 data={x,y}, official legal actions, full SDK frame stacks,
actual last pre-ACTION5 positions and SDK levels/WIN/GAME_OVER are
preserved. Only actual SDK level3 or WIN constitutes native progress.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as original_native_trial

VALUES=(-1,0,1)
BARS=("U","M","L","B")
CLICKS={
  "U":"6@12,21", # native upper color8 16x4, x8..23,y20..23
  "M":"6@44,29", # original middle color8 20x4, x40..59,y28..31
  "L":"6@12,33", # original lower color8 24x4, x8..31,y32..35
  "B":"6@40,41", # source lowest initially selected color9 x36..59,y40..43
}
BANDS={"U":(20,24),"M":(28,32),"L":(32,36),"B":(40,44)}

def original_word(steps):
    parts=[]
    for bar,offset in zip(BARS,steps):
        parts.append(CLICKS[bar])
        parts.extend((["4"] if offset>0 else ["3"])*abs(offset))
    parts.append("5")
    return " ".join(parts)

# Modulo-3 balanced design: every pair of 4 offsets spans all 3x3
# combinations on 27 source programs, followed by nine fixed controls.
MAIN=tuple(
    (a,b,c,((a+1+b+1+c+1)%3)-1)
    for a,b,c in product(VALUES,repeat=3)
)
EXTRA=(
   (-1,-1,-1,0),
   (0,0,0,0),
   (1,1,1,1),
   (-1,0,1,1),
   (1,0,-1,1),
   (0,-1,1,0),
   (0,1,-1,0),
   (1,-1,1,-1),
   (-1,1,-1,0),
)
STEPS=MAIN+EXTRA
def name(steps):
    return "U%s_M%s_L%s_B%s"%tuple(
       ("N" if a==-1 else "Z" if a==0 else "P") for a in steps)
PROGRAMS=tuple((name(steps),steps,original_word(steps)) for steps in STEPS)
assert len(MAIN)==27 and len(EXTRA)==9 and len(STEPS)==len(set(STEPS))==36
assert len(PROGRAMS)==len(set(n for n,_,_ in PROGRAMS))==36
assert all(len(STAGE1_WITNESSES)==2 for _ in (0,))
assert all(set(q)<=set(VALUES) for q in STEPS)
# Assert actual pairwise coverage rather than merely referring to it.
for i in range(4):
  for j in range(i+1,4):
    assert set((row[i],row[j]) for row in MAIN)==set(product(VALUES,repeat=2))

def actual_bar_positions(frame):
    observed={}
    for bar,(y0,y1) in BANDS.items():
        region=frame[y0:y1]
        yy,xx=np.nonzero(np.isin(region,[8,9]))
        observed[bar]={
          "actual_native_bbox":(
              [int(xx.min()),int(yy.min()+y0),
               int(xx.max()),int(yy.max()+y0)] if len(xx) else None),
          "actual_native_bar_pixels":int(len(xx)),
          "original_native_selected_color9_cells":int(np.count_nonzero(region==9)),
          "original_native_color8_cells":int(np.count_nonzero(region==8)),
        }
    return observed

def source_stage2_commit(trial,raw):
    events=trial["stage2_native_observations"]
    for event in events:
        if event["native_action"]!=5:
            continue
        step=event["phase_step"]
        prev=(raw["witness_"+str(len(trial["full_original_SDK_action_records"])-len(events)-6)][-1]
              if step==1 else raw["stage2_"+str(step-1)][-1])
        # First stage2 commit is always after at least four clicks.
        assert step>1
        previous=raw["stage2_"+str(step-1)][-1]
        stack=raw.get("stage2_"+str(step))
        return {
            "original_stage2_ACTION5_step":step,
            "official_SDK_level_before":event["source_SDK_level_before"],
            "official_SDK_level_after":event["source_SDK_level_after"],
            "official_SDK_state_after":event["source_SDK_state_after"],
            "actual_source_pre_ACTION5_bar_positions":actual_bar_positions(previous),
            "real_original_sdk_returned_frames":len(stack) if stack is not None else None,
            "authentic_original_last_frame_after_ACTION5":(
                actual_bar_positions(stack[-1]) if stack is not None else None),
        }
    return {"status":"UNKNOWN_NATIVE_ACTION5_NOT_REACHED"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    trials,raw_frames=[],{}
    for condition,steps,word in PROGRAMS:
        for witness,entry in STAGE1_WITNESSES:
            # Every trial creates its own entirely NEW original NORMAL game.
            result,images=original_native_trial(witness,entry,condition,word,0)
            result["predeclared_stage2_bar_offsets"]=dict(zip(BARS,steps))
            result["native_stage2_commit_observation"]=source_stage2_commit(result,images)
            trials.append(result)
            for phase,arr in images.items():
                raw_frames[f"{condition}_{witness}_rep0_{phase}"]=arr

    per={}
    for condition,steps,word in PROGRAMS:
        group=[t for t in trials if t["frozen_level2_control"]==condition]
        per[condition]={
          "original_frozen_native_bar_offsets":dict(zip(BARS,steps)),
          "genuine_stage2_action_word":word,
          "two_independent_source_entry_witnesses":[t["witness"] for t in group],
          "source_sdk_last_levels":[t["original_source_final_level"] for t in group],
          "source_sdk_last_states":[t["original_source_final_state"] for t in group],
          "genuine_level3_or_WIN":[t["source_level3_or_WIN"] for t in group],
          "actual_source_dispositions":[t["source_stage2_control_disposition"] for t in group],
          "native_before_commit_source_bars":[
              t["native_stage2_commit_observation"].get(
                "actual_source_pre_ACTION5_bar_positions") for t in group],
          "original_SDK_returned_ACTION5_frames":[
              t["native_stage2_commit_observation"].get(
                "real_original_sdk_returned_frames") for t in group],
          "stage2_real_clicks":[[
             [e["native_click_xy"],e["original_native_preclick_color"]]
             for e in t["stage2_native_observations"] if e["native_action"]==6
          ] for t in group],
        }
    out={
       "kind":"GENUINE_ORIGINAL_SP80_STAGE2_FOUR_BAR_PAIRWISE_MOVEMENT_AND_ACTION5",
       "source_frozen_pairwise_27_offsets":MAIN,
       "source_frozen_extreme_control_offsets":EXTRA,
       "source_native_action_plans":PROGRAMS,
       "original_source_entry_witnesses":STAGE1_WITNESSES,
       "true_original_sdk_independent_game_resets":len(trials),
       "true_native_sdk_action_responses":sum(t["source_SDK_actions_accepted"] for t in trials),
       "actual_source_stage2_clicks":sum(int(e["native_action"]==6)
           for t in trials for e in t["stage2_native_observations"]),
       "source_genuine_level3_or_WIN":sum(int(t["source_level3_or_WIN"]) for t in trials),
       "source_sdk_dispositions":dict(Counter(t["source_stage2_control_disposition"] for t in trials)),
       "each_original_pairwise_fourbar_condition":per,
       "all_genuine_source_original_sdk_records":trials,
       "limits":"This is a balanced source-native bounded exploratory stage2 movement test, not a known source puzzle law, hidden engine model or game win. Genuine original game reached via full level0/1 source controls. Only official SDK levels>=3 or WIN proves native stage3 progress. Complete original returned 64x64 frame stacks retained and click x/y native pixels recorded.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_frames)
    print("SP80_STAGE2_FOUR_BAR_PAIRWISE "+json.dumps({
       k:v for k,v in out.items()
       if k not in ("each_original_pairwise_fourbar_condition","all_genuine_source_original_sdk_records")
    },sort_keys=True))
    print("SP80_STAGE2_FOUR_BAR_PROGRESS "+json.dumps({
       name:{
          "native_offsets":v["original_frozen_native_bar_offsets"],
          "level":v["source_sdk_last_levels"],
          "state":v["source_sdk_last_states"],
          "precommit_bars":v["native_before_commit_source_bars"]
       } for name,v in per.items()
       if any(v["genuine_level3_or_WIN"])
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*len(STAGE1_WITNESSES):
        raise RuntimeError("Missing independently reset original stage2 SDK games")
if __name__=="__main__":
    main()
