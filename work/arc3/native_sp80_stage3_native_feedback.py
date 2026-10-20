"""Prospective stage3 native feedback trials, original SP80 SDK only.

Stage3 source grid is independently measured in run #39463571663
(two fresh original Arcade.NORMAL games, same root SHA).
Actual source components: selected palette9 [17,17,31,19], palette8
[38,17,52,19], [8,29,16,31], [20,29,28,31],
[44,32,55,34], [38,41,49,43].
These are PIXEL BOUNDING BOXES, not inferred engine objects or rules.

Each prospective control is run on TWO completely new original games.
Only official original SDK level>=4 or WIN is a stage3 advance.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np

from .native_sp80_action5_frame_stacks import native_stack, frame_record_before_after
from .native_sp80_legal_pairs import PREFIX, legal, state, hash_frame
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_entry_source_map import STAGE2_VERIFIED_WORD
from .native_sp80_stage2_source_map import color_components, scene

# Native screen positions, frozen from the independent stage3 original source map.
BANDS=(
    ("selected9",(20,18),9),
    ("upper_right8",(40,18),8),
    ("middle_left8",(10,30),8),
    ("middle_center8",(22,30),8),
    ("lower_right8",(46,33),8),
    ("bottom_right8",(40,42),8),
)
PROPOSALS=(
    ("source_root_pour","5"),
    *(("%s_%s"%(name,direction),"6@%d,%d %s 5"%(xy[0],xy[1],action))
      for name,xy,_ in BANDS
      for direction,action in (("left","3"),("right","4"))),
    ("upper_pair","6@20,18 3 6@40,18 4 5"),
    ("middle_pair","6@10,30 4 6@22,30 3 5"),
    ("lower_pair","6@46,33 3 6@40,42 4 5"),
)
assert len(BANDS)==6
assert len(PROPOSALS)==16==len(set(name for name,_ in PROPOSALS))
assert all(parse_plan(word)[-1][0]==5 for _,word in PROPOSALS)
assert len(STAGE1_WITNESSES)==2
assert all(0<=xy[0]<64 and 0<=xy[1]<64 for _,xy,_ in BANDS)

def real_trial(witness,stage1_word,name,stage3_word):
    original=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=original.make("sp80")
    if env is None:
        raise RuntimeError("Original SP80 SDK game unavailable")
    obs=env.reset()
    frames,shape=native_stack(obs)
    if frames is None or int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Original SDK reset did not return level0")
    prev=np.asarray(frames[-1]).copy()
    stacks={"reset":frames}
    events=[]

    def step(action,xy,phase,index):
        nonlocal obs,prev
        prior_level=int(getattr(obs,"levels_completed",-1))
        prior_state=state(obs)
        advertised=legal(obs)
        if action not in advertised:
            return {"phase":phase,"index":index,"original_action":action,
                    "admission":"UNKNOWN_ACTION_NOT_ADVERTISED",
                    "original_legal_before":advertised},False
        if action==6 and xy is None:
            raise AssertionError("Native SDK click needs actual coordinates")
        before=prev.copy()
        actual_preclick=(int(before[xy[1],xy[0]]) if xy else None)
        kwargs={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy else {}
        result=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if result is None:
            return {"phase":phase,"index":index,"original_action":action,
                    "admission":"UNKNOWN_NULL_SOURCE_RESPONSE"},False
        source_frames,source_shape=native_stack(result)
        row={
            "phase":phase,"index":index,"original_action":action,
            "original_click_xy":list(xy) if xy else None,
            "actual_source_preclick_palette":actual_preclick,
            "actual_source_before_sha":hash_frame(before),
            "official_source_level_before":prior_level,
            "official_source_level_after":int(getattr(result,"levels_completed",-1)),
            "official_source_state_before":prior_state,
            "official_source_state_after":state(result),
            "original_legal_before":advertised,
            "original_legal_after":legal(result),
            "original_SDK_frame_shape":source_shape,
        }
        if source_frames is not None:
            stacks[phase+"_"+str(index)]=source_frames
            row["full_original_source_frame_ledger"]=frame_record_before_after(before,source_frames)
            prev=np.asarray(source_frames[-1]).copy()
            row["actual_source_after_sha"]=hash_frame(prev)
            row["actual_source_after_color9_regions"]=[
                z for z in color_components(prev) if z["palette"]==9
            ]
        else:
            row["admission"]="UNKNOWN_ORIGINAL_SDK_FRAME_FORMAT"
        events.append(row)
        obs=result
        return row,source_frames is not None

    def enter(word,phase,target):
        parts=parse_plan(word)
        for j,(a,xy) in enumerate(parts,1):
            record,admitted=step(a,xy,phase,j)
            if not admitted:
                raise RuntimeError("Original SDK entry not admitted: "+phase)
            expected=target-1 if j<len(parts) else target
            if int(getattr(obs,"levels_completed",-1))!=expected:
                raise RuntimeError("Original SDK entry changed unexpectedly: "+phase)
            if state(obs)!="NOT_FINISHED":
                raise RuntimeError("Original SDK reached terminal during "+phase)

    enter(" ".join(PREFIX),"entry0",1)
    enter(stage1_word,"entry1",2)
    enter(STAGE2_VERIFIED_WORD,"entry2",3)

    root=prev.copy()
    stage3={
        "official_source_level":int(getattr(obs,"levels_completed",-1)),
        "original_state":state(obs),
        "original_source_sha256":hash_frame(root),
        "actual_source_screen":scene(root),
        "actual_original_source_color_components":color_components(root),
        "advertised_SDK_actions":legal(obs),
    }
    if stage3["official_source_level"]!=3:
        raise RuntimeError("No original SDK stage3 source entry")
    disposition="COMPLETE"
    for j,(a,xy) in enumerate(parse_plan(stage3_word),1):
        row,admitted=step(a,xy,"stage3",j)
        if not admitted:
            disposition=row.get("admission","UNKNOWN");break
        if state(obs) in ("WIN","GAME_OVER"):
            disposition="ORIGINAL_TERMINAL_"+state(obs);break
        if int(getattr(obs,"levels_completed",-1))!=3:
            disposition="ORIGINAL_LEVEL_CHANGED";break

    stage3_events=[v for v in events if v["phase"]=="stage3"]
    return {
        "original_entry_witness":witness,
        "frozen_candidate":name,
        "frozen_stage3_word":stage3_word,
        "original_verified_stage3_root":stage3,
        "original_stage3_intervention_events":stage3_events,
        "full_original_sdk_action_events":events,
        "official_original_final_level":int(getattr(obs,"levels_completed",-1)),
        "official_original_final_state":state(obs),
        "official_original_win_levels":int(getattr(obs,"win_levels",-1)),
        "official_original_level4_or_WIN":(
            int(getattr(obs,"levels_completed",-1))>=4 or state(obs)=="WIN"
        ),
        "trial_disposition":disposition,
        "original_source_final_sha":hash_frame(prev),
    },stacks

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    trials=[];source_stacks={}
    for name,program in PROPOSALS:
        for witness,witness_word in STAGE1_WITNESSES:
            row,raw=real_trial(witness,witness_word,name,program)
            trials.append(row)
            for phase,stack in raw.items():
                source_stacks["%s_%s_%s"%(name,witness,phase)]=stack
            print("ORIGINAL_SP80_STAGE3_TRIAL "+json.dumps({
                "candidate":name,"witness":witness,
                "level":row["official_original_final_level"],
                "state":row["official_original_final_state"],
                "disposition":row["trial_disposition"],
                "original_source_stage3_events":len(row["original_stage3_intervention_events"])
            },sort_keys=True))
    hashes={r["original_verified_stage3_root"]["original_source_sha256"] for r in trials}
    if len(trials)!=32 or len(hashes)!=1:
        raise AssertionError("Original independent SDK stage3 entries diverged")
    summary={
        "kind":"ACTUAL_ORIGINAL_SP80_STAGE3_SOURCE_FEEDBACK_CONTRAST",
        "source_stage3_measurement_run":39463571663,
        "original_source_stage3_bands_frozen":BANDS,
        "precommitted_candidate_words":PROPOSALS,
        "original_independently_reset_games":len(trials),
        "original_source_stage3_entry_hash":next(iter(hashes)),
        "actual_original_source_level4_or_WIN":sum(bool(r["official_original_level4_or_WIN"]) for r in trials),
        "original_sdk_final_levels":dict(Counter(str(r["official_original_final_level"]) for r in trials)),
        "original_sdk_dispositions":dict(Counter(r["trial_disposition"] for r in trials)),
        "original_source_successes":[{"candidate":r["frozen_candidate"],
            "witness":r["original_entry_witness"],
            "level":r["official_original_final_level"],
            "state":r["official_original_final_state"],
            "word":r["frozen_stage3_word"]}
            for r in trials if r["official_original_level4_or_WIN"]],
        "all_actual_original_sdk_records":trials,
        "claim_boundary":"Native SDK source controls and returned screens alone. Visual components are not decoded physics; no F3 mapping, no fabricated stage4 and no six-level WIN without official SDK result."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_stacks)
    print("ORIGINAL_SP80_STAGE3_NATIVE_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="all_actual_original_sdk_records"
    },sort_keys=True))
if __name__=="__main__":
    main()
