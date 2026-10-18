"""Native SP80: does a witnessed level-0 action relation transfer to level 1?

Source event (previous independently verified official native game):
  native ACTION4,ACTION5 repeated three times => levels_completed 0 -> 1
  on the SIXTH action, GameState.NOT_FINISHED. This is NOT mathematical F3 A.

THIS TEST:
  - Independently reset real SP80 before each trajectory.
  - Repeat the witnessed level-0 prefix (4,5)*3 and REQUIRE native 0 -> 1.
  - Snapshot complete 64x64 native frames, legal controls, color distributions,
    level counter, terminal state, and every intermediate transition.
  - Apply a predeclared suffix from the NEW level-1 root and compare observed
    transition responses with corresponding level-0 prefix transitions.
  - Retest the specific falsifiable transfer hypothesis that (4,5)*3
    advances a second level from level 1, with reversed-word controls.
  - Stop when native counter changes, when action is withdrawn, or when a
    complete frame is not available; mark these cases UNKNOWN as appropriate.

NO saved solver, game source introspection, extra bot, invented F3
projection/quotient, or game-win claim. Native frames are never mapped to F3
colors or coordinates; mathematical Window48 remains a separate source.
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

GAME = "sp80"
PREFIX = "454545"
# Frozen before new native observations. Includes predeclared transfer check,
# short subword and reversed-order controls, and negative single-action probes.
SUFFIXES = (
    "", "4", "5", "45", "54", "4545", "5454",
    "454545", "545454", "444444", "555555"
)
RESETS_PER_SUFFIX = 2
SOURCE_WINDOW48_LAWS = 48


def hash_grid(g):
    return blake2b(np.ascontiguousarray(g).tobytes(),
                   digest_size=16).hexdigest()


def frame_view(obs):
    """Handle SDK animation stacks without treating them as game levels."""
    payload=getattr(obs, "frame", None)
    if payload is None:
        return None, {"frame_status":"MISSING","shape":None,"size":0}
    arr=np.asarray(payload)
    selected=arr[-1] if arr.ndim==3 else arr
    info={"frame_status":"COMPLETE" if selected.size==4096 else "NONSTANDARD",
          "shape":list(arr.shape),"size":int(arr.size),
          "selected_shape":list(selected.shape),
          "selected_size":int(selected.size)}
    if selected.size!=4096:
        return None,info
    grid=selected.reshape(64,64).astype(np.uint8).copy()
    if np.any(grid>15):
        raise ValueError("native palette is not ARC 0..15")
    return grid,info


def meta(obs,grid,frame_info):
    available=sorted({int(getattr(a,"value",a))
                      for a in (getattr(obs,"available_actions",None) or ())})
    return {
        "level":int(getattr(obs,"levels_completed",0)),
        "state":str(getattr(obs,"state",None)),
        "native_available_actions":available,
        **frame_info,
        "full_frame_hash":hash_grid(grid) if grid is not None else None,
        "native_color_counts":{
            str(i):int(np.count_nonzero(grid==i)) for i in range(16)
        } if grid is not None else None,
    }


def difference(before,after):
    if before is None or after is None:
        return None
    changed=(before!=after)
    ys,xs=np.nonzero(changed)
    return {
        "changed_native_pixels":int(np.count_nonzero(changed)),
        "bounding_box":([int(xs.min()),int(ys.min()),
                         int(xs.max()),int(ys.max())] if len(xs) else None),
        "transition_color_exchanges":[
            {"from":int(old),"to":int(new),"count":int(n)}
            for (old,new),n in sorted(Counter(
                (int(before[y,x]),int(after[y,x]))
                for y,x in zip(ys,xs)
            ).items())
        ],
    }


def new_game(arcade):
    env=arcade.make(GAME)
    if env is None:
        raise RuntimeError("official native SP80 unavailable")
    obs=env.reset()
    if obs is None:
        raise RuntimeError("official native reset missing")
    return env,obs


def advance(env,obs,letter,step,phase,frames,events):
    before=frames[-1] if frames else None
    advertised=sorted({int(getattr(a,"value",a))
                       for a in (getattr(obs,"available_actions",None) or ())})
    if int(letter) not in advertised:
        return obs,"UNKNOWN_NATIVE_CONTROL_NOT_ADVERTISED",0
    try:
        after_obs=env.step(getattr(GameAction,"ACTION"+letter))
    except Exception as err:
        events.append({"step":step,"native_action":int(letter),
                       "phase":phase,"error_class":type(err).__name__,
                       "error_message":str(err)[:200]})
        return obs,"UNKNOWN_NATIVE_ACTION_EXCEPTION",0
    if after_obs is None:
        events.append({"step":step,"native_action":int(letter),
                       "phase":phase,"frame_status":"NULL_NATIVE_RESPONSE"})
        return obs,"UNKNOWN_NULL_NATIVE_RESPONSE",1
    after,shape=frame_view(after_obs)
    current=meta(after_obs,after,shape)
    events.append({
        "step":step,"native_action":int(letter),"phase":phase,
        "native_response":current,
        "native_frame_delta":difference(before,after)
    })
    if after is None:
        return after_obs,"UNKNOWN_NONSTANDARD_NATIVE_FRAME",1
    frames.append(after)
    return after_obs,None,1


def execute(arcade,suffix,reset_number):
    env,obs=new_game(arcade)
    initial,info=frame_view(obs)
    if initial is None:
        raise RuntimeError("SP80 native root is not 64x64")
    root=meta(obs,initial,info)
    frames=[initial]
    events=[]
    issued=0
    trouble=None
    # The prefix is OBSERVED, not a native game solution imported to this test.
    for step,letter in enumerate(PREFIX,1):
        obs,problem,n=advance(env,obs,letter,step,"LEVEL0_WITNESS_PREFIX",frames,events)
        issued+=n
        if problem:
            trouble=problem
            break
        if int(getattr(obs,"levels_completed",0))!=0:
            if step!=len(PREFIX):
                trouble="UNEXPECTED_EARLY_LEVEL_CHANGE"
            break
    prefix_stage_complete=(
        trouble is None and len(events)==6 and len(frames)==7
        and int(getattr(obs,"levels_completed",0))==1
        and "WIN" not in str(getattr(obs,"state",None))
    )
    stage1=meta(obs,frames[-1],frame_view(obs)[1]) if prefix_stage_complete else None
    stage1_observation_index=len(frames)-1
    prefix_events=[dict(x) for x in events]
    if not prefix_stage_complete:
        trouble=trouble or "PREFIX_DID_NOT_REACH_NATIVE_LEVEL1"
    if prefix_stage_complete:
        for step,letter in enumerate(suffix,1):
            obs,problem,n=advance(env,obs,letter,len(PREFIX)+step,
                                  "LEVEL1_FROZEN_SUFFIX",frames,events)
            issued+=n
            if problem:
                trouble=problem
                break
            if int(getattr(obs,"levels_completed",0))!=1:
                break
    final_level=int(getattr(obs,"levels_completed",0))
    new_level_after_suffix=prefix_stage_complete and final_level>1
    stage1_effects=events[len(prefix_events):]
    root_effects=prefix_events
    # Compare native transition-level *measurements*, not hidden state,
    # across first and second level; the starting frame need not be equal.
    same_early_effects=[]
    for a,b in zip(root_effects,stage1_effects):
        da=a.get("native_frame_delta")
        db=b.get("native_frame_delta")
        same_early_effects.append({
            "level0_action":a.get("native_action"),
            "level1_action":b.get("native_action"),
            "identical_action_ids":a.get("native_action")==b.get("native_action"),
            "same_pixel_count":da is not None and db is not None and
                                da["changed_native_pixels"]==db["changed_native_pixels"],
            "same_color_exchange_multiset":da is not None and db is not None and
                da["transition_color_exchanges"]==db["transition_color_exchanges"],
            "same_exact_frame_delta_bbox":da is not None and db is not None and
                da["bounding_box"]==db["bounding_box"],
        })
    row={
        "game":GAME,
        "suffix":suffix,"independent_reset_index":reset_number,
        "native_actions_issued":issued,
        "prefix_verified_0_to_1":prefix_stage_complete,
        "actual_level_after_suffix":final_level,
        "second_level_advanced":bool(new_level_after_suffix),
        "native_state_after_suffix":str(getattr(obs,"state",None)),
        "prefix_root":root,
        "stage1_root":stage1,
        "stage1_root_frame_index":stage1_observation_index if stage1 else None,
        "stage1_root_equals_stage0_root_frame":(
            stage1["full_frame_hash"]==root["full_frame_hash"]
            if stage1 else None),
        "stage1_action_sequence":list(map(int,suffix)),
        "native_prefix_events":root_effects,
        "native_stage1_events":stage1_effects,
        "pairwise_initial_step_observational_relation":same_early_effects,
        "status":trouble or ("LEVEL2_OR_HIGHER_ADVANCE" if new_level_after_suffix
                           else "NO_OBSERVED_SECOND_ADVANCE"),
    }
    return row, np.stack(frames)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/window48-sp80-stage-transfer.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    arrays={}
    for suffix in SUFFIXES:
        for reset in range(RESETS_PER_SUFFIX):
            row,raw=execute(arcade,suffix,reset)
            records.append(row)
            arrays[f"after_{suffix or 'EMPTY'}_reset_{reset}"]=raw
    counts=Counter(r["status"] for r in records)
    prefix_count=sum(r["prefix_verified_0_to_1"] for r in records)
    second=[r for r in records if r["second_level_advanced"]]
    stage1_hashes={r["stage1_root"]["full_frame_hash"]
                   for r in records if r["stage1_root"] is not None}
    pre_root_hashes={r["prefix_root"]["full_frame_hash"] for r in records}
    comparison={
        "kind":"ORIGINAL_WINDOW48_F3_NATIVE_SP80_STAGE_TRANSFER",
        "native_game":"sp80",
        "native_provider":"official arc-agi Arcade NORMAL",
        "source_math":"original 48-law window_combined; no attempted F3 role mapping",
        "predeclared_level0_prefix":PREFIX,
        "predeclared_level1_suffixes":list(SUFFIXES),
        "independent_resets_per_suffix":RESETS_PER_SUFFIX,
        "native_actions":sum(r["native_actions_issued"] for r in records),
        "level0_prefix_verified_repeats":prefix_count,
        "stage0_root_hashes":sorted(pre_root_hashes),
        "stage1_root_hashes":sorted(stage1_hashes),
        "stage1_different_from_stage0_visible_frame":all(
            r["stage1_root_equals_stage0_root_frame"] is False
            for r in records if r["stage1_root"] is not None),
        "second_level_progress_trials":len(second),
        "second_level_progressions":[{
            "suffix":r["suffix"],"reset":r["independent_reset_index"],
            "native_level_after":r["actual_level_after_suffix"],
            "native_state":r["native_state_after_suffix"]
        } for r in second],
        "status_counts":dict(counts),
        "per_word_second_level_progress":{
            suffix:sum(r["second_level_advanced"] for r in records
                       if r["suffix"]==suffix)
            for suffix in SUFFIXES
        },
        "observations":records,
        "boundary":(
            "Real public native stage progress measured, not a full game win "
            "or F3-48 state/action correspondence. Word 454545 was discovered "
            "on level 0 in prior documented experiment; frozen suffixes are "
            "tested on the new stage as a transfer hypothesis. All exact "
            "native 64x64 frames and per-step color changes preserved. "
            "No game-source inspection, imitation engine, arbitrary field "
            "projection, hidden-stage inference or competition score."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(comparison,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("WINDOW48_SP80_STAGE_TRANSFER "+json.dumps({
        "native_actions":comparison["native_actions"],
        "independent_resets":len(records),
        "verified_stage0_to_1_prefix":prefix_count,
        "stage0_start_hash_count":len(pre_root_hashes),
        "stage1_start_hash_count":len(stage1_hashes),
        "stage1_is_different_visible_frame":comparison[
            "stage1_different_from_stage0_visible_frame"],
        "second_level_progress_replays":len(second),
        "per_suffix_level2_progress":comparison["per_word_second_level_progress"],
        "status_counts":dict(counts),
        "stage1_initial_delta_examples":[{
            "suffix":r["suffix"],
            "first_effects":r["pairwise_initial_step_observational_relation"][:2]
        } for r in records if r["independent_reset_index"]==0],
        "record":str(args.out),
        "native_raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if prefix_count==0:
        raise RuntimeError("No independently verified stage-1 roots")


if __name__=="__main__":
    main()
