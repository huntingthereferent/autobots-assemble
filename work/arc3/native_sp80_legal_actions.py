"""Discover REAL native SP80 stage-1 legal controls and their immediate effects.

Previous original SP80 research concentrated on ACTION4 and ACTION5,
producing exactly supported visible effects but native GAME_OVER with
one of six levels complete. We need actual source-advertised controls,
not a guessed action alphabet or a substitute game.

For each fresh reset, explicitly witness 454545 from level0 to level1.
Record available_actions on stage1 root, then separately probe each
legal, SDK-defined native ACTION1..ACTION8 exactly ONCE from a new
original stage1 root. Two independent source resets per native control.
No active autonomous policy or mechanical hidden-state assumptions.

A control not advertised or absent from native SDK is not executed.
No original API keys, environment GUIDs or scorecard IDs persisted.
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
CANDIDATES=tuple(range(1,9))
RESETS=2


def explicit_state(obs):
    s=getattr(obs,"state",None)
    return str(getattr(s,"name",s)).rsplit(".",1)[-1]


def available(obs):
    return sorted(set(int(getattr(a,"value",a))
                      for a in (getattr(obs,"available_actions",None) or [])))


def frame_sha(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()


def play(candidate,repeat):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Official native SP80 missing")
    obs=env.reset()
    root,info=frame_view(obs)
    if root is None:raise RuntimeError("Native original reset frame unavailable")
    frames=[root]
    prefix_observed=[]
    for step,letter in enumerate(PREFIX,1):
        action=int(letter)
        if action not in available(obs):
            raise RuntimeError("Actual stage1 entry control withdrawn at "+str(step))
        after=env.step(getattr(GameAction,"ACTION"+letter))
        if after is None:raise RuntimeError("Null original stage1 entry response")
        frame,shape=frame_view(after)
        if frame is None:raise RuntimeError("Nonstandard genuine stage1 entry frame")
        prefix_observed.append({
            "step":step,"native_action":action,
            "level":int(getattr(after,"levels_completed",-1)),
            "state":explicit_state(after),
            "frame_hash":frame_sha(frame),
        })
        frames.append(frame)
        obs=after
    level=int(getattr(obs,"levels_completed",-1))
    state=explicit_state(obs)
    if level!=1 or state in ("WIN","GAME_OVER"):
        raise RuntimeError("Genuine stage1 prefix was not witnessed")
    legal=available(obs)
    before=frames[-1]
    output={
        "probe":candidate,"replicate":repeat,
        "genuine_prefix":prefix_observed,
        "stage1_root_level":level,
        "stage1_root_state":state,
        "native_win_levels":int(getattr(obs,"win_levels",-1)),
        "all_genuine_stage1_advertised_native_controls":legal,
        "stage1_root_hash":frame_sha(before),
        "source_enum_has_candidate":hasattr(GameAction,"ACTION"+str(candidate)),
    }
    if candidate not in legal:
        output.update({"disposition":"NOT_ADVERTISED_NO_NATIVE_PROBE",
                       "source_issued_probe_action":False})
        return output,np.stack(frames)
    if not output["source_enum_has_candidate"]:
        output.update({"disposition":"NO_SDK_ENUM_NO_NATIVE_PROBE",
                       "source_issued_probe_action":False})
        return output,np.stack(frames)
    after=env.step(getattr(GameAction,"ACTION"+str(candidate)))
    if after is None:
        output.update({"disposition":"UNKNOWN_NULL_NATIVE_RESPONSE",
                       "source_issued_probe_action":True})
        return output,np.stack(frames)
    grid,shape=frame_view(after)
    output.update({
        "disposition":"REAL_NATIVE_PROBE_EXECUTED",
        "source_issued_probe_action":True,
        "actual_native_action":candidate,
        "after_native_state":explicit_state(after),
        "after_levels_completed":int(getattr(after,"levels_completed",-1)),
        "win_levels":int(getattr(after,"win_levels",-1)),
        "advertised_after_native_controls":available(after),
        "actual_full_frame_available":grid is not None,
        "actual_source_frame_shape":shape,
    })
    if grid is not None:
        frames.append(grid)
        ys,xs=np.nonzero(before!=grid)
        changed=[
            {"xy":[int(x),int(y)],
             "before_native_color":int(before[y,x]),
             "after_native_color":int(grid[y,x])}
            for y,x in zip(ys,xs)
        ]
        output["original_native_changed_pixel_count"]=len(changed)
        output["actual_original_pixel_color_changes"]=changed
        output["original_after_hash"]=frame_sha(grid)
    return output,np.stack(frames)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    records,arrays=[],{}
    for candidate in CANDIDATES:
        for repeat in range(RESETS):
            trial,frames=play(candidate,repeat)
            records.append(trial)
            arrays[f"ACTION{candidate}_reset{repeat}"]=frames
    counts=Counter()
    advertised=set()
    for row in records:
        counts[row["disposition"]]+=1
        advertised.update(row["all_genuine_stage1_advertised_native_controls"])
        if row.get("source_issued_probe_action") and row.get("after_levels_completed",-1)>1:
            counts["native_level2_or_later_advances"]+=1
        if row.get("after_native_state")=="WIN":
            counts["actual_native_wins"]+=1
        if row.get("after_native_state")=="GAME_OVER":
            counts["native_GAME_OVER_probes"]+=1
    output={
        "kind":"ORIGINAL_SP80_STAGE1_ADVERTISED_LEGAL_NATIVE_CONTROL_DISCOVERY",
        "predeclared_candidate_native_action_ids":CANDIDATES,
        "fresh_native_resets_per_candidate":RESETS,
        "actual_original_native_resets":len(records),
        "genuine_stage1_advertised_control_union":sorted(advertised),
        "advertised_but_outside_predeclared_probe_set":sorted(advertised-set(CANDIDATES)),
        "counts":dict(counts),
        "records":records,
        "limits":"Discovery not independently held-out proof; only original public SDK advertised actions probed, from independently witnessed real stage1 root. State and levels_completed govern actual progress, not changed pixels. No synthetic game, bot policy, F3 source equivalence or game-win inference.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_NATIVE_LEGAL_ACTIONS "+json.dumps({
        "resets":len(records),
        "advertised":sorted(advertised),
        "counts":dict(counts),
        "per_candidate":[{
            "control":n,
            "dispositions":[r["disposition"] for r in records if r["probe"]==n],
            "levels":[r.get("after_levels_completed") for r in records if r["probe"]==n],
            "states":[r.get("after_native_state") for r in records if r["probe"]==n],
            "changed_pixels":[r.get("original_native_changed_pixel_count") for r in records if r["probe"]==n]
        } for n in CANDIDATES]
    },sort_keys=True))
    if not records:raise RuntimeError("No original native stage1 probes executed")


if __name__=="__main__":
    main()
