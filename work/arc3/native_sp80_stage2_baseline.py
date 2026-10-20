"""Real original SP80: first source-authenticated level2 baseline and action probes.

Two genuine stage1->2 words witnessed on independent native run
#39318735025. This obtains level2 only via actual SDK stage0 454545
then the exact witnessed stage1 route, never by constructing a scene.

Prospectively freeze a two-witness × [read-only or first native
ACTION1..5] × two independent original Arcade.NORMAL resets design.
Record actual level2 source frame, advertised legal controls, every
original obs.frame in NPZ, old/new XY/color per returned frame, source
SDK levels_completed, WIN/GAME_OVER and source game state. An action
not advertised is recorded UNKNOWN, not forced; genuine level3/WIN
would be recognized ONLY by the public SDK. No source-engine inference.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from .native_sp80_action5_frame_stacks import native_stack,frame_record_before_after
from .native_sp80_legal_pairs import PREFIX,state,legal,hash_frame
from .native_sp80_multi_select import parse_plan

STAGE1_WITNESSES=(
 ("A","6@24,37 4 4 6@32,25 6@12,17 4 4 4 5"),
 ("B","6@24,37 4 4 6@32,25 4 4 6@12,17 4 4 4 5"),
)
STAGE2_FIRST_ACTIONS=(0,1,2,3,4,5)
RESETS=2
assert len(STAGE1_WITNESSES)==2 and RESETS==2
assert all(parse_plan(s)[-1][0]==5 for _,s in STAGE1_WITNESSES)


def original_selected_regions(frame):
    out={}
    for (name,y0,y1) in (("top",0,13),("upper_bar",13,24),
                          ("middle_bar",24,36),("lower_bar",36,48),
                          ("frontier",48,64)):
        region=frame[y0:y1]
        out[name]={
            str(c):int(np.count_nonzero(region==c))
            for c in (6,8,9,11,13,14)
        }
    ys,xs=np.nonzero(frame==9)
    out["selected_color9_bbox"]=(
      [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
      if len(xs) else None)
    out["source_unique_palette_colors"]=sorted(int(c) for c in np.unique(frame))
    return out


def native_probe(witness,word,probe,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Missing genuine SDK original SP80")
    obs=env.reset()
    frames,meta=native_stack(obs)
    if frames is None or int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Original SP80 source reset not admitted")
    raw={"reset":frames}
    previous=frames[-1]
    events=[]
    def step(action,coords,phase,i):
        nonlocal obs,previous
        before_level=int(getattr(obs,"levels_completed",-1))
        before_state=state(obs)
        permitted=legal(obs)
        if action not in permitted:
            return {"phase":phase,"step":i,"native_action":action,
                    "disposition":"UNKNOWN_NOT_ADVERTISED",
                    "original_native_available_actions":permitted},False
        kwargs=({"data":{"x":int(coords[0]),"y":int(coords[1])}}
                if coords else {})
        if action==6 and coords is None:
            raise AssertionError("Native ACTION6 requires actual SDK coords")
        pre_click=(int(previous[coords[1],coords[0]]) if coords else None)
        result=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if result is None:
            return {"phase":phase,"step":i,"native_action":action,
                    "disposition":"UNKNOWN_NULL_SDK_RESULT"},False
        stack,info=native_stack(result)
        actual_state=state(result)
        actual_level=int(getattr(result,"levels_completed",-1))
        event={
            "phase":phase,"phase_step":i,"native_action":action,
            "source_click_xy":list(coords) if coords else None,
            "actual_original_pixel_under_click":pre_click,
            "official_SDK_level_before":before_level,
            "official_SDK_level_after":actual_level,
            "official_SDK_state_before":before_state,
            "official_SDK_state_after":actual_state,
            "original_legal_actions_before":permitted,
            "original_legal_actions_after":legal(result),
            "actual_source_frame_shape":info,
        }
        if stack is not None:
            raw[phase+"_"+str(i)]=stack
            event["full_returned_original_frame_ledger"]=frame_record_before_after(previous,stack)
            previous=stack[-1]
            event["last_native_64x64_hash"]=hash_frame(previous)
        else:
            event["native_frame_admission"]="UNKNOWN_NONSTANDARD_OR_TERMINAL"
        events.append(event)
        obs=result
        return event,stack is not None

    for i,a in enumerate(PREFIX,1):
        event,ok=step(int(a),None,"entry",i)
        if not ok or state(obs) in ("WIN","GAME_OVER"):
            raise RuntimeError("Source stage0->1 prefix did not produce valid original frames")
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Source native stage1 not reached")
    for i,(action,coords) in enumerate(parse_plan(word),1):
        event,ok=step(action,coords,"witness",i)
        if not ok or int(getattr(obs,"levels_completed",-1))!=(
             1 if i<len(parse_plan(word)) else 2):
            raise RuntimeError("Source exact stage1->2 witness failed "+witness)
        if state(obs) in ("WIN","GAME_OVER"):
            raise RuntimeError("Original witness did not produce continuing level2 state")
    if int(getattr(obs,"levels_completed",-1))!=2:
        raise AssertionError("Official SDK did not reach genuine level2")
    baseline_image=previous.copy()
    level2={
        "actual_original_level2_source_frame_hash":hash_frame(baseline_image),
        "actual_original_level2_source_color_regions":original_selected_regions(baseline_image),
        "genuine_source_available_level2_actions":legal(obs),
        "official_SDK_level2_state":state(obs),
        "actual_original_level2_WIN_levels":int(getattr(obs,"win_levels",-1)),
        "stage2_original_native_last_frame_shape":[64,64],
    }
    admitted=True
    if probe:
        event,admitted=step(probe,None,"stage2",1)
    return {
        "original_witness":witness,
        "stage1_native_program":word,
        "prospectively_chosen_first_stage2_action":probe,
        "original_independent_reset":replicate,
        "genuine_stage2_baseline":level2,
        "actual_official_final_levels_completed":int(getattr(obs,"levels_completed",-1)),
        "actual_official_final_state":state(obs),
        "actual_sdk_level3_or_WIN":bool(int(getattr(obs,"levels_completed",-1))>=3 or state(obs)=="WIN"),
        "stage2_probe_admission":("SOURCE_READ_ONLY" if probe==0 else
             "NATIVE_ACCEPTED" if admitted else event.get("disposition","UNKNOWN")),
        "source_real_sdk_action_events":events,
        "original_source_final_frame_hash":hash_frame(previous),
    },raw


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,frames=[],{}
    for witness,word in STAGE1_WITNESSES:
        for probe in STAGE2_FIRST_ACTIONS:
            for rep in range(RESETS):
                t,raw=native_probe(witness,word,probe,rep)
                trials.append(t)
                frames.update({f"{witness}_stage2probe{probe}_rep{rep}_{k}":v
                        for k,v in raw.items()})
    by={}
    for probe in STAGE2_FIRST_ACTIONS:
        group=[t for t in trials if t["prospectively_chosen_first_stage2_action"]==probe]
        by[str(probe)]={
            "genuine_original_games":len(group),
            "official_stage2_legal_action_sets":[t["genuine_stage2_baseline"]["genuine_source_available_level2_actions"] for t in group],
            "stage2_entry_screen_hash":[t["genuine_stage2_baseline"]["actual_original_level2_source_frame_hash"] for t in group],
            "native_final_levels":[t["actual_official_final_levels_completed"] for t in group],
            "native_final_states":[t["actual_official_final_state"] for t in group],
            "source_stage2_action_admissions":[t["stage2_probe_admission"] for t in group],
            "source_stage2_outcome_screen_hash":[t["original_source_final_frame_hash"] for t in group],
        }
    result={
        "kind":"ORIGINAL_SP80_SDK_LEVEL2_ENTRY_NATIVE_LEGAL_ACTION_BASELINE",
        "frozen_genuine_witnesses":STAGE1_WITNESSES,
        "prospective_first_stage2_native_actions":STAGE2_FIRST_ACTIONS,
        "fresh_source_resets_per_witness_action":RESETS,
        "native_independent_original_game_resets":len(trials),
        "genuine_original_SDK_action_responses":sum(len(t["source_real_sdk_action_events"]) for t in trials),
        "source_achieved_level2_entry":sum(t["genuine_stage2_baseline"]["official_SDK_level2_state"]=="NOT_FINISHED" for t in trials),
        "actual_stage2_sdk_level3_or_WIN":sum(int(t["actual_sdk_level3_or_WIN"]) for t in trials),
        "source_stage2_probe_summary":by,
        "all_original_SDK_native_trial_evidence":trials,
        "limits":"Original source stage2 only reached by repeated genuine SDK witnessed stage0 and stage1 routes. Only source SDK levels>=3 or WIN counts progress. Read-only source state/image data not hidden goal evidence. Real SDK full returned frames archived.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("SP80_STAGE2_NATIVE_BASELINE "+json.dumps({
      k:v for k,v in result.items() if k!="all_original_SDK_native_trial_evidence"
    },sort_keys=True))
    if len(trials)!=len(STAGE1_WITNESSES)*len(STAGE2_FIRST_ACTIONS)*RESETS:
        raise AssertionError("Incomplete source SDK stage2 observations")

if __name__=="__main__":main()
