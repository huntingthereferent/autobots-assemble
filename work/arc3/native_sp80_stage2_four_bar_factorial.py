"""Original SP80 native stage2: prospective four-bar joint-movement factorial.

Parent source-authenticated stage2 click study demonstrated all FOUR
actual original color8/9 horizontal bars respond to genuine coordinate
ACTION6, while original SDK level3 remains unwitnessed.
This is NOT a stage3 win condition or hidden-game physics inference.

Freeze four genuinely clicked bar motions:
 F highlighted 24x4 bottom: left 0 or 2 native ACTION3;
 L lower 24x4: right 0 or 2 ACTION4;
 M middle 20x4: left 0 or 2 ACTION3;
 U upper 16x4: right 0 or 2 ACTION4.
All 2^4=16 states and eight controlled 1/3-step offsets, two fresh
original Arcade.NORMAL SP80 games each. Native level2 reached only
via exact original stage0 454545 + stage1 witness A.
Preserve real source click pixels, four bar pre-ACTION5 boxes, all
SDK-returned true images, official levels_completed and game state.
Original level3/WIN is the ONLY actual progress label.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import product
from pathlib import Path
import numpy as np
from .native_sp80_stage2_four_bar_clicks import play_source
from .native_sp80_multi_select import parse_plan

# Each source click coordinate was actually verified in preceding native
# stage2 independent experiments, on the exact same original source root.
CLICKS={"F":"6@40,41","L":"6@12,33","M":"6@44,29","U":"6@12,21"}
MOVE={"F":"3","L":"4","M":"3","U":"4"}
ORDER="FLMU"
RESETS=2
def source_word(steps,order=ORDER):
    counts=dict(zip("FLMU",steps))
    words=[]
    for bar in order:
        words.append(CLICKS[bar])
        words.extend([MOVE[bar]]*counts[bar])
    words.append("5")
    return " ".join(words)

FACTORS=tuple(
  ("four_bar_F%d_L%d_M%d_U%d"%(f,l,m,u),source_word((f,l,m,u)))
  for f,l,m,u in product((0,2),repeat=4)
)
CONTROLS=tuple(
  ("four_bar_control_F%d_L%d_M%d_U%d"%(f,l,m,u),source_word((f,l,m,u)))
  for f,l,m,u in (
   (1,1,1,1),(3,3,3,3),
   (3,0,3,0),(0,3,0,3),
   (3,3,0,0),(0,0,3,3),
   (2,3,2,3),(3,2,3,2)))
PROGRAMS=FACTORS+CONTROLS
assert len(FACTORS)==16 and len(CONTROLS)==8
assert len(PROGRAMS)==24 and RESETS==2
assert len({name for name,_ in PROGRAMS})==24
assert all(parse_plan(w)[-1][0]==5 and
    sum(a==6 for a,xy in parse_plan(w))==4 and
    all(a!=6 or xy is not None for a,xy in parse_plan(w))
    for name,w in PROGRAMS)

def first_last_commit(trial):
    items=[e for e in trial["true_native_all_original_action_events"]
        if e["phase"]=="stage2" and e["real_source_action"]==5]
    return [{
        "real_source_action_step":e["phase_step"],
        "actual_original_native_pre_ACTION5_bars":e.get("original_pre_action_bars"),
        "source_returned_SDK_frames":e.get("original_true_SDK_returned_frames"),
        "official_source_level_after":e["source_level_after"],
        "original_source_state_after":e["source_SDK_state_after"],
    } for e in items]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    raw_all={};records=[]
    for name,word in PROGRAMS:
        for replicate in range(RESETS):
            t,raw=play_source(name,word,replicate)
            t["true_native_stage2_final_commit_observations"]=first_last_commit(t)
            records.append(t)
            for k,array in raw.items():
                raw_all[f"{name}_rep{replicate}_{k}"]=array
    by={}
    for name,word in PROGRAMS:
        rows=[t for t in records if t["source_original_program_name"]==name]
        by[name]={
           "original_predeclared_four_bar_action_word":word,
           "source_real_levels_after":[r["official_SDK_final_level"] for r in rows],
           "original_game_states_after":[r["official_SDK_final_state"] for r in rows],
           "original_native_level3_or_WIN":[r["real_sdk_level3_or_win"] for r in rows],
           "source_disposition":[r["source_disposition"] for r in rows],
           "source_last_action_precommit_observations":[
                r["true_native_stage2_final_commit_observations"] for r in rows],
        }
    outcome={
      "kind":"ORIGINAL_SP80_LEVEL2_FOUR_BAR_INDEPENDENT_NATIVE_FACTORIAL",
      "predeclared_native_0_or2_bar_steps":FACTORS,
      "frozen_native_four_bar_boundary_controls":CONTROLS,
      "genuine_original_source_resets_per_program":RESETS,
      "actual_independently_reset_original_games":len(records),
      "source_original_SDK_actions":sum(len(r["true_native_all_original_action_events"]) for r in records),
      "actual_source_level3_or_WIN_trials":sum(int(r["real_sdk_level3_or_win"]) for r in records),
      "native_original_dispositions":dict(Counter(r["source_disposition"] for r in records)),
      "source_per_frozen_four_bar_program":by,
      "unfiltered_genuine_native_original_source_events":records,
      "limitations":"Original public Arcade.NORMAL SDK; full returned source frames, actual native x,y click pixels and genuine SDK levels. Four-color-bar movements are controlled interventions, not assumed game goal or complete engine model. Official SDK level>=3 or WIN is sole success.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_all)
    print("SP80_STAGE2_FOUR_BAR_FACTORIAL "+json.dumps({
        k:v for k,v in outcome.items()
        if k not in ("source_per_frozen_four_bar_program",
                     "unfiltered_genuine_native_original_source_events")
    },sort_keys=True))
    print("SP80_STAGE2_FOUR_BAR_OUTCOMES "+json.dumps({
        k:{"levels":v["source_real_levels_after"],"states":v["original_game_states_after"],
            "commit":v["source_last_action_precommit_observations"]}
        for k,v in by.items()
    },sort_keys=True))
    if len(records)!=len(PROGRAMS)*RESETS:raise RuntimeError("Original source reset shortfall")
if __name__=="__main__":main()
