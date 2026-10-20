"""Original SP80 new SDK level2 witness reproduction and neighboring controls.

SOURCE-OWNED evidence: real original SDK run #39318735025 progressed
stage1->stage2 2/2 for each exact native word:
  F2,L0,U3: 6@24,37 4 4 6@32,25 6@12,17 4 4 4 5
  F2,L2,U3: 6@24,37 4 4 6@32,25 4 4 6@12,17 4 4 4 5
Recheck these identical original programs on FRESH separate native
Arcade.NORMAL resets, and prospectively test L1, F1/F3, U2/U4,
L3/L4, order and early ACTION5 controls. Avoid universal game laws.
Original source SDK level>=2 or WIN alone proves progression.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

CLICK={"F":"6@24,37","L":"6@32,25","U":"6@12,17"}
SOURCE_STAGE2_EXPECTED_SHA256="b23d0e2243bc716d36e8602c7d30758a687250f142263510d2bc36432b5f35b4"
RESETS=2

def program(f,l,u,order="FLU",per_bar_commit=False,skip_lower=False):
    counts={"F":f,"L":l,"U":u}
    tokens=[]
    for bar in order:
        if bar=="L" and skip_lower:continue
        tokens.append(CLICK[bar])
        n=counts[bar]
        tokens.extend(["4" if n>0 else "3"]*abs(n))
        if per_bar_commit:tokens.append("5")
    if not per_bar_commit:tokens.append("5")
    return " ".join(tokens)

CASES=(
 ("replicate_success_A",2,0,3,"FLU",False,False),
 ("replicate_success_B",2,2,3,"FLU",False,False),
 ("between_middle_L1",2,1,3,"FLU",False,False),
 ("negative_middle_L3",2,3,3,"FLU",False,False),
 ("outer_middle_L4",2,4,3,"FLU",False,False),
 ("lower_moved_left_Lminus1",2,-1,3,"FLU",False,False),
 ("first_F1_middle0",1,0,3,"FLU",False,False),
 ("first_F3_middle0",3,0,3,"FLU",False,False),
 ("upper_U2_middle0",2,0,2,"FLU",False,False),
 ("upper_U4_middle0",2,0,4,"FLU",False,False),
 ("first_F1_middle2",1,2,3,"FLU",False,False),
 ("first_F3_middle2",3,2,3,"FLU",False,False),
 ("upper_U2_middle2",2,2,2,"FLU",False,False),
 ("upper_U4_middle2",2,2,4,"FLU",False,False),
 ("reverse_order_ULF_A",2,0,3,"ULF",False,False),
 ("reverse_order_LUF_A",2,0,3,"LUF",False,False),
 ("reverse_order_FUL_A",2,0,3,"FUL",False,False),
 ("reverse_order_ULF_B",2,2,3,"ULF",False,False),
 ("skip_unmoved_middle_click",2,0,3,"FLU",False,True),
 ("per_bar_commit_A",2,0,3,"FLU",True,False),
 ("per_bar_commit_B",2,2,3,"FLU",True,False),
)
PROGRAMS=tuple((name,program(f,l,u,order,per_bar,skipL))
     for name,f,l,u,order,per_bar,skipL in CASES)
assert len(PROGRAMS)==len({name for name,_ in PROGRAMS})==21
assert RESETS==2
assert dict(PROGRAMS)["replicate_success_A"]=="6@24,37 4 4 6@32,25 6@12,17 4 4 4 5"
assert dict(PROGRAMS)["replicate_success_B"]=="6@24,37 4 4 6@32,25 4 4 6@12,17 4 4 4 5"
assert all(parse_plan(w)[-1][0]==5 and
    all(action!=6 or xy is not None for action,xy in parse_plan(w))
    for _,w in PROGRAMS)


def level_observations(trial,frames):
    res=[]
    for e in trial["real_sdk_observation_ledger"]:
        if e.get("phase")!="context":continue
        step=e["phase_action_number"]
        k="context_"+str(step)
        if k not in frames:
            res.append({"action":step,"source_status":"UNKNOWN_NO_FULL_FRAME"});continue
        row={
           "source_context_step":step,
           "native_action":e["native_action_id"],
           "source_clicked_pixel":e["actual_native_pre_click_pixel"],
           "native_click_xy":e["native_click_xy"],
           "actual_original_SDK_level_after":e["original_source_level_after"],
           "actual_original_SDK_game_state_after":e["original_source_state_after"],
           "actual_original_SDK_returned_frames":len(frames[k]),
        }
        if e["native_action_id"]==5:
            row["original_native_final_screen_hash"]=hash_frame(frames[k][-1])
            row["source_real_level2_event"]=int(e["original_source_level_after"])>=2
        res.append(row)
    return res


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    trials,raw={},{}
    result_trials=[]
    for name,word in PROGRAMS:
        for rep in range(RESETS):
            t,frames=one(name,word,rep)
            t["native_checkpoint_replay_events"]=level_observations(t,frames)
            result_trials.append(t)
            for phase,arr in frames.items():
                raw[f"{name}_rep{rep}_{phase}"]=arr
    outcome={}
    for name,word in PROGRAMS:
        rows=[t for t in result_trials if t["name"]==name]
        outcome[name]={
            "original_SDK_program":word,
            "source_original_game_levels":[t["original_last_source_level"] for t in rows],
            "source_original_game_states":[t["original_last_source_state"] for t in rows],
            "source_level2_or_WIN":[t["native_level2_or_win"] for t in rows],
            "source_last_source_dispositions":[t["actual_source_disposition"] for t in rows],
            "actual_SDK_returned_A5_count_and_last_hash":[[
                  [e["actual_original_SDK_returned_frames"],e["original_native_final_screen_hash"]]
                  for e in t["native_checkpoint_replay_events"]
                  if e.get("native_action")==5] for t in rows],
        }
    output={
      "kind":"GENUINE_ORIGINAL_SP80_NEW_STAGE2_ENTRY_REPRODUCTION_AND_NEIGHBORS",
      "source_predeclared_programs":PROGRAMS,
      "independent_real_SDK_resets_per_program":RESETS,
      "real_source_native_original_games":len(result_trials),
      "actual_native_SDK_action_responses":sum(t["actual_native_calls"] for t in result_trials),
      "genuine_original_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in result_trials),
      "actual_native_source_dispositions":dict(Counter(t["actual_source_disposition"] for t in result_trials)),
      "source_real_outcome_by_program":outcome,
      "real_original_SDK_evidence":result_trials,
      "limitation":"New source SDK original game reset trials. Genuine stage2 entry only if official levels_completed>=2 or WIN. 2/6 is not six-level victory, source hidden-state equality or universal mathematics. Every original returned frame in NPZ and source ledger JSON. Preserve negative outcomes and original F3 working world.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_STAGE2_ENTRY_REPRO "+json.dumps({
       k:v for k,v in output.items() if k not in ("real_original_SDK_evidence","source_real_outcome_by_program")
    },sort_keys=True))
    if len(result_trials)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Some original source SDK resets missing")

if __name__=="__main__":
    main()
