"""Original SP80 SDK: authentic level2 coordinate-click inventory.

Requires actual NORMAL mode level0->1 prefix and independently witnessed
level1->2 source word A or B on EACH fresh original game reset. At the
native level2 SDK entry frame, prospectively test ACTION6 with real x/y
on the three observed color8 bands, the selected color9 band, white
top glyphs and a background control. Matched bar-click+ACTION4 and
bar-click+ACTION5 controls test whether stage2 selection persists.

Capture every genuine SDK obs.frame returned image (including every
intermediate), each changed x/y/native before/after color, actual SDK
levels_completed/WIN, official available_actions, actual pre-click
pixel and full-screen selected-color9 bbox.

This tests native *selection behavior*, not a guessed stage3 objective,
the original game engine source, or the separate F3 mathematical world.
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

# Coordinates refer ONLY to real original stage2 screen.
# Observed from authenticated stage2 entry run #39357759294:
# upper color8 x8..23,y20..23; middle color8 x40..59,y28..31;
# lower color8 x8..31,y32..35; selected color9 x36..59,y40..43.
FROZEN_CLICK_CONTROLS=(
    ("upper_color8","6@12,21"),
    ("middle_color8","6@44,29"),
    ("lower_color8","6@12,33"),
    ("already_selected_color9","6@40,41"),
    ("top_white_left","6@14,5"),
    ("top_white_center","6@30,5"),
    ("top_white_right","6@46,5"),
    ("background","6@62,50"),
    ("upper_then_right","6@12,21 4"),
    ("middle_then_right","6@44,29 4"),
    ("lower_then_right","6@12,33 4"),
    ("selected_then_right","6@40,41 4"),
    ("upper_then_commit","6@12,21 5"),
    ("middle_then_commit","6@44,29 5"),
    ("lower_then_commit","6@12,33 5"),
    ("selected_then_commit","6@40,41 5"),
)
RESETS=2
assert len(FROZEN_CLICK_CONTROLS)==16
assert len({name for name,_ in FROZEN_CLICK_CONTROLS})==16
assert len(STAGE1_WITNESSES)==2 and RESETS==2
assert all(parse_plan(word)[0][0]==6 and
           all(a!=6 or xy is not None for a,xy in parse_plan(word))
           for _,word in FROZEN_CLICK_CONTROLS)

def color9_bbox(frame):
    y,x=np.nonzero(frame==9)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None

def count_palette(frame):
    return {str(k):int(np.count_nonzero(frame==k)) for k in (6,8,9,11,13,14)}

def trial(witness_name,witness_word,control_name,control_word,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None: raise RuntimeError("Authentic original SP80 SDK unavailable")
    obs=env.reset()
    stack,meta=native_stack(obs)
    if stack is None or int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Original SP80 reset did not return valid source root")
    raw={"reset":stack}
    previous=stack[-1]
    events=[]
    def take(action,coords,phase,step):
        nonlocal obs,previous
        before_level=int(getattr(obs,"levels_completed",-1))
        before_state=state(obs)
        actions=legal(obs)
        if action not in actions:
            return {"phase":phase,"step":step,"native_action":action,
                    "admission":"UNKNOWN_SOURCE_ACTION_NOT_ADVERTISED",
                    "SDK_advertised_before":actions},False
        if action==6 and coords is None:
            raise AssertionError("Every authentic ACTION6 requires native x/y")
        before=previous.copy()
        click_pixel=int(before[coords[1],coords[0]]) if coords else None
        kwargs={"data":{"x":int(coords[0]),"y":int(coords[1])}} if coords else {}
        after=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if after is None:
            return {"phase":phase,"step":step,"native_action":action,
                    "admission":"UNKNOWN_NULL_ORIGINAL_SDK_RESPONSE"},False
        frames,info=native_stack(after)
        row={
           "phase":phase,"phase_step":step,
           "native_action":action,
           "native_click_xy":list(coords) if coords else None,
           "original_native_preclick_color":click_pixel,
           "source_SDK_level_before":before_level,
           "source_SDK_level_after":int(getattr(after,"levels_completed",-1)),
           "source_SDK_state_before":before_state,
           "source_SDK_state_after":state(after),
           "source_SDK_win_levels":int(getattr(after,"win_levels",-1)),
           "source_original_legal_before":actions,
           "source_original_legal_after":legal(after),
           "source_actual_frame_shape":info,
           "source_preimage_hash":hash_frame(before),
           "source_preimage_color9_bbox":color9_bbox(before),
           "source_preimage_palette":count_palette(before),
        }
        if frames is not None:
            raw[phase+"_"+str(step)]=frames
            row["full_original_SDK_frame_ledger"]=frame_record_before_after(previous,frames)
            previous=frames[-1]
            row["source_postimage_hash"]=hash_frame(previous)
            row["source_postimage_color9_bbox"]=color9_bbox(previous)
            row["source_postimage_palette"]=count_palette(previous)
        else:
            row["admission"]="UNKNOWN_NONSTANDARD_FRAMES_OR_NATIVE_TERMINAL"
        events.append(row)
        obs=after
        return row,frames is not None

    for i,a in enumerate(PREFIX,1):
        entry,admitted=take(int(a),None,"entry",i)
        if not admitted or state(obs) in ("GAME_OVER","WIN"):
            raise RuntimeError("No genuine native 0->1 source entry")
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Authentic source level1 entry absent")

    for i,(a,xy) in enumerate(parse_plan(witness_word),1):
        record,admitted=take(a,xy,"witness",i)
        if not admitted:
            raise RuntimeError("Original SDK stage1->2 witness not accepted")
        expected_level=1 if i<len(parse_plan(witness_word)) else 2
        if int(getattr(obs,"levels_completed",-1))!=expected_level:
            raise RuntimeError("Authentic original SDK stage2 witness did not advance as recorded")
        if state(obs)!="NOT_FINISHED":
            raise RuntimeError("Unexpected terminal on original stage2-entry witness")
    level2_frame=previous.copy()
    level2_entry={
        "source_original_level2_sha":hash_frame(level2_frame),
        "source_original_color9_bbox":color9_bbox(level2_frame),
        "source_original_available_actions":legal(obs),
        "source_original_level2_palette":count_palette(level2_frame),
        "source_original_level":int(getattr(obs,"levels_completed",-1)),
    }
    context_status="COMPLETE"
    for i,(a,xy) in enumerate(parse_plan(control_word),1):
        record,admitted=take(a,xy,"stage2",i)
        if not admitted:
            context_status=record.get("admission","UNKNOWN");break
        if state(obs) in ("WIN","GAME_OVER"):
            context_status="NATIVE_TERMINAL_"+state(obs);break
        if int(getattr(obs,"levels_completed",-1))!=2:
            context_status="NATIVE_LEVEL_CHANGED";break

    stage2_events=[e for e in events if e["phase"]=="stage2"]
    return {
       "witness":witness_name,"witness_stage1_source_word":witness_word,
       "frozen_level2_control":control_name,
       "frozen_level2_action_word":control_word,
       "genuine_fresh_original_reset":replicate,
       "source_genuine_level2_entry":level2_entry,
       "source_SDK_actions_accepted":len(events),
       "original_source_final_level":int(getattr(obs,"levels_completed",-1)),
       "original_source_final_state":state(obs),
       "source_level3_or_WIN":int(getattr(obs,"levels_completed",-1))>=3 or state(obs)=="WIN",
       "source_stage2_control_disposition":context_status,
       "stage2_native_observations":stage2_events,
       "full_original_SDK_action_records":events,
       "original_final_source_frame_hash":hash_frame(previous),
    },raw

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,source_arrays=[],{}
    for witness,word in STAGE1_WITNESSES:
      for name,control in FROZEN_CLICK_CONTROLS:
        for rep in range(RESETS):
          row,raw=trial(witness,word,name,control,rep)
          trials.append(row)
          for phase,stack in raw.items():
            source_arrays[f"{witness}_{name}_rep{rep}_{phase}"]=stack

    by_name={}
    for name,word in FROZEN_CLICK_CONTROLS:
        rows=[t for t in trials if t["frozen_level2_control"]==name]
        by_name[name]={
           "precommitted_original_stage2_word":word,
           "genuine_independent_game_reset_count":len(rows),
           "original_entry_frame_hashes":[r["source_genuine_level2_entry"]["source_original_level2_sha"] for r in rows],
           "real_source_level3_or_WIN":[r["source_level3_or_WIN"] for r in rows],
           "original_final_SDK_levels":[r["original_source_final_level"] for r in rows],
           "original_final_SDK_states":[r["original_source_final_state"] for r in rows],
           "source_SDK_dispositions":[r["source_stage2_control_disposition"] for r in rows],
           "native_original_stage2_effects":[r["stage2_native_observations"] for r in rows],
        }
    out={
       "kind":"GENUINE_SP80_ORIGINAL_LEVEL2_COORDINATE_CLICK_INVENTORY",
       "predeclared_native_stage1_entry_witnesses":STAGE1_WITNESSES,
       "predeclared_stage2_click_and_first_control_words":FROZEN_CLICK_CONTROLS,
       "independent_resets_per_witness_and_control":RESETS,
       "genuine_original_SDK_games":len(trials),
       "accepted_original_SDK_native_actions":sum(t["source_SDK_actions_accepted"] for t in trials),
       "real_source_stage2_clicks":sum(int(e["native_action"]==6) for t in trials for e in t["stage2_native_observations"]),
       "genuine_SDK_stage2_entries":sum(t["source_genuine_level2_entry"]["source_original_level"]==2 for t in trials),
       "actual_original_level3_or_WIN":sum(int(t["source_level3_or_WIN"]) for t in trials),
       "source_dispositions":dict(Counter(t["source_stage2_control_disposition"] for t in trials)),
       "real_source_per_coordinate_control":by_name,
       "complete_original_native_sdk_records":trials,
       "limits":"Actual original SP80 Arcade.NORMAL SDK; stage2 reached through authentic SDK 0->1 and 1->2 actions on every reset. Real ACTION6 coordinates and clicked original pixel colors required. Selection is visible source observation, not a decoded objective. SDK level3/WIN alone defines actual progress; retain all native returned frames and original source records. No cloned game or separate F3 mathematical-law assertion.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_arrays)
    print("SP80_STAGE2_CLICK_INVENTORY "+json.dumps({
       k:v for k,v in out.items()
       if k not in ("real_source_per_coordinate_control","complete_original_native_sdk_records")
    },sort_keys=True))
    print("SP80_STAGE2_CLICK_EFFECTS "+json.dumps({
      name:[{
        "witness":r["witness"],"reset":r["genuine_fresh_original_reset"],
        "native_preclick_color":r["stage2_native_observations"][0].get("original_native_preclick_color") if r["stage2_native_observations"] else None,
        "source_pre_bbox":r["stage2_native_observations"][0].get("source_preimage_color9_bbox") if r["stage2_native_observations"] else None,
        "source_post_bbox":r["stage2_native_observations"][0].get("source_postimage_color9_bbox") if r["stage2_native_observations"] else None,
        "source_click_changed_pixels":r["stage2_native_observations"][0].get("full_original_SDK_frame_ledger",{}).get("original_before_to_final_pixel_count") if r["stage2_native_observations"] else None,
        "source_final_level":r["original_source_final_level"],
      } for r in trials if r["frozen_level2_control"]==name]
      for name,_ in FROZEN_CLICK_CONTROLS
    },sort_keys=True))
    if len(trials)!=len(STAGE1_WITNESSES)*len(FROZEN_CLICK_CONTROLS)*RESETS:
        raise RuntimeError("Incomplete original SDK level2 source inventory")

if __name__=="__main__":
    main()
