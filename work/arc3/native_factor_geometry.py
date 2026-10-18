"""Native LS20 obstacle-aware prediction, correcting a falsified geometry model.

FROZEN earlier witness from native_factor_prediction.py:
  28/34 full-frame correct, 34/34 two-cell trace correct.
  Left moves near wall-colored cells contradicted free translations.

NEW predeclared rule: moving observed 25-pixel native glyph onto ANY static
non-background native cell blocks movement; the trace still advances. Original
ACTION2 lower-root boundary remains an independently witnessed constraint.

Retest the original eight words AND independent, predeclared new words.
Predictions are computed BEFORE each actual official ARC environment action;
do not inspect game source, alter rules on a failure, or synthesize the game.
These native observations are NOT a proof of F3 recurrence.
"""
from __future__ import annotations
from collections import Counter
import argparse
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_factor_prediction import (
    initialize, calibrate, predict, digest,
    GLYPH_COLORS, BACKGROUND, NATIVE_VECTORS,
    WORDS as EARLIER_WORDS,
)

# Declare and freeze BEFORE running the new native experiments.
NEW_WORDS = ("1312", "3114", "1432", "112233",
             "1324", "3311", "4112", "22114")
assert not (set(EARLIER_WORDS) & set(NEW_WORDS))


def static_board(root, template):
    base = root.copy()
    for points in template.values():
        for x,y in points:
            if int(base[y,x]) not in GLYPH_COLORS:
                raise ValueError("moving source not present at declared native coordinate")
            base[y,x] = BACKGROUND
    return base


def candidate_motion(base, template, dx,dy,letter):
    vx,vy=NATIVE_VECTORS[letter]
    tx,ty=dx+vx,dy+vy
    if letter=="2" and dy>=0:
        return dx,dy,"BLOCKED_OBSERVED_LOWER_ROOT_BOUNDARY",{}
    obstructions=[]
    for points in template.values():
        for x,y in points:
            qx,qy=x+tx,y+ty
            if not (0<=qx<64 and 0<=qy<64):
                obstructions.append(("OUT_OF_BOUNDS",qx,qy))
            elif int(base[qy,qx])!=BACKGROUND:
                obstructions.append((str(int(base[qy,qx])),qx,qy))
    if obstructions:
        counts=Counter(kind for kind,_,_ in obstructions)
        return dx,dy,"BLOCKED_STATIC_NATIVE_GEOMETRY",{
            "blocked_colors":dict(counts),
            "sample_obstructions":[{"native_color":color,"x":x,"y":y}
                                   for color,x,y in obstructions[:8]],
        }
    return tx,ty,"ADMITTED_NATIVE_TRANSLATION",{}


def run_test(arcade,game,root,template,old,new):
    base=static_board(root,template)
    trials=[]
    raw={}
    native_actions=0
    for group,word in [("RETEST_FROZEN_EARLIER",w) for w in old]+[
                       ("HELDOUT_UNSEEN_WORD",w) for w in new]:
        env,obs,actual=initialize(arcade,game)
        if not np.array_equal(actual,root):
            raise RuntimeError("native game root differs from calibrated prediction root")
        root_level=int(getattr(obs,"levels_completed",0))
        grids=[actual]
        dx=dy=0
        steps=[]
        for t,letter in enumerate(word,1):
            legal={int(getattr(a,"value",a)) for a in (obs.available_actions or ())}
            if int(letter) not in legal:
                steps.append({"action":int(letter),"t":t,"status":"UNKNOWN_UNAVAILABLE"})
                break
            nx,ny,reason,blockers=candidate_motion(base,template,dx,dy,letter)
            predicted=predict(root,template,nx,ny,t) # before actual env.step
            predicted_hash=digest(predicted)
            after_obs=env.step(getattr(GameAction,"ACTION"+letter))
            native_actions+=1
            if after_obs is None or after_obs.frame is None:
                steps.append({"action":int(letter),"t":t,"status":"UNKNOWN_NO_NATIVE_FRAME",
                              "predicted_frame":predicted_hash})
                break
            seen=np.asarray(after_obs.frame)
            if seen.ndim==3:
                seen=seen[-1]
            observed=seen.reshape(64,64).astype(np.uint8).copy()
            grids.append(observed)
            mismatched=predicted!=observed
            yy,xx=np.nonzero(mismatched)
            exact=bool(not np.any(mismatched))
            glyph_equal=bool(np.array_equal(np.isin(predicted,GLYPH_COLORS),
                                            np.isin(observed,GLYPH_COLORS)))
            trace_equal=bool(np.array_equal(predicted==11,observed==11))
            steps.append({
                "t":t,"native_action":int(letter),
                "predeclared_geom_rule":reason,"blocker_detail":blockers,
                "predicted_glyph_offset":[nx,ny],
                "predicted_frame":predicted_hash,
                "observed_frame":digest(observed),
                "full_frame_match":exact,"glyph_mask_match":glyph_equal,
                "trace_mask_match":trace_equal,
                "mismatch_pixels":int(np.count_nonzero(mismatched)),
                "mismatch_examples":[
                    {"x":int(x),"y":int(y),
                     "predicted_native_color":int(predicted[y,x]),
                     "actual_native_color":int(observed[y,x])}
                    for y,x in zip(yy[:8],xx[:8])
                ],
                "level_after":int(getattr(after_obs,"levels_completed",0)),
                "status":"MATCH" if exact else "NATIVE_COUNTEREXAMPLE",
            })
            dx,dy=nx,ny
            obs=after_obs
            if int(getattr(obs,"levels_completed",0))!=root_level:
                steps[-1]["status"]="LEVEL_CHANGED"
                break
        trials.append({
            "group":group,"word":word,"actions_executed":len(grids)-1,
            "every_full_frame_predicted":len(steps)==len(word) and
                                         all(z.get("status")=="MATCH" for z in steps),
            "native_level_end":int(getattr(obs,"levels_completed",0)),
            "steps":steps,
        })
        raw["word_"+word]=np.stack(grids)
    return trials,raw,native_actions


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--game",default="ls20")
    p.add_argument("--out",type=Path,default=Path("runtime/data/arc3/native-factor-geometry.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    root,calibrated,template=calibrate(arcade,args.game)
    trials,raw,count=run_test(arcade,args.game,root,template,EARLIER_WORDS,NEW_WORDS)
    groups={}
    for group in ("RETEST_FROZEN_EARLIER","HELDOUT_UNSEEN_WORD"):
        subset=[t for t in trials if t["group"]==group]
        steps=[step for t in subset for step in t["steps"]]
        groups[group]={
            "words":len(subset),"native_actions":sum(t["actions_executed"] for t in subset),
            "exact_full_frames":sum(s.get("full_frame_match",False) for s in steps),
            "exact_glyph_masks":sum(s.get("glyph_mask_match",False) for s in steps),
            "exact_trace_masks":sum(s.get("trace_mask_match",False) for s in steps),
            "evaluated_steps":len(steps),
            "complete_word_predictions":sum(t["every_full_frame_predicted"] for t in subset),
        }
    record={
        "kind":"NATIVE_ARC_GEOMETRY_AWARE_FACTOR_MODEL",
        "game":args.game,"native_provider":"official arc-agi Arcade NORMAL",
        "source_root_hash":digest(root),
        "calibration_action3_hash":digest(calibrated),
        "calibration_native_actions":1,
        "total_test_actions":count,
        "native_movement_model":"static non-background collision + observed lower root bound",
        "native_trace_model":"two color-11 pixels removed in each successive x column",
        "before_results_words":{
            "earlier_retest":list(EARLIER_WORDS),"new_holdout":list(NEW_WORDS)
        },
        "groups":groups,
        "runs":trials,
        "boundary":"No game engine source read; no F3 modulo projection or proof of ARC to F3 mapping; native observations and every model error preserved.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    raw["root"]=root
    raw["calibration_action3"]=calibrated
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ARC3_NATIVE_GEOMETRY_FACTOR "+json.dumps({
        "game":args.game,"calibration":1,"tested_native_actions":count,
        "groups":groups,"per_word":[{
            "group":t["group"],"word":t["word"],"full_word_match":t["every_full_frame_predicted"],
            "mismatches":[{
                "t":s.get("t"),"action":s.get("native_action"),"reason":s.get("predeclared_geom_rule"),
                "pixels":s.get("mismatch_pixels"),"colors":s.get("blocker_detail")}
                for s in t["steps"] if s.get("full_frame_match") is False
            ]} for t in trials],
        "out":str(args.out),"raw":str(args.out.with_suffix(".npz"))
    },sort_keys=True))


if __name__=="__main__":
    main()
