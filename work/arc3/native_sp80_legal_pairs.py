"""Bounded genuine SP80 stage1 pair-composition discovery.

Public original ARC SDK stage1 actually advertises native controls 1..6.
Prior individual action probes witnessed 161,161,33,33,1,1 first-use
changed original pixels, but revealed NO game level progress.

Predeclare 12 original two-action native words with pairs, reversed
order and independent cross-axis controls. From a new original native
reset for EACH trial, reproduce the real 454545 stage1-entry witness.
Execute word ONLY as actions remain SDK advertised; stop on a genuine
WIN, GAME_OVER, or native level change. Capture exact full 64x64 before
and after frames and compare interior y1..62 to original stage1 ROOT.

This is DISCOVERY, not a frozen solver, proposed F3 correspondence or
proof that controls with equal first-use changed pixels are inverses.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import blake2b
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_sp80_stage_transfer import frame_view

PREFIX="454545"
WORDS=(
    "12","21","34","43","56","65",
    "14","41","23","32","45","54"
)
RESETS=2
assert len(WORDS)==len(set(WORDS))==12
assert all(len(w)==2 and set(w)<={"1","2","3","4","5","6"} for w in WORDS)


def state(obs):
    s=getattr(obs,"state",None)
    return str(getattr(s,"name",s)).rsplit(".",1)[-1]


def legal(obs):
    return sorted(set(int(getattr(a,"value",a))
                      for a in (getattr(obs,"available_actions",None) or [])))


def hash_frame(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()


def changes(a,b):
    ys,xs=np.nonzero(a!=b)
    return [{"xy":[int(x),int(y)],
             "before":int(a[y,x]),"after":int(b[y,x])}
            for y,x in zip(ys,xs)]


def one(word,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Original native game unavailable")
    obs=env.reset()
    root,info=frame_view(obs)
    if root is None:raise RuntimeError("Genuine native reset without complete frame")
    frames=[root]
    entry=[]
    for i,letter in enumerate(PREFIX,1):
        aid=int(letter)
        if aid not in legal(obs):
            raise RuntimeError("Genuine level1 witness control withdrawn")
        obs=env.step(getattr(GameAction,"ACTION"+letter))
        if obs is None:raise RuntimeError("Null real native stage1 entry")
        arr,shape=frame_view(obs)
        if arr is None:raise RuntimeError("Original real native stage1 entry missing frame")
        frames.append(arr)
        entry.append({"action":aid,"step":i,"level":int(getattr(obs,"levels_completed",-1)),
                      "state":state(obs),"frame_sha":hash_frame(arr)})
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Native 454545 failed to yield level1 root")
    stage1_root=frames[-1]
    available_at_start=legal(obs)
    effects=[]
    interrupted=None
    progress=False
    for i,letter in enumerate(word,1):
        aid=int(letter)
        old=frames[-1]
        advertised_before=legal(obs)
        if aid not in advertised_before:
            interrupted="NATIVE_ACTION_WITHDRAWN"
            effects.append({"context_step":i,"native_action":aid,
                            "status":interrupted,"advertised_before":advertised_before})
            break
        if not hasattr(GameAction,"ACTION"+letter):
            interrupted="NATIVE_ENUM_MISSING"
            break
        after=env.step(getattr(GameAction,"ACTION"+letter))
        if after is None:
            interrupted="UNKNOWN_NULL_NATIVE_RESPONSE"
            break
        next_state=state(after)
        next_level=int(getattr(after,"levels_completed",-1))
        arr,shape=frame_view(after)
        row={
            "context_step":i,"native_action":aid,
            "previous_frame_sha":hash_frame(old),
            "advertised_before":advertised_before,
            "official_after_state":next_state,
            "official_after_levels_completed":next_level,
            "win_levels":int(getattr(after,"win_levels",-1)),
            "advertised_after":legal(after),
            "native_frame_info":shape,
            "native_complete_frame":arr is not None,
        }
        if arr is not None:
            frames.append(arr)
            delta=changes(old,arr)
            row["native_changed_pixel_count"]=len(delta)
            row["actual_original_pixel_color_changes"]=delta
            row["after_frame_sha"]=hash_frame(arr)
            row["original_interior_matches_stage1_root"]=bool(
                np.array_equal(arr[1:63],stage1_root[1:63]))
            row["original_interior_changed_cells_from_stage1_root"]=int(
                np.count_nonzero(arr[1:63]!=stage1_root[1:63]))
            row["original_bottom_row_changed_cells_from_stage1_root"]=int(
                np.count_nonzero(arr[63]!=stage1_root[63]))
        effects.append(row)
        obs=after
        progress=(next_level>1 or next_state=="WIN")
        if next_state in ("WIN","GAME_OVER"):
            interrupted="NATIVE_TERMINAL_"+next_state
            break
        if next_level!=1:
            interrupted="NATIVE_LEVEL_CHANGED"
            break
        if arr is None:
            interrupted="UNKNOWN_NONSTANDARD_NATIVE_FRAME"
            break
    ending=frames[-1]
    out={
        "word":word,"replicate":replicate,"genuine_stage1_entry":entry,
        "original_stage1_root_sha":hash_frame(stage1_root),
        "official_stage1_root_advertised_native_controls":available_at_start,
        "original_sdk_steps_after_stage1_entry":len(effects),
        "actual_accepted_complete_native_action_frames":sum(int(e.get("native_complete_frame",False)) for e in effects),
        "source_effects":effects,
        "status":"COMPLETE" if interrupted is None and len(effects)==len(word) else interrupted,
        "progress_to_level2_or_native_WIN":bool(progress),
        "last_reported_native_level":int(getattr(obs,"levels_completed",-1)),
        "last_reported_native_state":state(obs),
        "final_available_native_actions":legal(obs),
        "final_original_frame_hash":hash_frame(ending),
        "entire_original_interior_restored_to_stage1_root":bool(
            np.array_equal(ending[1:63],stage1_root[1:63])),
        "entire_original_full_frame_restored_to_stage1_root":bool(
            np.array_equal(ending,stage1_root)),
        "original_interior_pixels_different_from_root":int(
            np.count_nonzero(ending[1:63]!=stage1_root[1:63])),
        "original_boundary_y63_pixels_different_from_root":int(
            np.count_nonzero(ending[63]!=stage1_root[63])),
    }
    return out,np.stack(frames)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    records,raw=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            result,frames=one(word,replicate)
            records.append(result)
            raw[f"word_{word}_reset{replicate}"]=frames
    counts=Counter(r["status"] for r in records)
    outcomes={
        "kind":"OFFICIAL_NATIVE_SP80_STAGE1_TWO_ACTION_COMPOSITION_DISCOVERY",
        "precommitted_genuine_two_action_words":WORDS,
        "fresh_original_native_resets_per_word":RESETS,
        "total_original_native_resets":len(records),
        "total_level2_or_WIN_observed":sum(int(r["progress_to_level2_or_native_WIN"]) for r in records),
        "status_counts":dict(counts),
        "each_word":{
            w:{
                "reset_count":RESETS,
                "any_level2_or_WIN":any(r["progress_to_level2_or_native_WIN"]
                                        for r in records if r["word"]==w),
                "interior_restored":[r["entire_original_interior_restored_to_stage1_root"]
                                      for r in records if r["word"]==w],
                "interior_mismatch_counts":[r["original_interior_pixels_different_from_root"]
                                            for r in records if r["word"]==w],
                "boundary_mismatch_counts":[r["original_boundary_y63_pixels_different_from_root"]
                                            for r in records if r["word"]==w],
                "last_levels":[r["last_reported_native_level"]
                               for r in records if r["word"]==w],
                "native_states":[r["last_reported_native_state"]
                                 for r in records if r["word"]==w],
            } for w in WORDS
        },
        "original_source_trials":records,
        "limits":"Discovery on authentic stage1 SP80 normal-mode native actions1..6, not a general autonomous solver, F3 source-law action identity or proof of inverse controls. Terminal WIN or GAME_OVER must be actually observed; exact native frame changes remain original-source evidence.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcomes,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_NATIVE_TWO_ACTION_PAIRS "+json.dumps({
        k:v for k,v in outcomes.items() if k!="original_source_trials"},sort_keys=True))
    if not records:raise RuntimeError("No actual native stage1 pairing evidence")


if __name__=="__main__":
    main()
