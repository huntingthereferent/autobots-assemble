"""Verify independent native sp80 level transition observed by macro screen.

The earlier 25-game source-rooted F3-48 composite screen interrupted the
sp80 ordered native 4,5 macro on a level change. THIS IS A SEPARATE ACTUAL
NATIVE evidence check; no game solution was obtained from saved ARC routes,
game source, web hints, or simulator. Execute predeclared controls from clean
resets and report exact first transition plus status.

If levels_completed rises, that is actual native progression evidence; a
level change or nonterminal game state is NOT automatically a full game win,
and in no case proves an F3 generator/correspondence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_window48_roster_preflight import (
    native_grid,digest,legal_ids,frame_state
)

GAME="sp80"
# Frozen prior to this independent replay. The original trial considered
# three repetitions of 4,5, thus six native actions.
WORDS=("4","5","45","54","44","55","4545","5454","454545","545454","444444","555555")
INDEPENDENT_RESETS_EACH=2


def replay(arcade,word,run_index):
    env=arcade.make(GAME)
    if env is None:
        raise RuntimeError("official native sp80 game unavailable")
    obs=env.reset()
    if obs is None or getattr(obs,"frame",None) is None:
        raise RuntimeError("actual native sp80 root is missing")
    root_level=int(getattr(obs,"levels_completed",0))
    frames=[native_grid(obs)]
    steps=[{
        "step":0,"native_action":None,
        **frame_state(obs)
    }]
    error=None
    actions_issued=0
    for j,letter in enumerate(word,1):
        n=int(letter)
        if n not in legal_ids(obs):
            error="NATIVE_ACTION_WITHDRAWN"
            break
        try:
            obs=env.step(getattr(GameAction,"ACTION"+letter))
            actions_issued+=1
        except Exception as exc:
            error=f"NATIVE_EXCEPTION_{type(exc).__name__}"
            break
        if obs is None:
            error="NATIVE_NULL_RESPONSE"
            break

        # A completed level/game may return a nonstandard native frame.
        # Read the *actual native level counter and terminal state FIRST*.
        stage={
            "step":j,"native_action":n,
            "levels_completed":int(getattr(obs,"levels_completed",0)),
            "state":str(getattr(obs,"state",None)),
            "advertised_native_actions":legal_ids(obs),
        }
        payload=getattr(obs,"frame",None)
        if payload is None:
            stage.update({"frame_status":"NO_FRAME","frame_shape":None,
                          "frame_size":0,"frame_hash":None})
            steps.append(stage)
            error="NATIVE_FRAMELESS_RESPONSE"
            if stage["levels_completed"]!=root_level:
                error="LEVEL_CHANGED_WITHOUT_FRAME"
            break
        image=np.asarray(payload)
        stage["frame_shape"]=list(image.shape)
        stage["frame_size"]=int(image.size)
        # ARC may return an animation stack [n,64,64] for ACTION5;
        # the declared native observation is its LAST full 64x64 frame.
        final_visible=image[-1] if image.ndim==3 else image
        stage["selected_native_frame_shape"]=list(final_visible.shape)
        stage["selected_native_frame_size"]=int(final_visible.size)
        if final_visible.size!=4096:
            stage.update({"frame_status":"NONSTANDARD_NATIVE_FRAME",
                          "frame_hash":None})
            steps.append(stage)
            error=("LEVEL_CHANGED_NONSTANDARD_FRAME" if
                   stage["levels_completed"]!=root_level
                   else "NONSTANDARD_NATIVE_FRAME")
            break
        g=native_grid(obs)
        stage.update({
            "frame_status":"COMPLETE_64x64",
            "frame_hash":digest(g),
            "different_full_frame_from_previous":bool(
                not np.array_equal(frames[-1],g)),
            "changed_cells":int(np.count_nonzero(frames[-1]!=g)),
        })
        frames.append(g)
        steps.append(stage)
        if stage["levels_completed"]!=root_level:
            error="LEVEL_COUNT_CHANGED_STOP"
            break
    last_level=steps[-1]["levels_completed"]
    return {
        "game":GAME,"word":word,"independent_reset_index":run_index,
        "native_action_count":actions_issued,
        "requested_action_count":len(word),
        "root_hash":steps[0]["frame_hash"],
        "root_levels_completed":root_level,
        "last_levels_completed":last_level,
        "first_level_change_at_action":next(
            (x["step"] for x in steps
             if x["levels_completed"]!=root_level),None),
        "actual_level_progression":last_level>root_level,
        "terminal_native_state":steps[-1]["state"],
        "status":error or "COMPLETE_NO_LEVEL_CHANGE",
        "native_steps":steps,
    },np.stack(frames)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/window48-sp80-level-recheck.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    raw={}
    for word in WORDS:
        for i in range(INDEPENDENT_RESETS_EACH):
            row,frames=replay(arcade,word,i)
            records.append(row)
            raw[f"{word}_reset_{i}"]=frames
    root_hashes=sorted({r["root_hash"] for r in records})
    progress=[r for r in records if r["actual_level_progression"]]
    summary={
        "game":GAME,
        "kind":"INDEPENDENT_NATIVE_SP80_LEVEL_CHANGE_VERIFICATION",
        "predeclared_words":list(WORDS),
        "resets_per_word":INDEPENDENT_RESETS_EACH,
        "roots_identical":len(root_hashes)==1,
        "root_hashes":root_hashes,
        "native_actions":sum(r["native_action_count"] for r in records),
        "actual_level_progression_replays":len(progress),
        "word_progress_counts":{
            w:sum(r["actual_level_progression"] for r in records
                  if r["word"]==w) for w in WORDS},
        "progress_details":[{
            "word":r["word"],
            "reset_index":r["independent_reset_index"],
            "action_index":r["first_level_change_at_action"],
            "before_level":r["root_levels_completed"],
            "after_level":r["last_levels_completed"],
            "terminal_game_state":r["terminal_native_state"],
        } for r in progress],
        "observations":records,
        "meaning":(
            "Actual official native public game observations. A rising "
            "levels_completed number is evidence of native LEVEL progress "
            "but not a full game win or F3 mathematics. A level change "
            "immediately ends this bounded replay; no trained ARC solver, "
            "saved route, replacement environment, arbitrary F3 projection "
            "or leaderboard claim."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("WINDOW48_SP80_NATIVE_LEVEL_RECHECK "+json.dumps({
        "game":GAME,
        "independent_resets":len(records),
        "same_start_frame":summary["roots_identical"],
        "native_actions":summary["native_actions"],
        "level_progress_replays":summary["actual_level_progression_replays"],
        "word_progress_counts":summary["word_progress_counts"],
        "progress_details":summary["progress_details"],
        "incomplete":[{
            "word":r["word"],"reset":r["independent_reset_index"],
            "status":r["status"],
        } for r in records
            if r["status"] not in ("COMPLETE_NO_LEVEL_CHANGE",
                                   "LEVEL_COUNT_CHANGED_STOP")],
        "record":str(args.out),
        "raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))


if __name__=="__main__":
    main()
