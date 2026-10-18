"""Source-derived F3 word equality probes on independent public native ARC games.

The original 9 F3 worlds and their *separating word probes* determine the
investigation, not game-specific ARC advice. Two native simple controls are
provisionally assigned to letters A/B only as a FALSIFIABLE hypothesis.

This does not run a solver, replay a historical winning path, modify F3,
reduce observed colors modulo 3, or identify equal visible frames with equal
hidden game states. Full native observations are retained.
"""
from __future__ import annotations

import argparse
from hashlib import blake2b, sha256
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from work.arc_like_maze.math import inverse_candidates
from work.arc_like_maze.relation_probe import separating_probes


# These actual public native games were selected from the repo's existing
# ARC research inventory BEFORE observing their results here.
GAMES = ("ft09", "sk48")
MAX_SOURCE_PROBES = 4
MAX_WORD_LENGTH = 18
ACTUATION_KINDS = tuple(range(1, 6))


def frame_grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:
        a=a[-1]
    if a.size!=4096:
        raise ValueError("official observation not a 64x64 frame")
    b=a.reshape(64,64)
    if np.any(b<0) or np.any(b>15):
        raise ValueError("native color outside 0..15")
    return b.astype(np.uint8).copy()


def digest(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()


def native_metadata(obs,a):
    return {
        "whole_frame_hash":digest(a),
        "levels_completed":int(getattr(obs,"levels_completed",0)),
        "state":str(getattr(obs,"state",None)),
        "advertised_native_actions":[int(getattr(n,"value",n))
             for n in (getattr(obs,"available_actions",[]) or [])],
        "native_color_counts":{str(int(v)):int(n)
             for v,n in zip(*np.unique(a,return_counts=True))}
    }


def define_math_probe_words():
    worlds=inverse_candidates()
    separating=separating_probes(worlds)
    # Two universal constraints that apply to ALL original worlds are sampled
    # before any family-specific separating questions.
    constraints=[("", "AAA"),("AB","BA")]
    family=[]
    for pair in separating:
        if max(map(len,pair))>MAX_WORD_LENGTH:
            continue
        if pair in constraints:
            continue
        family.append(pair)
        if len(family)==MAX_SOURCE_PROBES:
            break
    # No need to query words beyond the predeclared short sourced comparisons.
    pairs=constraints+family
    words=sorted({w for pair in pairs for w in pair},
                 key=lambda w:(len(w),w))
    exact_reference=[
        {"phi":list(w.phi),
         "word_equalities":[w.apply(a)==w.apply(b) for a,b in pairs]}
        for w in worlds]
    return pairs,words,exact_reference,len(separating)


def choose_two_controls(obs):
    listed={int(getattr(a,"value",a)) for a in
            (getattr(obs,"available_actions",[]) or [])}
    simple=tuple(a for a in ACTUATION_KINDS if a in listed)
    if len(simple)<2:
        return None
    return simple[:2]


def native_root(arcade,game):
    env=arcade.make(game)
    if env is None:
        raise RuntimeError("native game unavailable")
    obs=env.reset()
    if obs is None or getattr(obs,"frame",None) is None:
        raise RuntimeError("native reset frame missing")
    return env,obs,frame_grid(obs)


def execute_word(arcade,game,word,roles):
    env,obs,root=native_root(arcade,game)
    observed=[root]
    transitions=[]
    initial_level=int(getattr(obs,"levels_completed",0))
    reason=None
    for i,letter in enumerate(word,1):
        assigned=roles[0 if letter=="A" else 1]
        available={int(getattr(a,"value",a)) for a in
                   (getattr(obs,"available_actions",[]) or [])}
        if assigned not in available:
            reason="NATIVE_ACTION_NOT_ADVERTISED"
            break
        before=observed[-1]
        next_obs=env.step(getattr(GameAction,f"ACTION{assigned}"))
        if next_obs is None or getattr(next_obs,"frame",None) is None:
            reason="NO_NATIVE_SUCCESSOR_FRAME"
            break
        after=frame_grid(next_obs)
        observed.append(after)
        yy,xx=np.nonzero(before!=after)
        transitions.append({
            "letter":letter,"native_action":assigned,"step":i,
            "changed_cells":len(xx),
            "diff_bbox":[int(xx.min()),int(yy.min()),
                         int(xx.max()),int(yy.max())] if len(xx) else None,
            "before_hash":digest(before),"after_hash":digest(after),
            "level_after":int(getattr(next_obs,"levels_completed",0)),
            "state_after":str(getattr(next_obs,"state",None)),
        })
        obs=next_obs
        if int(getattr(obs,"levels_completed",0))!=initial_level:
            reason="NATIVE_LEVEL_CHANGE"
            break
    return {
        "word":word,
        "status":reason or "COMPLETED_NATIVE_WORD",
        "native_actions_executed":len(observed)-1,
        "root":{
            "whole_frame_hash":digest(root),
            "levels_completed":initial_level
        },
        "endpoint":native_metadata(obs,observed[-1]),
        "transitions":transitions,
    },np.stack(observed)


def evaluate_game(arcade,game,pairs,words,math_refs):
    env,obs,root=native_root(arcade,game)
    roles=choose_two_controls(obs)
    initial=native_metadata(obs,root)
    output={"game":game,"native_reset":initial,
            "provisional_A_B_actions":list(roles) if roles is not None else None}
    if roles is None:
        output["status"]="WALL_FEWER_THAN_TWO_SIMPLE_NATIVE_ACTIONS"
        return output,{}
    observations={}
    raw={}
    for word in words:
        row,frames=execute_word(arcade,game,word,roles)
        observations[word]=row
        raw[game+"_word_"+(word or "EMPTY")]=frames
    root_consistent=len({row["root"]["whole_frame_hash"]
                         for row in observations.values()}|{digest(root)})==1
    all_complete=all(row["status"]=="COMPLETED_NATIVE_WORD"
                     for row in observations.values())
    comparisons=[]
    for pair in pairs:
        a,b=pair
        left,right=observations[a],observations[b]
        left_ok=left["status"]=="COMPLETED_NATIVE_WORD"
        right_ok=right["status"]=="COMPLETED_NATIVE_WORD"
        visible_equal=(
            left["endpoint"]["whole_frame_hash"]==
            right["endpoint"]["whole_frame_hash"]
            if left_ok and right_ok and root_consistent else None)
        predictions=[w["word_equalities"][len(comparisons)] for w in math_refs]
        # Under a literal *injective* visible-state representation, equality
        # predictions and actual whole-frame equality would have to agree.
        consistent=[i for i,pred in enumerate(predictions)
                    if visible_equal is not None and pred==visible_equal]
        comparisons.append({
            "F3_word_pair":list(pair),
            "native_action_pair":list(roles),
            "actual_full_visible_frame_equal":visible_equal,
            "F3_worlds_predict_equal":sum(predictions),
            "F3_worlds_predict_unequal":len(predictions)-sum(predictions),
            "strict_injective_visible_consistent_candidate_indices":consistent
                if visible_equal is not None else None,
            "scope":(
                "Visible-frame equality is not hidden-state identity; "
                "classification is ONLY for a hypothetical direct injective "
                "mapping of native whole frames to original F3 states."
            ),
        })
    excluded=set()
    if root_consistent:
        for c in comparisons:
            viable=c["strict_injective_visible_consistent_candidate_indices"]
            if viable is not None:
                excluded.update(set(range(len(math_refs)))-set(viable))
    output.update({
        "status":("NATIVE_WORDS_COMPLETE" if all_complete and root_consistent
                  else "INCOMPLETE_OR_ROOT_DRIFT"),
        "roots_identical_across_independent_resets":root_consistent,
        "all_predeclared_words_complete":all_complete,
        "native_actuation_count":sum(v["native_actions_executed"]
                                     for v in observations.values()),
        "tested_words":observations,
        "F3_source_comparisons":comparisons,
        "excluded_original_F3_worlds_under_direct_injective_visible_mapping":
            sorted(excluded),
        "candidate_world_count_under_that_strict_mapping":
            9-len(excluded),
    })
    return output,raw


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/f3-new-native-games.json"))
    args=p.parse_args()
    pairs,words,source_refs,source_count=define_math_probe_words()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    games=[]
    grids={}
    for game in GAMES:
        try:
            observed,frames=evaluate_game(
                arcade,game,pairs,words,source_refs)
        except (RuntimeError,ValueError) as error:
            observed={"game":game,"status":"NATIVE_GAME_UNAVAILABLE_OR_INVALID",
                      "error_type":type(error).__name__,
                      "error_message":str(error)[:300]}
            frames={}
        games.append(observed)
        grids.update(frames)
    record={
        "kind":"ORIGINAL_F3_WORD_EQUIVALENCE_VS_INDEPENDENT_NATIVE_PUBLIC_GAMES",
        "native_source":"official arc-agi Arcade NORMAL",
        "predeclared_games":list(GAMES),
        "original_mathematical_source":"work/arc_like_maze/math.py",
        "probe_selector_source":"work/arc_like_maze/relation_probe.py",
        "mathematical_probes_available":source_count,
        "predeclared_math_pairs":[list(x) for x in pairs],
        "unique_native_action_words":words,
        "source_nine_F3_equality_signatures":source_refs,
        "observed_games":games,
        "boundary":"No direct ARC=F3 identification, hidden state proof, learned ARC solver, or competition score. Raw native pixel frames are retained; no pixel or coordinate modulo.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    if grids:
        np.savez_compressed(args.out.with_suffix(".npz"),**grids)
    print("F3_NATIVE_OTHER_GAMES "+json.dumps({
        "games":[{
            "game":g["game"],"status":g["status"],
            "root_actions":g.get("native_reset",{}).get("advertised_native_actions"),
            "provisional_A_B":g.get("provisional_A_B_actions"),
            "all_source_words_completed":g.get("all_predeclared_words_complete"),
            "roots_identical":g.get("roots_identical_across_independent_resets"),
            "native_actions":g.get("native_actuation_count",0),
            "strict_direct_F3_worlds_remaining":g.get(
                "candidate_world_count_under_that_strict_mapping"),
            "word_comparisons":[{
                "words":r["F3_word_pair"],
                "actual_visible_equal":r["actual_full_visible_frame_equal"],
                "nine_F3_equal":r["F3_worlds_predict_equal"]
            } for r in g.get("F3_source_comparisons",[])]
        } for g in games],
        "native_word_count":len(words),
        "math_probe_count":len(pairs),
        "out":str(args.out),
        "arrays":str(args.out.with_suffix(".npz")) if grids else None,
    },sort_keys=True))
    if not any(g.get("status")=="NATIVE_WORDS_COMPLETE" for g in games):
        raise RuntimeError("No new game produced complete native evidence; see manifest")


if __name__ == "__main__":
    main()
