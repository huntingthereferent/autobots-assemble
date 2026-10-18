"""Predeclared, falsifiable LS20 native visible-state prediction experiment.

Hypothesis FROM PRIOR NATIVE OBSERVATIONS ONLY:
- 15 native-color-9 pixels and 10 native-color-12 pixels co-translate
  by FIVE actual grid pixels on supported directional moves.
- Native ACTION2 is blocked at the starting lower boundary, but transports
  the glyph +5 y after it has moved upward.
- Two native-color-11 pixels at rows 61,62 and successive x=13,14,...
  turn to native-color-3 on EACH environment step, even if glyph is blocked.

Calibrate the mobile glyph's literal pixel coordinates from ONE independent
native ACTION3 at root, and then predict full 64x64 frames BEFORE taking any
action on untouched mixed native sequences. Do not change predictions after a
miss. No modulo-three projection, no ARC solver, no synthetic game and no
claim that this native two-factor model is mathematically F3.
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

from .native_relation_scan import grid

GLYPH_COLORS = (9, 12)
TRACE_COLOR = 11
BACKGROUND = 3
TRACE_Y = (61, 62)
TRACE_FIRST_X = 13
STEP_PX = 5

# Declared before any results from this experiment.
WORDS = ("1122", "2112", "3214", "3412",
         "113422", "4123", "2211", "1234")
EXPECTED_COUNTS = {9: 15, 12: 10}
NATIVE_VECTORS = {"1": (0,-5), "2": (0,5), "3": (-5,0), "4": (5,0)}


def digest(g: np.ndarray) -> str:
    return blake2b(g.tobytes(), digest_size=16).hexdigest()


def initialize(arcade, game: str):
    env = arcade.make(game)
    if env is None:
        raise RuntimeError("official native ARC environment unavailable")
    observed = env.reset()
    if observed is None or getattr(observed, "frame", None) is None:
        raise RuntimeError("native reset did not yield complete pixels")
    return env, observed, grid(observed).copy()


def calibrate(arcade, game: str):
    env, initial, root = initialize(arcade, game)
    legal = {int(getattr(x, "value", x)) for x in (initial.available_actions or ())}
    if 3 not in legal:
        raise RuntimeError("native ACTION3 unavailable")
    after_obs = env.step(GameAction.ACTION3)
    if after_obs is None or after_obs.frame is None:
        raise RuntimeError("native calibration action had no frame")
    moved = grid(after_obs).copy()
    if int(getattr(after_obs, "levels_completed", 0)) != int(getattr(initial,"levels_completed",0)):
        raise RuntimeError("unexpected native level transition in calibration")
    template = {}
    for color,count in EXPECTED_COUNTS.items():
        ys,xs = np.nonzero((root == color) & (moved != color))
        points = tuple((int(x),int(y)) for y,x in zip(ys,xs))
        if len(points) != count:
            raise RuntimeError("native calibration no longer matches prior exact-transport witness")
        after_pts = {(int(x),int(y)) for y,x in zip(*np.nonzero((moved == color) & (root != color)))}
        if {(x-STEP_PX,y) for x,y in points} != after_pts:
            raise RuntimeError("actual native calibration not a rigid -5x transport")
        template[color] = points
    for y in TRACE_Y:
        for x in range(TRACE_FIRST_X, TRACE_FIRST_X+max(map(len,WORDS))):
            if int(root[y,x]) != TRACE_COLOR:
                raise RuntimeError("predeclared native trace is missing source color11")
    return root, moved, template


def predict(root: np.ndarray, template: dict, dx: int,dy: int, t: int):
    predicted = root.copy()
    for points in template.values():
        for x,y in points:
            predicted[y,x] = BACKGROUND
    for color,points in template.items():
        for x,y in points:
            tx,ty = x+dx,y+dy
            if not (0<=tx<64 and 0<=ty<64):
                raise RuntimeError("predicted geometry exceeds native frame")
            predicted[ty,tx] = color
    for k in range(t):
        for y in TRACE_Y:
            predicted[y, TRACE_FIRST_X+k] = BACKGROUND
    return predicted


def offset_after(dx: int, dy: int, letter: str) -> tuple[int,int,bool]:
    vx,vy=NATIVE_VECTORS[letter]
    # Exact boundary hypothesis from prior ACTION2-before/after-ACTION1 evidence.
    if letter == "2" and dy >= 0:
        return dx,dy,True
    return dx+vx,dy+vy,False


def evaluate(arcade, game: str, root: np.ndarray, template: dict):
    rows = []
    raw_frames = {}
    counted_actions = 0
    for word in WORDS:
        env, initial, actual = initialize(arcade,game)
        if not np.array_equal(actual,root):
            raise RuntimeError("held-out native root changed since calibration")
        series = [actual]
        dx=dy=0
        steps=[]
        initial_level = int(getattr(initial,"levels_completed",0))
        obs=initial
        for t,letter in enumerate(word,1):
            legal = {int(getattr(a,"value",a)) for a in (obs.available_actions or ())}
            if int(letter) not in legal:
                steps.append({"step":t,"action":int(letter),
                              "status":"UNKNOWN_ACTION_UNAVAILABLE"})
                break
            next_dx,next_dy,blocked = offset_after(dx,dy,letter)
            prior_predicted = predict(root,template,dx,dy,t-1)
            predicted = predict(root,template,next_dx,next_dy,t)
            # Prediction already materialized before actual native intervention.
            expectation={
                "step":t,"action":int(letter),"glyph_offset_before":[dx,dy],
                "glyph_offset_predicted":[next_dx,next_dy],
                "movement_predicted_blocked":blocked,
                "predicted_full_frame_hash":digest(predicted),
                "predicted_glyph_hash":digest(np.isin(predicted,GLYPH_COLORS).astype(np.uint8)),
                "predicted_trace_hash":digest((predicted==TRACE_COLOR).astype(np.uint8)),
                "predicted_prior_frame_hash":digest(prior_predicted),
            }
            observation=env.step(getattr(GameAction,"ACTION"+letter))
            counted_actions += 1
            if observation is None or getattr(observation,"frame",None) is None:
                steps.append({**expectation,"status":"UNKNOWN_NATIVE_FRAME_MISSING"})
                break
            actual=grid(observation).copy()
            series.append(actual)
            difference=predicted!=actual
            ys,xs=np.nonzero(difference)
            mismatch={
                "exact_full_frame":bool(not np.any(difference)),
                "glyph_mask":bool(np.array_equal(np.isin(actual,GLYPH_COLORS),
                                               np.isin(predicted,GLYPH_COLORS))),
                "trace_mask":bool(np.array_equal(actual==TRACE_COLOR,
                                               predicted==TRACE_COLOR)),
                "wrong_cell_count":int(np.count_nonzero(difference)),
                "first_wrong_pixels":[{"x":int(x),"y":int(y),
                                       "predicted_native_color":int(predicted[y,x]),
                                       "actual_native_color":int(actual[y,x])}
                                      for y,x in zip(ys[:8],xs[:8])],
            }
            steps.append({
                **expectation,"actual_full_frame_hash":digest(actual),
                "level_after":int(getattr(observation,"levels_completed",0)),
                "native_state":str(getattr(observation,"state",None)),
                "witness":mismatch,"status":"PREDICTION_MATCH" if mismatch["exact_full_frame"]
                                                   else "NATIVE_COUNTEREXAMPLE",
            })
            dx,dy=next_dx,next_dy
            obs=observation
            if int(getattr(observation,"levels_completed",0))!=initial_level:
                steps[-1]["status"]="LEVEL_TRANSITION_STOP"
                break
        raw_frames["word_"+word]=np.stack(series)
        rows.append({"word":word,"expected_native_actions":len(word),
                     "executed_native_actions":len(series)-1,
                     "predicted_terminal_offset":[dx,dy],
                     "per_action":steps,
                     "all_full_frame_predictions_match":(
                         len(steps)==len(word) and
                         all(s["status"]=="PREDICTION_MATCH" for s in steps)),
                     "level_completed":int(getattr(obs,"levels_completed",0))})
    return rows,raw_frames,counted_actions


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--game",default="ls20")
    p.add_argument("--out",type=Path,default=Path("runtime/data/arc3/native-factor-predictions.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    root,calibrated,template=calibrate(arcade,args.game)
    rows,frames,count=evaluate(arcade,args.game,root,template)
    total=sum(len(r["per_action"]) for r in rows)
    exact=sum(s["status"]=="PREDICTION_MATCH" for r in rows for s in r["per_action"])
    glyph=sum(s.get("witness",{}).get("glyph_mask",False) for r in rows for s in r["per_action"])
    trace=sum(s.get("witness",{}).get("trace_mask",False) for r in rows for s in r["per_action"])
    record={
        "kind":"NATIVE_LS20_PREDECLARED_VISIBLE_FACTOR_PREDICTIONS",
        "game":args.game,
        "native_source":"official arc-agi Arcade NORMAL",
        "predeclared_words":WORDS,
        "predeclared_model":{
            "glyph_native_colors":GLYPH_COLORS,
            "glyph_source_pixels":{str(c):list(v) for c,v in template.items()},
            "movement_unit_pixels":STEP_PX,
            "provisional_direction_vectors":NATIVE_VECTORS,
            "action2_blocked_when_y_offset_nonnegative":True,
            "trace": {"native_color_from":11,"native_color_to":3,
                      "rows":TRACE_Y,"x_first":TRACE_FIRST_X,"dx_per_action":1},
        },
        "calibration_native_actions":1,
        "heldout_native_actions":count,
        "calibration_root_hash":digest(root),
        "calibration_after_ACTION3_hash":digest(calibrated),
        "full_frame_exact":exact,"glyph_mask_exact":glyph,"trace_mask_exact":trace,
        "evaluated_predictions":total,
        "runs":rows,
        "scope":"Root calibration and heldout native probes on same public game; no hidden-state model, field-coordinate map, or new F3 claim; every mismatch retained.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    frames["calibration_root"]=root
    frames["calibration_action3"]=calibrated
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("ARC3_NATIVE_FACTOR_PREDICTION "+json.dumps({
        "game":args.game,"calibration_actions":1,"heldout_native_actions":count,
        "evaluated_predictions":total,"full_frame_exact":exact,
        "glyph_mask_exact":glyph,"trace_mask_exact":trace,
        "per_word":[{"word":r["word"],"executed":r["executed_native_actions"],
                     "all_exact":r["all_full_frame_predictions_match"],
                     "first_mismatch":next((s for s in r["per_action"]
                                            if s["status"]!="PREDICTION_MATCH"),None)}
                    for r in rows],
        "record":str(args.out),
        "raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))


if __name__=="__main__":
    main()
