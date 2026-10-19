"""Native original SP80: multiple genuine coordinate-bearing ACTION6 object selections.

Previous original public SDK #181 witnessed proper coordinate-bearing
ACTION6 at color8 original bars: 48 native8->9, 80 native9->8 and one
native14->0 cell; real original stage1 highlight moved to clicked bar.
Earlier no-coordinate ACTION6 attempts were incomplete click tests.
Here test source-legal multi-object selection, movement and ACTION5
without assuming bar mechanics, an objective, hidden state or any game win.

All source action words are FROZEN before new original Arcade.NORMAL
execution, and every ACTION6 ALWAYS includes real data={'x','y'}.
Every source click records the actual clicked PRE-action native pixel.
A precommitted coordinate may hit a different color after movement:
that is evidence, not a failed assertion or presumed selection.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_sp80_legal_pairs import PREFIX, state, legal, hash_frame, changes
from .native_sp80_stage_transfer import frame_view
from .native_sp80_coordinate_click import real_frame_summary

# Tokens 1..5 are true simple native actions. 6@x,y is REQUIRED format
# for every genuine original SDK coordinate-based selection.
PLANS=(
    ("no_click_simple_control","1 1 1 5"),
    ("lower_move_left3_commit","6@32,25 3 3 3 5"),
    ("upper_move_right3_commit","6@12,17 4 4 4 5"),
    ("lower_upper_commit","6@32,25 6@12,17 5"),
    ("upper_lower_commit","6@12,17 6@32,25 5"),
    ("lower_move3_upper_move2_commit","6@32,25 3 3 3 6@12,17 4 4 5"),
    ("upper_move3_lower_move2_commit","6@12,17 4 4 4 6@32,25 3 3 5"),
    ("first_move_up3_lower_move2_commit","6@24,37 1 1 1 6@32,25 3 3 5"),
    ("first_move_up3_upper_move2_commit","6@24,37 1 1 1 6@12,17 4 4 5"),
    ("lower_upper_first_commit","6@32,25 3 3 6@12,17 4 4 6@24,37 1 1 5"),
    ("upper_lower_first_commit","6@12,17 4 4 6@32,25 3 3 6@24,37 1 1 5"),
    ("lower_upper_lower_commit","6@32,25 6@12,17 6@32,25 5"),
    ("upper_lower_upper_commit","6@12,17 6@32,25 6@12,17 5"),
    ("background_lower_upper_commit","6@50,40 6@32,25 3 3 6@12,17 4 4 5"),
    ("all_three_clicks_commit","6@24,37 6@32,25 6@12,17 5"),
    ("lower_move4_upper_move4_commit","6@32,25 3 3 3 3 6@12,17 4 4 4 4 5"),
    ("upper_move4_lower_move4_commit","6@12,17 4 4 4 4 6@32,25 3 3 3 3 5"),
)
RESETS=2
assert len(PLANS)==len(set(x for x,_ in PLANS))==17
assert RESETS==2


def parse_plan(text):
    parsed=[]
    for raw in text.split():
        if raw.startswith("6@"):
            coords=raw[2:].split(",")
            if len(coords)!=2:raise ValueError("Bad native click coords")
            x,y=map(int,coords)
            if not (0<=x<64 and 0<=y<64):
                raise ValueError("Out of bounds original SDK click")
            parsed.append((6,(x,y)))
        elif raw in ("1","2","3","4","5"):
            parsed.append((int(raw),None))
        else:
            raise ValueError("Unsupported native action token: "+raw)
    return parsed


assert all(len(parse_plan(steps))>=3 for _,steps in PLANS)
assert all(not (action==6 and xy is None)
           for _,steps in PLANS for action,xy in parse_plan(steps))


def session(name,script,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Original public native SP80 unavailable")
    obs=env.reset()
    reset,meta=frame_view(obs)
    if reset is None:raise RuntimeError("No native reset frame")
    frames=[reset]
    entry=[]
    for i,ch in enumerate(PREFIX,1):
        aid=int(ch)
        if aid not in legal(obs):
            raise RuntimeError("Original stage1 entry action not advertised")
        after=env.step(getattr(GameAction,"ACTION"+ch))
        if after is None:raise RuntimeError("Native null stage1 entry")
        grid,shape=frame_view(after)
        if grid is None:raise RuntimeError("Native incomplete stage1 entry")
        frames.append(grid)
        entry.append({"sdk_action_index":i,"action":aid,"native_level":int(getattr(after,"levels_completed",-1)),
                      "sdk_state":state(after),"frame_hash":hash_frame(grid)})
        obs=after
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Actual 454545 did not enter native stage1")

    actions=parse_plan(script)
    original_stage1_root_sha=hash_frame(frames[-1])
    events=[]
    disposition=None
    for index,(aid,point) in enumerate(actions,1):
        if aid not in legal(obs):
            disposition="NATIVE_ACTION_WITHDRAWN";break
        old=frames[-1]
        kwargs={"data":{"x":int(point[0]),"y":int(point[1])}} if aid==6 else {}
        before_click_color=int(old[point[1],point[0]]) if point else None
        after=env.step(getattr(GameAction,"ACTION"+str(aid)),**kwargs)
        if after is None:
            disposition="UNKNOWN_NULL_ORIGINAL_NATIVE_RESPONSE";break
        grid,info=frame_view(after)
        source_level=int(getattr(after,"levels_completed",-1))
        sdk_state=state(after)
        row={
            "context_action_index":index,"actual_native_action_id":aid,
            "actual_original_SDK_coordinate_argument":list(point) if point else None,
            "original_clicked_pixel_color_before":before_click_color,
            "actual_legal_actions_before":legal(obs),
            "original_source_before_frame_hash":hash_frame(old),
            "original_native_after_frame_info":info,
            "source_full_frame_available":grid is not None,
            "original_after_levels_completed":source_level,
            "original_after_state":sdk_state,
            "original_win_levels":int(getattr(after,"win_levels",-1)),
        }
        if grid is not None:
            frames.append(grid)
            diff=changes(old,grid)
            row["actual_changed_native_pixel_color_pairs"]=diff
            row["native_changed_pixel_count"]=len(diff)
            row["native_after_frame_hash"]=hash_frame(grid)
            row["original_preaction_visible"]=real_frame_summary(old)
            row["original_postaction_visible"]=real_frame_summary(grid)
        events.append(row)
        obs=after
        if sdk_state in ("WIN","GAME_OVER"):
            disposition="NATIVE_TERMINAL_"+sdk_state;break
        if source_level!=1:
            disposition="NATIVE_LEVEL_CHANGED";break
        if grid is None:
            disposition="UNKNOWN_NONSTANDARD_NATIVE_FRAME";break

    return {
        "name":name,"frozen_source_tokens":script,"replicate":replicate,
        "stage1_witnessed_entry":entry,
        "native_source_root_hash":original_stage1_root_sha,
        "genuine_action_records":events,
        "actual_actions_with_full_native_frames":sum(int(x["source_full_frame_available"]) for x in events),
        "original_native_last_sdk_state":state(obs),
        "original_native_last_level":int(getattr(obs,"levels_completed",-1)),
        "original_native_level2_or_WIN":bool(state(obs)=="WIN" or int(getattr(obs,"levels_completed",-1))>=2),
        "source_disposition":"COMPLETE" if disposition is None and len(events)==len(actions) else disposition,
        "last_source_native_frame_hash":hash_frame(frames[-1]),
    },np.stack(frames)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    trials,raw=[],{}
    for name,program in PLANS:
        for replicate in range(RESETS):
            record,frames=session(name,program,replicate)
            trials.append(record)
            raw[f"{name}_{replicate}"]=frames
    summary={}
    for name,program in PLANS:
        rows=[t for t in trials if t["name"]==name]
        summary[name]={
            "program":program,
            "genuine_resets":len(rows),
            "actual_source_actions":[t["actual_actions_with_full_native_frames"] for t in rows],
            "native_dispositions":[t["source_disposition"] for t in rows],
            "last_native_levels":[t["original_native_last_level"] for t in rows],
            "last_native_states":[t["original_native_last_sdk_state"] for t in rows],
            "genuine_level2_or_WIN":[t["original_native_level2_or_WIN"] for t in rows],
            "actual_coordinate_clicks":[[{"xy":e["actual_original_SDK_coordinate_argument"],
                "native_before_color":e["original_clicked_pixel_color_before"],
                "native_changed_cells":e.get("native_changed_pixel_count"),
                "after_visible_color9_bbox":e.get("original_postaction_visible",{}).get("native_color9_xy_bounds")}
                for e in t["genuine_action_records"] if e["actual_native_action_id"]==6]
                for t in rows],
            "original_color9_final_bbox":[t["genuine_action_records"][-1].get("original_postaction_visible",{}).get("native_color9_xy_bounds")
                 if t["genuine_action_records"] else None for t in rows],
        }
    out={
        "kind":"SP80_ORIGINAL_NATIVE_MULTIPLE_COORDINATE_OBJECT_SELECTION",
        "genuinely_frozen_click_and_movement_programs":PLANS,
        "original_game_resets_per_program":RESETS,
        "genuine_original_native_resets":len(trials),
        "original_full_frame_context_actions":sum(t["actual_actions_with_full_native_frames"] for t in trials),
        "actual_source_level2_or_WIN":sum(int(t["original_native_level2_or_WIN"]) for t in trials),
        "real_source_dispositions":dict(Counter(t["source_disposition"] for t in trials)),
        "per_program":summary,
        "original_native_evidence":trials,
        "limits":"Official original Arcade.NORMAL SDK, coordinate-bearing data for EVERY source ACTION6, genuine entered stage1, actual WIN/levels only. Precommitted screen coordinates may land on different native colors after movement. No source F3 mathematical mapping, hidden state or inferred game win.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_MULTI_SELECT "+json.dumps(
        {k:v for k,v in out.items() if k!="original_native_evidence"},
        sort_keys=True))
    if len(trials)!=len(PLANS)*RESETS:
        raise RuntimeError("Missing genuine native game resets")


if __name__=="__main__":
    main()
