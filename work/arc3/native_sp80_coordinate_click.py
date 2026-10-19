"""Native SP80: genuine coordinate-bearing ACTION6 selection/progression test.

IMPORTANT CORRECTION TO PRIOR NATIVE RESEARCH:
Arc prize official toolkit specifies ACTION6 is a COMPLEX click action
and needs data={'x': int, 'y': int}. Several historical observation
workers issued ACTION6 with no coordinates and observed its resulting
frames. Those are valid source frames but NOT evidence of an intended
object click. Never silently relabel the old tests.

This source-only experiment reads actual native original frame pixels
at each clicked source coordinate, issues valid data-bearing ACTION6,
then uses official legal native ACTION1..ACTION5 under controlled
fresh stage1 game resets. Compare prior no-click words, background/
UI control clicks, original moving color9 region, original two color8
regions, actual color4/6 HUD pixels and an original color11 top glyph.
Only SDK levels_completed>=2 or WIN establishes native game progress.

No game clones, bots, fabricated success, F3 generator mapping or
hidden game-state interpretations. Persist raw original SDK frames.
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

from .native_sp80_legal_pairs import (
    PREFIX, state, legal, hash_frame, changes)
from .native_sp80_stage_transfer import frame_view
from .native_sp80_overlap_intervention import source_frame_observation

RESETS=2

# All original (x,y) positions are independently native-frame observed.
# Labels describe pre-action pixel SOURCE values; not assumed game mechanics.
TRIALS=(
    ("no_click_lower_control",None,"1115"),
    ("no_click_upper_control",None,"111113335"),
    ("click_color9_body_alone",(24,37),""),
    ("click_color9_body_then_lower",(24,37),"1115"),
    ("click_color9_body_then_A6",(24,37),"1116"),
    ("click_color9_right_side_then_lower",(36,37),"1115"),
    ("click_lower_color8_alone",(32,25),""),
    ("click_lower_color8_then_lower",(32,25),"1115"),
    ("click_upper_color8_then_lower",(12,17),"1115"),
    ("click_lower_color8_then_upper",(32,25),"111113335"),
    ("click_color6_bottom_then_lower",(41,57),"1115"),
    ("click_color4_bottom_then_lower",(41,61),"1115"),
    ("click_color12_background_then_lower",(50,40),"1115"),
    ("click_color11_top_glyph_then_lower",(18,5),"1115"),
    ("click_color9_body_move_right_then_commit",(24,37),"445"),
)
assert len(set(name for name,_,_ in TRIALS))==len(TRIALS)==15
assert all((pos is None or 0<=pos[0]<=63 and 0<=pos[1]<=63)
           and set(suffix)<={"1","2","3","4","5","6"} for _,pos,suffix in TRIALS)


def real_frame_summary(arr):
    frame=source_frame_observation(arr)
    frame["actual_native_color4_count"]=int(np.count_nonzero(arr==4))
    frame["actual_native_color6_count"]=int(np.count_nonzero(arr==6))
    frame["native_top_color11_count"]=int(np.count_nonzero(arr[4:12,12:56]==11))
    return frame


def real_original_session(label,click,suffix,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Original SP80 source SDK game missing")
    obs=env.reset()
    root,metadata=frame_view(obs)
    if root is None:raise RuntimeError("No native reset frame")
    frames=[root]
    entry=[]
    for i,letter in enumerate(PREFIX,1):
        native=int(letter)
        if native not in legal(obs):
            raise RuntimeError("Missing native legal stage1-entry action")
        after=env.step(getattr(GameAction,"ACTION"+letter))
        if after is None:raise RuntimeError("Original native null stage1 entry")
        grid,shape=frame_view(after)
        if grid is None:raise RuntimeError("Native nonstandard stage1 entry")
        frames.append(grid)
        entry.append({
            "action":native,"step":i,"sdk_state":state(after),
            "native_levels_completed":int(getattr(after,"levels_completed",-1)),
            "original_frame_digest":hash_frame(grid),
        })
        obs=after
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Native source 454545 failed stage1 entry")

    source_stage1_root=frames[-1]
    if click is not None and 6 not in legal(obs):
        raise RuntimeError("Official native SDK did not advertise coordinate ACTION6")
    native_sequence=[(6,click)] if click is not None else []
    if "6" in suffix and click is None:
        raise ValueError("Original ACTION6 requires an explicitly predeclared coordinate")
    native_sequence.extend((int(c),click if c=="6" else None) for c in suffix)

    source_ledger=[]
    interruption=None
    for position,(native,xy) in enumerate(native_sequence,1):
        advertised=legal(obs)
        if native not in advertised:
            interruption="NATIVE_ACTION_WITHDRAWN"
            break
        before=frames[-1]
        args={"x":int(xy[0]),"y":int(xy[1])} if native==6 else None
        old_pixel=(int(before[xy[1],xy[0]]) if xy is not None else None)
        action=getattr(GameAction,"ACTION"+str(native))
        after=env.step(action,data=args) if args is not None else env.step(action)
        if after is None:
            interruption="UNKNOWN_NULL_NATIVE_RESPONSE"
            break
        next_level=int(getattr(after,"levels_completed",-1))
        next_state=state(after)
        grid,shape=frame_view(after)
        item={
            "source_context_step":position,
            "native_action_id":native,
            "original_click_xy":list(xy) if xy else None,
            "original_native_pixel_at_click_before":old_pixel,
            "source_advertised_before_action":advertised,
            "before_original_frame_sha":hash_frame(before),
            "after_original_sdk_levels_completed":next_level,
            "after_original_sdk_win_levels":int(getattr(after,"win_levels",-1)),
            "after_original_sdk_state":next_state,
            "native_after_advertised":legal(after),
            "native_after_frame_info":shape,
            "full_original_native_after_frame_available":grid is not None,
        }
        if grid is not None:
            frames.append(grid)
            diff=changes(before,grid)
            item["original_native_pixel_color_changes"]=diff
            item["native_changed_pixel_count"]=len(diff)
            item["original_after_frame_sha"]=hash_frame(grid)
            item["original_preaction_visible"]=real_frame_summary(before)
            item["original_postaction_visible"]=real_frame_summary(grid)
        source_ledger.append(item)
        obs=after
        if next_state in ("WIN","GAME_OVER"):
            interruption="NATIVE_TERMINAL_"+next_state
            break
        if next_level!=1:
            interruption="NATIVE_LEVEL_CHANGED"
            break
        if grid is None:
            interruption="UNKNOWN_ORIGINAL_FRAME"
            break

    last=frames[-1]
    return {
        "label":label,"replicate":replicate,
        "source_action6_click_xy":list(click) if click is not None else None,
        "original_suffix_simple_actions":suffix,
        "authentic_stage1_prefix":entry,
        "original_stage1_root_frame_sha":hash_frame(source_stage1_root),
        "original_root_click_pixel_color":int(source_stage1_root[click[1],click[0]]) if click else None,
        "original_sdk_stage1_legal_actions":legal(obs) if not source_ledger else source_ledger[0]["source_advertised_before_action"],
        "native_original_context_ledger":source_ledger,
        "real_original_sdk_actions_attempted":len(source_ledger),
        "real_original_sdk_actions_with_full_frames":sum(int(q["full_original_native_after_frame_available"]) for q in source_ledger),
        "actual_last_source_level":int(getattr(obs,"levels_completed",-1)),
        "actual_last_source_state":state(obs),
        "native_level2_or_WIN":bool(int(getattr(obs,"levels_completed",-1))>=2 or state(obs)=="WIN"),
        "source_disposition":"COMPLETE" if interruption is None and len(source_ledger)==len(native_sequence) else interruption,
        "source_original_last_frame_sha":hash_frame(last),
    },np.stack(frames)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    records,raw=[],{}
    for name,xy,suffix in TRIALS:
        for reset in range(RESETS):
            trial,frames=real_original_session(name,xy,suffix,reset)
            records.append(trial)
            raw[f"{name}_reset{reset}"]=frames
    table={}
    for label,xy,suffix in TRIALS:
        rows=[q for q in records if q["label"]==label]
        table[label]={
            "click":list(xy) if xy else None,
            "suffix":suffix,
            "source_pixel_clicked":[q["original_root_click_pixel_color"] for q in rows],
            "actual_original_levels":[q["actual_last_source_level"] for q in rows],
            "original_SDK_state":[q["actual_last_source_state"] for q in rows],
            "native_level2_or_WIN":[q["native_level2_or_WIN"] for q in rows],
            "source_action_admissions":[q["real_original_sdk_actions_with_full_frames"] for q in rows],
            "source_disposition":[q["source_disposition"] for q in rows],
            "native_click_changed_cells":[next(
                (a.get("native_changed_pixel_count") for a in q["native_original_context_ledger"] if a["native_action_id"]==6),
                None) for q in rows],
            "original_final_color9_xy":[(q["native_original_context_ledger"][-1].get("original_postaction_visible",{}).get("native_color9_xy_bounds")
                                         if q["native_original_context_ledger"] else None) for q in rows],
        }
    out={
        "kind":"SP80_OFFICIAL_ORIGINAL_NATIVE_DATA_BEARING_ACTION6_SELECTION",
        "original_public_SDK_action6_contract":"Must specify data={'x':int,'y':int}; old no-coordinate tests are not valid location-specific controls",
        "predeclared_spatial_click_controls":TRIALS,
        "native_independent_games_per_control":RESETS,
        "real_original_native_stage1_resets":len(records),
        "real_valid_stage1_native_actions":sum(q["real_original_sdk_actions_with_full_frames"] for q in records),
        "actual_source_level2_or_WIN":sum(int(q["native_level2_or_WIN"]) for q in records),
        "source_dispositions":dict(Counter(q["source_disposition"] for q in records)),
        "source_per_control":table,
        "original_native_source_trials":records,
        "limits":"Genuine original SDK coordinate click and native states/levels, no inferred selection mechanics or goal from colors. Only positive level2 or WIN reports constitute success; never treat old coordinate-free action6 as same experiment. No F3 law, solver bot, cloned SP80 or competition score.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_COORDINATE_ACTION6 "+json.dumps({
        k:v for k,v in out.items() if k!="original_native_source_trials"},
        sort_keys=True))
    if len(records)!=len(TRIALS)*RESETS:
        raise RuntimeError("Incomplete official original native click trials")


if __name__=="__main__":
    main()
