"""F3 original A-order-three witness search on measured ARC LS20 glyph factor.

Search native action words of length 1..6 against the *previously validated*
pixel-observation model, NOT a simulated ARC game. The model was independently
tested 69/69 on actual native frames. Exact glyph position is kept in pixel
units. In particular, NO modulo-three mapping of a position or color is made.

A candidate word W must satisfy W(root)!=root, W²(root)!=root,
W(root)!=W²(root), W³(root)=root on exact glyph coordinates.
Check long predeclared word repetitions on the official native game to test
model validity and distinguish a glyph return from a full-frame return.

No fitted goal behavior, downloaded puzzle solution, game engine
reimplementation, heuristic ARC bot, or claim of F3 alignment.
"""
from __future__ import annotations

import argparse
from collections import Counter,deque
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np

from work.arc_like_maze.math import inverse_candidates
from .native_factor_prediction import (
    calibrate, initialize, predict, digest, GLYPH_COLORS
)
from .native_factor_geometry import candidate_motion,static_board
from .native_relation_scan import grid


MAX_WORD_LENGTH = 6  # fixed before seeing this experiment's results
ALPHABET = "1234"
# Independent native checks of the screened model, including strict control
# failures A, obvious cancellation, and wall-adjacent longer compositions.
NATIVE_CONFIRMATION = ("1", "34", "12", "3214", "113422", "3142")


def original_f3_requirement() -> dict:
    witnesses = []
    for w in inverse_candidates():
        origin = w.origin
        p1,p2,p3=(w.apply("A"*n) for n in (1,2,3))
        if not (p1!=origin and p2!=origin and p1!=p2 and p3==origin):
            raise AssertionError("declared original F3 A is not order three")
        witnesses.append({"phi":list(w.phi),"A_origin":list(p1),
                          "A2_origin":list(p2),"A3_origin":list(p3)})
    return {"source":"work/arc_like_maze/math.py:World.step",
            "origin_F3_three_cycle_verified":len(witnesses)==9,
            "worlds":witnesses}


def measured_model(root,template):
    board=static_board(root,template)
    @lru_cache(maxsize=None)
    def next_offset(state:tuple[int,int],letter:str)->tuple[int,int]:
        nx,ny,_reason,_blockers=candidate_motion(
            board,template,state[0],state[1],letter)
        return (nx,ny)
    def apply_word(start:tuple[int,int], word:str)->tuple[int,int]:
        state=start
        for letter in word:
            state=next_offset(state,letter)
        return state
    # Bounded reachability from a native-calibrated root in the measured
    # observational factor. These are MODEL-PREDICTED, not all native-tested.
    root_state=(0,0)
    seen={root_state}
    todo=deque([root_state])
    while todo:
        s=todo.popleft()
        for letter in ALPHABET:
            ns=next_offset(s,letter)
            if ns not in seen:
                seen.add(ns)
                todo.append(ns)
    return apply_word,sorted(seen),next_offset


def scan_macros(apply_word,states):
    rooted_counts=Counter()
    accessible_counts=Counter()
    root_examples={}
    accessible_examples={}
    period_three_root=[]
    period_three_other=[]
    tested=0
    root=(0,0)
    def status(s0,p1,p2,p3):
        if p3!=s0:
            return "NOT_THREE_RETURN"
        if p1==s0:
            return "FIXED_BY_FIRST_MACRO"
        if p2==s0:
            return "PERIOD_TWO_OR_EARLIER"
        if len({s0,p1,p2})==3:
            return "STRICT_PERIOD_THREE"
        return "DEGENERATE_RETURN"
    for n in range(1,MAX_WORD_LENGTH+1):
        for letters in product(ALPHABET,repeat=n):
            word="".join(letters)
            tested+=1
            for j,starting in enumerate([root]+[s for s in states if s!=root]):
                p1=apply_word(starting,word)
                p2=apply_word(p1,word)
                p3=apply_word(p2,word)
                st=status(starting,p1,p2,p3)
                if j==0:
                    rooted_counts[st]+=1
                    if st not in root_examples:
                        root_examples[st]={"word":word,"offsets":[list(s) for s in
                                                 (starting,p1,p2,p3)]}
                    if st=="STRICT_PERIOD_THREE":
                        period_three_root.append({"word":word,"offsets":[list(s) for s in
                                                  (starting,p1,p2,p3)]})
                else:
                    accessible_counts[st]+=1
                    if st not in accessible_examples:
                        accessible_examples[st]={"word":word,
                                                 "model_start_offset":list(starting),
                                                 "offsets":[list(s) for s in
                                                          (starting,p1,p2,p3)]}
                    if st=="STRICT_PERIOD_THREE" and len(period_three_other)<25:
                        period_three_other.append({"word":word,
                                                  "model_start_offset":list(starting),
                                                  "offsets":[list(s) for s in
                                                           (starting,p1,p2,p3)]})
    return {
        "scope":"Exact integer-pixel glyph offsets in previously native-validated geometric model; finite candidate word search only, not native gameplay",
        "native_alphabet":ALPHABET,
        "max_nonempty_composite_length":MAX_WORD_LENGTH,
        "words_examined_at_root":tested,
        "model_reachable_offsets":len(states),
        "root_orbit_counts":dict(rooted_counts),
        "model_other_start_orbit_counts":dict(accessible_counts),
        "root_class_examples":root_examples,
        "other_start_class_examples":accessible_examples,
        "strict_three_cycles_at_root":period_three_root[:25],
        "other_start_strict_three_cycle_examples":period_three_other,
        "strict_three_cycles_at_root_total":rooted_counts["STRICT_PERIOD_THREE"],
        "strict_three_cycles_at_other_model_offsets_total":accessible_counts["STRICT_PERIOD_THREE"],
    }


def native_confirm(arcade,game,root,template,apply_word):
    results=[]
    grids={}
    total=0
    for word in NATIVE_CONFIRMATION:
        env, obs, initial=initialize(arcade,game)
        if not np.array_equal(initial,root):
            raise RuntimeError("native root differs from calibration root")
        frames=[initial]
        baseline_level=int(getattr(obs,"levels_completed",0))
        model=(0,0)
        t=0
        steps=[]
        macro_endpoints=[{"macro_index":0,"offset":[0,0],
                          "glyph_hash":digest(np.isin(initial,GLYPH_COLORS).astype(np.uint8)),
                          "full_hash":digest(initial)}]
        interrupted=False
        for repeat in range(1,4):
            for letter in word:
                t+=1
                options={int(getattr(a,"value",a)) for a in
                         (getattr(obs,"available_actions",None) or ())}
                if int(letter) not in options:
                    interrupted=True
                    steps.append({"step":t,"native_action":int(letter),
                                  "status":"UNKNOWN_UNAVAILABLE"})
                    break
                model=apply_word(model,letter)
                expected=predict(root,template,*model,t)
                expected_hash=digest(expected)  # BEFORE actual action
                actual_obs=env.step(getattr(GameAction,"ACTION"+letter))
                total+=1
                if actual_obs is None or getattr(actual_obs,"frame",None) is None:
                    interrupted=True
                    steps.append({"step":t,"native_action":int(letter),
                                  "predicted_full_hash":expected_hash,
                                  "status":"UNKNOWN_NO_FRAME"})
                    break
                native=grid(actual_obs).copy()
                frames.append(native)
                equality=bool(np.array_equal(expected,native))
                err=np.nonzero(expected!=native)
                steps.append({
                    "step":t,"native_action":int(letter),
                    "predicted_full_hash":expected_hash,
                    "observed_full_hash":digest(native),
                    "predicted_offset":[*model],
                    "full_frame_equal":equality,
                    "glyph_mask_equal":bool(np.array_equal(
                        np.isin(expected,GLYPH_COLORS),np.isin(native,GLYPH_COLORS))),
                    "trace_mask_equal":bool(np.array_equal(expected==11,native==11)),
                    "error_cell_count":int(np.count_nonzero(expected!=native)),
                    "sample_wrong_pixel":[{"x":int(x),"y":int(y),
                                          "expected_native_color":int(expected[y,x]),
                                          "actual_native_color":int(native[y,x])}
                                          for y,x in list(zip(err[0][:3],err[1][:3]))],
                    "state":str(getattr(actual_obs,"state",None)),
                    "levels_completed":int(getattr(actual_obs,"levels_completed",0)),
                    "status":"PREDICTION_MATCH" if equality else "NATIVE_COUNTEREXAMPLE",
                })
                obs=actual_obs
                if int(getattr(obs,"levels_completed",0))!=baseline_level:
                    interrupted=True
                    steps[-1]["status"]="LEVEL_CHANGED_STOP"
                    break
            if interrupted:
                break
            snap=frames[-1]
            macro_endpoints.append({
                "macro_index":repeat,
                "offset":[*model],
                "glyph_hash":digest(np.isin(snap,GLYPH_COLORS).astype(np.uint8)),
                "full_hash":digest(snap),
            })
        rawkey="word_"+word
        grids[rawkey]=np.stack(frames)
        glyph3=None
        full3=None
        if len(macro_endpoints)==4:
            glyph3=macro_endpoints[0]["glyph_hash"]==macro_endpoints[3]["glyph_hash"]
            full3=macro_endpoints[0]["full_hash"]==macro_endpoints[3]["full_hash"]
        results.append({
            "macro":word,"executed_native_actions":len(frames)-1,
            "macro_endpoints":macro_endpoints,
            "root_glyph_return_after_three_macros":glyph3,
            "root_full_frame_return_after_three_macros":full3,
            "all_frames_predicted_exactly":not interrupted and
                                          all(s["status"]=="PREDICTION_MATCH" for s in steps),
            "interrupted":interrupted,
            "per_action":steps,
        })
    return results,grids,total


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--game",default="ls20")
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/f3-macro-order.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    root,calibrated,template=calibrate(arcade,args.game)
    apply_word,states,step=measured_model(root,template)
    mathw=original_f3_requirement()
    scan=scan_macros(apply_word,states)
    observations,raw,total=native_confirm(arcade,args.game,root,template,apply_word)
    record={
        "kind":"F3_ORIGINAL_ORDER_THREE_VS_NATIVE_GLYPH_MACRO_SCOPE",
        "game":args.game,
        "native_environment":"official arc-agi Arcade NORMAL",
        "source_math":mathw,
        "search":scan,
        "predeclared_native_composite_controls":list(NATIVE_CONFIRMATION),
        "native_calibration_actions":1,
        "native_validation_actions":total,
        "native_validation":observations,
        "limitations":(
            "Finite exhaustive word length <=6 in validated local glyph model, "
            "not exhaustive proof over all possible native action words or worlds; "
            "model-reachable offsets not independently native-witnessed; "
            "full native trace is visibly monotonic before saturation. "
            "No F3 modulo projection, hidden-state equality, general ARC solving, "
            "or competition score is claimed."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    raw["root"]=root
    raw["native_calibration_after_ACTION3"]=calibrated
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ARC3_F3_ORDER3_RESULT "+json.dumps({
        "game":args.game,
        "source_F3_A_order3":mathw["origin_F3_three_cycle_verified"],
        "macro_search":{k:v for k,v in scan.items() if k in (
            "words_examined_at_root","model_reachable_offsets",
            "root_orbit_counts","model_other_start_orbit_counts",
            "strict_three_cycles_at_root_total",
            "strict_three_cycles_at_other_model_offsets_total")},
        "native_calibration_actions":1,
        "native_confirmation_actions":total,
        "native_confirmation":[{
            "word":v["macro"],
            "native_actions":v["executed_native_actions"],
            "all_frames_exact":v["all_frames_predicted_exactly"],
            "glyph_three_macro_return":v["root_glyph_return_after_three_macros"],
            "full_three_macro_return":v["root_full_frame_return_after_three_macros"],
            "first_mismatch":next((x for x in v["per_action"]
                                   if x.get("status")!="PREDICTION_MATCH"),None),
        } for v in observations],
        "record":str(args.out),"raw_frames":str(args.out.with_suffix(".npz"))
    },sort_keys=True))


if __name__=="__main__":
    main()
