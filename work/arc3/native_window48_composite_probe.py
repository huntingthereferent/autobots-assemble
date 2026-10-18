"""Window48 / real ARC — TWO-action native macro A³ preflight.

Reuses the original window_combined source's order-three requirement without
claiming native actions correspond to A/B. Exhaustively tests all distinct
ordered pairs of advertised simple native controls at ALL public game roots.
For W=ij (i != j), perform W, W², W³ on the actual official native game.

Predeclared observable projections:
  * entire 64x64 native frame
  * EACH individual native 0..15 color's exact binary 64x64 mask
No pixels, colors, positions or world laws are reduced modulo three.
A strict visible 3-cycle requires 0, W, W² distinct and W³=0.

A discovered mask cycle is an exploratory factor candidate, not F3
alignment; replicate on independent reset for TWO successive full orbits,
and test after a single distinct advertised control as a second starting
context. All native actions and raw native observations are retained.
No puzzle solution, fabricated game engine, heuristic solver or scoring.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import blake2b
from itertools import permutations
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from work.arc_like_maze.window_combined import family
from work.arc3.native_window48_roster_preflight import (
    native_grid, digest, frame_state, legal_ids, roster,
)

SIMPLE_IDS = (1, 2, 3, 4, 5)
MAX_MACRO_LEN = 2
PRIMARY_MACRO_REPETITIONS = 3
REPLICATION_REPETITIONS = 6
OBSERVABLE_COLORS = tuple(range(16))


def source_requirement():
    worlds=family()
    if len(worlds)!=48:
        raise AssertionError("Not original Window48")
    for world in worlds:
        root=(0,0,0)
        values=[world.apply(root,"A"*n) for n in range(4)]
        if len(set(values[:3]))!=3 or values[0]!=values[3]:
            raise AssertionError("Source F3 A strict rooted third-power changed")
    return {"original_worlds":48,
            "original_math":"work/arc_like_maze/window_combined.py",
            "source_condition":"A(root), AA(root), root pairwise distinct; AAA(root)=root"}


def exact_mask_hash(frame, native_color):
    return blake2b(np.ascontiguousarray(frame == native_color,
                                       dtype=np.uint8).tobytes(),
                   digest_size=16).hexdigest()


def observables(frame):
    return {
        "whole":digest(frame),
        "per_native_color_mask":{
            str(color):exact_mask_hash(frame,color)
            for color in OBSERVABLE_COLORS
        },
        "native_color_counts":{
            str(color):int(np.count_nonzero(frame==color))
            for color in OBSERVABLE_COLORS
        },
    }


def classify_orbit(values):
    if len(values)<4:
        return "UNKNOWN_INCOMPLETE"
    if values[3]!=values[0]:
        return "THREE_MACRO_RETURN_REFUTED"
    if len(set(values[:3]))==3:
        return "STRICT_PERIOD_THREE_VISIBLE"
    return "DEGENERATE_VISIBLE_RETURN"


def run_native(arcade,game,word,repeat, *, context=None):
    env=arcade.make(game)
    if env is None:
        return {"status":"UNKNOWN_GAME_UNAVAILABLE"}, []
    obs=env.reset()
    if obs is None or getattr(obs,"frame",None) is None:
        return {"status":"UNKNOWN_ROOT_FRAME_UNAVAILABLE"}, []
    root_state=int(getattr(obs,"levels_completed",0))
    states=[]
    frames=[]
    actual_actions=0
    letters=([context] if context is not None else []) + list(word)*repeat
    start_after_context=1 if context is not None else 0
    macro_endpoints=[]
    interruption=None
    for i in range(len(letters)+1):
        if i==0:
            g=native_grid(obs)
            frames.append(g)
            states.append({"step":0,"action":None,"level":root_state,
                           "state":str(getattr(obs,"state",None)),
                           "observables":observables(g)})
        if i==start_after_context or (
                i>start_after_context and
                (i-start_after_context)%len(word)==0):
            macro_endpoints.append(i)
        if i==len(letters):
            break
        native_action=letters[i]
        if native_action not in legal_ids(obs):
            interruption="UNKNOWN_CONTROL_WITHDRAWN"
            break
        try:
            obs=env.step(getattr(GameAction,f"ACTION{native_action}"))
            actual_actions+=1
        except Exception as exc:
            interruption="UNKNOWN_NATIVE_ACTION_EXCEPTION"
            states.append({"error":str(exc)[:260],
                           "error_class":type(exc).__name__})
            break
        if obs is None or getattr(obs,"frame",None) is None:
            interruption="UNKNOWN_FRAMELESS_NATIVE_ACTION"
            break
        g=native_grid(obs)
        frames.append(g)
        current_level=int(getattr(obs,"levels_completed",0))
        states.append({"step":i+1,"action":native_action,
                       "level":current_level,
                       "state":str(getattr(obs,"state",None)),
                       "observables":observables(g)})
        if current_level!=root_state:
            interruption="UNKNOWN_LEVEL_CHANGED"
            break
    # Only complete native trials support positive or negative equality.
    complete=(interruption is None and len(frames)==len(letters)+1)
    row={
        "word":list(word),"context_action":context,
        "repetitions_requested":repeat,
        "actions_executed":actual_actions,
        "status":"COMPLETE" if complete else interruption,
        "complete":complete,
        "macro_endpoint_frame_indices":macro_endpoints,
        "observations":states,
    }
    if complete:
        row["macro_whole_hashes"]=[
            states[idx]["observables"]["whole"] for idx in macro_endpoints]
        row["macro_native_color_mask_hashes"]={
            str(c):[states[idx]["observables"]["per_native_color_mask"][str(c)]
                    for idx in macro_endpoints]
            for c in OBSERVABLE_COLORS}
        row["macro_native_color_sizes"]={
            str(c):[states[idx]["observables"]["native_color_counts"][str(c)]
                    for idx in macro_endpoints]
            for c in OBSERVABLE_COLORS}
        if repeat==3:
            row["full_frame_classification"]=classify_orbit(
                row["macro_whole_hashes"])
            row["mask_classifications"]={
                str(c):classify_orbit(row["macro_native_color_mask_hashes"][str(c)])
                for c in OBSERVABLE_COLORS}
            row["strict_native_color_candidates"]=[
                c for c in OBSERVABLE_COLORS
                if row["mask_classifications"][str(c)] ==
                   "STRICT_PERIOD_THREE_VISIBLE"]
    return row,frames


def replicate_candidate(arcade,game,word,candidates,legal_root,raw):
    """Fresh reset: six repeated macro operations, independent from discovery.

    A second context may be tested only when another simple control is
    advertised. No context control is assigned mathematical B.
    """
    results=[]
    checks=[("replication_root",None)]
    other=next((n for n in legal_root if n in SIMPLE_IDS and n not in word),None)
    if other is not None:
        checks.append(("second_observed_context",other))
    for label,context in checks:
        row,frames=run_native(
            arcade,game,word,REPLICATION_REPETITIONS,context=context)
        row["kind"]=label
        row["predeclared_native_color_candidates"]=list(candidates)
        confirmed={}
        if row.get("complete"):
            for c in candidates:
                hashes=row["macro_native_color_mask_hashes"][str(c)]
                # Two full orbits and no accidental early return:
                confirmed[str(c)]=(
                    len(hashes)==7 and len(set(hashes[:3]))==3 and
                    all(hashes[n]==hashes[n%3] for n in range(7))
                )
        row["six_macro_native_cycle_reproduced"]=confirmed
        results.append(row)
        if frames:
            key=f"{game}_{''.join(map(str,word))}_{label}"
            raw[key]=np.stack(frames)
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/window48-native-composite-A3.json"))
    args=p.parse_args()
    math=source_requirement()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    games=roster(arcade)
    if not games:
        raise RuntimeError("official native public game roster empty")

    root_roster=[]
    probes=[]
    replications=[]
    raw={}
    for game in games:
        try:
            env=arcade.make(game)
            if env is None:
                root_roster.append({"game":game,"status":"UNKNOWN_NO_GAME"})
                continue
            root_obs=env.reset()
            if root_obs is None or getattr(root_obs,"frame",None) is None:
                root_roster.append({"game":game,"status":"UNKNOWN_NO_ROOT"})
                continue
            root=native_grid(root_obs)
            legal=[a for a in SIMPLE_IDS if a in legal_ids(root_obs)]
            root_roster.append({
                "game":game,"status":"OBSERVED_NATIVE_ROOT",
                "available_native_controls":legal_ids(root_obs),
                "root_hash":digest(root),
                "ordered_distinct_two_action_macro_count":len(legal)*(len(legal)-1),
            })
            raw[f"{game}_root"]=root
            for word in permutations(legal,2):
                trial,frames=run_native(arcade,game,word,
                                        PRIMARY_MACRO_REPETITIONS)
                trial["game"]=game
                probes.append(trial)
                if frames:
                    raw[f"{game}_macro_{word[0]}{word[1]}"]=np.stack(frames)
                if trial.get("complete") and (
                    trial["full_frame_classification"] ==
                        "STRICT_PERIOD_THREE_VISIBLE" or
                    bool(trial["strict_native_color_candidates"])):
                    candidates=trial["strict_native_color_candidates"]
                    trial["needs_native_cycle_replication"]=True
                    second=replicate_candidate(arcade,game,word,
                                               candidates,legal,raw)
                    replications.append({
                        "game":game,"macro":list(word),
                        "full_frame_candidate":trial[
                            "full_frame_classification"] ==
                            "STRICT_PERIOD_THREE_VISIBLE",
                        "root_mask_candidates":candidates,
                        "replicated_native_tests":second,
                    })
        except Exception as exc:
            root_roster.append({
                "game":game,"status":"UNKNOWN_NATIVE_EXCEPTION",
                "error_class":type(exc).__name__,
                "error_message":str(exc)[:260],
            })
    statuses=Counter(row["status"] for row in probes)
    whole=Counter(row.get("full_frame_classification")
                  for row in probes if row.get("complete"))
    masks=Counter(value for row in probes if row.get("complete")
                  for value in row["mask_classifications"].values())
    result={
        "kind":"WINDOW48_NATIVE_ORDERED_TWO_ACTION_MACRO_SCREEN",
        "source_math":math,
        "public_native_environment":"official arc-agi Arcade NORMAL",
        "game_roster":games,
        "observed_native_roots":root_roster,
        "predeclared_macro_family":"all ordered DISTINCT pairs of native ACTION1..5 advertised at root",
        "predeclared_projections":"all 16 unmodified native color masks and entire exact 64x64 frame",
        "primary_macro_repetitions":3,
        "replication_macro_repetitions":6,
        "primary_probes":probes,
        "replication_of_exploratory_color_candidates":replications,
        "native_actions_total":(
            sum(x["actions_executed"] for x in probes) +
            sum(x["actions_executed"] for r in replications
                for x in r["replicated_native_tests"])
        ),
        "probe_status_counts":dict(statuses),
        "complete_whole_frame_orbits":dict(whole),
        "complete_per_native_color_mask_orbits":dict(masks),
        "limitations":(
            "Predeclared two-action macros and native color masks are exploratory "
            "projections. A strict native mask cycle even if replicated does "
            "NOT establish a Window48 F3 generator, a closed invariant factor, "
            "a native-action role identification, or hidden-state equivalence. "
            "A mask may omit history/counters; full native frames stay separate. "
            "No pixel or field modulo, game solution, hidden test or ARC win. "
            "Incomplete/level-changing trajectories remain UNKNOWN."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    if raw:
        np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("WINDOW48_NATIVE_COMPOSITES "+json.dumps({
        "games_roster":len(games),
        "root_count":sum(x["status"]=="OBSERVED_NATIVE_ROOT" for x in root_roster),
        "probe_count":len(probes),
        "total_native_actions":result["native_actions_total"],
        "probe_statuses":dict(statuses),
        "whole_frame_orbits":dict(whole),
        "mask_orbits":dict(masks),
        "exploratory_strict_cycle_candidates":[{
            "game":x["game"],"macro":x["macro"],
            "native_colors":x["root_mask_candidates"],
            "full_frame_candidate":x["full_frame_candidate"],
            "replication":[{
                "kind":r["kind"],
                "status":r["status"],
                "confirmed":r["six_macro_native_cycle_reproduced"],
            } for r in x["replicated_native_tests"]]
        } for x in replications],
        "unknown_probes":[{
            "game":x.get("game"),"word":x.get("word"),
            "status":x["status"]} for x in probes
            if x["status"]!="COMPLETE"],
        "record":str(args.out),
        "raw_native_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if not any(x["status"]=="COMPLETE" for x in probes):
        raise RuntimeError("No complete native composite probes; preserve evidence")


if __name__=="__main__":
    main()
