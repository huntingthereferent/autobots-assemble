"""Native SP80 stage-specific ACTION4 effect masks: preregistered D4 + shift.

Observed independently in earlier real native runs:
  - level0 prefix '454545' advances 0 -> 1 on action six.
  - same '454545' does not transfer level1 -> 2.
  - ACTION4 change-mask counts: 34 vs 33 at both stage starts.

Falsifiable GEOMETRIC experiment; NOT F3 arithmetic or a native A/B role:
  1. Actual official ARC game; independently reset three times.
  2. At each reset run 454545 from level0 and then 454545 at level1.
  3. Select a geometric transform using only level0 vs level1 ACTION4
     effect masks at *word step 1* in first reset.
  4. Freeze transform and integer translation. Predict level1 exact
     changed-cell masks from level0 effect masks at word steps 3 and 5
     (same ACTION4), and steps 2 and 4 (different ACTION5) as controls.
  5. Compare same fitted relationship at all word steps across resets 2/3,
     with no refit. Keep every pixel-level miss and clipping.

Candidate transforms are exactly eight D4 symmetries of the 64x64 grid,
followed by a data-estimated integer translation determined from sparse
pixel coincidences in training pair only. Translation WITH clipping is not
a bijective 64x64 grid conjugacy. 34!=33 already rules out an EXACT
bijective map between ACTION4 effect masks.

Keep native colors unchanged. This detects an observed alignment and its
limits; it does not invent F3 coordinates or claim a native game solve.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_sp80_stage_transfer import frame_view, hash_grid

GAME = "sp80"
WORDS = "454545"
RESETS = 3
ACTIONS_TO_VALIDATE = (2, 3, 4, 5, 6)
D4_NAMES = ("identity", "rot90", "rot180", "rot270",
            "reflect_x", "reflect_y", "diag", "antidiag")


def coords(mask):
    ys, xs = np.nonzero(mask)
    return frozenset((int(x), int(y)) for y,x in zip(ys,xs))


def d4(point,kind):
    x,y=point
    if kind == "identity": return (x,y)
    if kind == "rot90": return (63-y,x)
    if kind == "rot180": return (63-x,63-y)
    if kind == "rot270": return (y,63-x)
    if kind == "reflect_x": return (63-x,y)
    if kind == "reflect_y": return (x,63-y)
    if kind == "diag": return (y,x)
    if kind == "antidiag": return (63-y,63-x)
    raise ValueError("not a D4 element")


def transform(src,kind,dx,dy):
    projected={(d4(p,kind)[0]+dx,d4(p,kind)[1]+dy) for p in src}
    clipped={p for p in projected if 0<=p[0]<64 and 0<=p[1]<64}
    return frozenset(clipped),len(projected)-len(clipped)


def compare(src,dst,kind,dx,dy):
    projected,clipped=transform(src,kind,dx,dy)
    common=projected&dst
    fp=projected-dst
    fn=dst-projected
    denominator=len(projected)+len(dst)
    return {
        "overlap":len(common),
        "source_count":len(src),
        "target_count":len(dst),
        "projected_count":len(projected),
        "clipped_source_pixels":clipped,
        "f1":2*len(common)/denominator if denominator else 1.0,
        "exact":projected==dst and clipped==0,
        "false_positive_count":len(fp),
        "false_negative_count":len(fn),
        "sample_false_positive_xy":[list(p) for p in sorted(fp)[:8]],
        "sample_false_negative_xy":[list(p) for p in sorted(fn)[:8]],
    }


def candidate_fit(source,target,allowed=D4_NAMES):
    """One-step-only registration, then frozen for all held-out effects."""
    if not source or not target:
        raise RuntimeError("nonempty ACTION4 changed-cell masks required")
    scored=[]
    for kind in allowed:
        left={d4(p,kind) for p in source}
        shifts=sorted({(tx-sx,ty-sy)
                       for sx,sy in left for tx,ty in target})
        for dx,dy in shifts:
            score=compare(source,target,kind,dx,dy)
            scored.append((
                -score["overlap"],-score["f1"],
                score["clipped_source_pixels"],abs(dx)+abs(dy),
                kind,dx,dy,score
            ))
    best=min(scored,key=lambda row:row[:7])
    return {
        "symmetry":best[4],"translation_dx":best[5],
        "translation_dy":best[6],"training_score":best[7],
        "candidate_d4_and_shift_hypotheses_scored":len(scored),
    }


def run_once(arcade,index):
    env=arcade.make(GAME)
    if env is None: raise RuntimeError("official SP80 not available")
    obs=env.reset()
    root,info=frame_view(obs)
    if root is None: raise RuntimeError("native SP80 root not full frame")
    frames=[root]
    steps=[]
    for n,letter in enumerate(WORDS*2,1):
        available={int(getattr(a,"value",a))
                   for a in (getattr(obs,"available_actions",[]) or [])}
        if int(letter) not in available:
            raise RuntimeError(f"native action withdrawn at {n}")
        try:
            obs=env.step(getattr(GameAction,"ACTION"+letter))
        except Exception as exc:
            raise RuntimeError(f"native action exception {n} {type(exc).__name__}: {exc}") from exc
        if obs is None:
            raise RuntimeError(f"null native game response {n}")
        next_grid,shape=frame_view(obs)
        if next_grid is None:
            raise RuntimeError(f"nonstandard native frame {n}: {shape}")
        level=int(getattr(obs,"levels_completed",0))
        expected=0 if n<6 else 1
        if level!=expected:
            raise RuntimeError(f"native level unexpectedly {level} after action {n}, expected {expected}")
        mask=frames[-1]!=next_grid
        steps.append({
            "native_action":int(letter),
            "step_in_stage":((n-1)%6)+1,
            "stage":0 if n<=6 else 1,
            "frame_before":hash_grid(frames[-1]),
            "frame_after":hash_grid(next_grid),
            "changed_cells":int(np.count_nonzero(mask)),
            "actual_level_after":level,
            "native_game_state":str(getattr(obs,"state",None)),
            "native_frame_source_shape":shape["shape"],
        })
        frames.append(next_grid)
    return {
        "reset":index,"root":hash_grid(frames[0]),
        "stage1_root":hash_grid(frames[6]),
        "native_actions":12,
        "end_native_level":int(getattr(obs,"levels_completed",0)),
        "steps":steps,
    },np.stack(frames)


def mask_pair(frames,step):
    """stage-local transition number step=1..6."""
    if step not in range(1,7): raise ValueError("invalid stage step")
    return coords(frames[step-1]!=frames[step]),coords(
        frames[step+5]!=frames[step+6])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-stage-d4-heldout.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    experiments=[]
    frames={}
    for i in range(RESETS):
        row,raw=run_once(arcade,i)
        experiments.append(row)
        frames[f"reset_{i}"]=raw

    fit_x,fit_y=mask_pair(frames["reset_0"],1)
    chosen=candidate_fit(fit_x,fit_y)
    kind,dx,dy=chosen["symmetry"],chosen["translation_dx"],chosen["translation_dy"]
    translation_only=candidate_fit(fit_x,fit_y,("identity",))
    other_steps=[]
    for reset in range(RESETS):
        for step in range(1,7):
            source,target=mask_pair(frames[f"reset_{reset}"],step)
            m=compare(source,target,kind,dx,dy)
            other_steps.append({
                "reset_index":reset,"word_step":step,
                "native_action":int(WORDS[step-1]),
                "role":("TRAINING_PAIR" if reset==0 and step==1
                        else "FRESH_RESET_TRAINING_STEP" if step==1
                        else "FROZEN_HELDOUT_ACTION4" if step in (3,5)
                        else "NEGATIVE_CONTROL_ACTION5"),
                **m,
            })

    # Competing simpler hypothesis selected on the SAME training pair only.
    # Compare independent heldout words/steps without fitting new shifts.
    tk,tdx,tdy=(
        translation_only["symmetry"],
        translation_only["translation_dx"],
        translation_only["translation_dy"])
    translation_evaluations=[]
    for reset in range(RESETS):
        for step in range(1,7):
            source,target=mask_pair(frames[f"reset_{reset}"],step)
            z=compare(source,target,tk,tdx,tdy)
            translation_evaluations.append({
                "reset_index":reset,"word_step":step,
                "native_action":int(WORDS[step-1]),
                **z,
            })
    # A symmetry claim requires predictions that differ on the heldout
    # masks; equal scores alone cannot identify the D4 orientation.
    competing_predictions=[]
    for reset in range(RESETS):
        for step in range(1,7):
            source,target=mask_pair(frames[f"reset_{reset}"],step)
            d4_pixels,_=transform(source,kind,dx,dy)
            simple_pixels,_=transform(source,tk,tdx,tdy)
            competing_predictions.append({
                "reset":reset,"word_step":step,
                "native_action":int(WORDS[step-1]),
                "exact_same_predicted_pixels":d4_pixels==simple_pixels,
                "symmetric_difference_predicted_pixels":len(
                    d4_pixels^simple_pixels),
                "d4_overlap":len(d4_pixels&target),
                "translation_overlap":len(simple_pixels&target),
            })
    heldout=[x for x in other_steps
             if x["role"]=="FROZEN_HELDOUT_ACTION4"]
    controls=[x for x in other_steps
              if x["role"]=="NEGATIVE_CONTROL_ACTION5"]
    simpler_heldout=[x for x in translation_evaluations
                     if x["word_step"] in (3,5)]
    simpler_controls=[x for x in translation_evaluations
                      if x["word_step"] in (2,4,6)]
    baseline=[
        compare(*mask_pair(frames[f"reset_{i}"],step),
                "identity",0,0)
        for i in range(RESETS) for step in (3,5)
    ]
    data={
        "kind":"SP80_NATIVE_STAGE0_STAGE1_PREREGISTERED_D4_PLUS_TRANSLATION",
        "native_source":"official public arc-agi Arcade NORMAL",
        "game":GAME,"math_context":"original Window48 48 laws; NO native F3 correspondence",
        "predeclared_actions":WORDS*2,
        "independent_native_resets":RESETS,
        "native_actions":sum(e["native_actions"] for e in experiments),
        "training_reset":0,"training_step":1,
        "fit_hypothesis":"best sparse pixel overlap among D4+integer translation on first ACTION4 mask ONLY",
        "frozen_fit":chosen,
        "translation_only_training_fit":translation_only,
        "translation_only_frozen_evaluations":translation_evaluations,
        "prediction_distinctions_between_fitted_models":
            competing_predictions,
        "action4_competing_models_predict_identical_pixels":all(
            x["exact_same_predicted_pixels"]
            for x in competing_predictions if x["native_action"]==4),
        "translation_only_heldout_action4_mean_f1":
            sum(x["f1"] for x in simpler_heldout)/len(simpler_heldout),
        "translation_only_action5_control_mean_f1":
            sum(x["f1"] for x in simpler_controls)/len(simpler_controls),
        "heldout_same_action_step_indices":[3,5],
        "different_action_negative_control_indices":[2,4,6],
        "every_stage_action_observation":experiments,
        "every_frozen_transform_evaluation":other_steps,
        "heldout_action4_exact_count":sum(x["exact"] for x in heldout),
        "heldout_action4_total":len(heldout),
        "heldout_action4_mean_f1":sum(x["f1"] for x in heldout)/len(heldout),
        "identity_no_shift_heldout_mean_f1":sum(x["f1"] for x in baseline)/len(baseline),
        "action5_negative_control_mean_f1":sum(x["f1"] for x in controls)/len(controls),
        "limits":(
            "Pixel changes differ in cardinality already (34 vs 33). "
            "A nonzero translation clipped to 64x64 is NOT bijective "
            "or a proven conjugacy. D4+translation selected on only the "
            "first source-observed action effect; later effects and resets "
            "are held out from model selection. Independent resets of "
            "the SAME native public game do not generalize to other games. "
            "No F3 color conversion, hidden-state mapping, ARC solver or win."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("SP80_NATIVE_D4_HELDOUT "+json.dumps({
        "native_actions":data["native_actions"],
        "resets":RESETS,
        "stage1_roots":len({e["stage1_root"] for e in experiments}),
        "training_fit":chosen,
        "translation_only_training_fit":translation_only,
        "action4_competing_models_predict_identical_pixels":
            data["action4_competing_models_predict_identical_pixels"],
        "models_compare":[x for x in competing_predictions
                          if x["reset"]==0],
        "translation_only_heldout_action4_mean_f1":
            data["translation_only_heldout_action4_mean_f1"],
        "translation_only_action5_control_mean_f1":
            data["translation_only_action5_control_mean_f1"],
        "heldout_action4_exact":data["heldout_action4_exact_count"],
        "heldout_action4_total":data["heldout_action4_total"],
        "heldout_action4_mean_f1":data["heldout_action4_mean_f1"],
        "identity_baseline_mean_f1":data["identity_no_shift_heldout_mean_f1"],
        "action5_control_mean_f1":data["action5_negative_control_mean_f1"],
        "translation_only_per_step":[
            {"reset":x["reset_index"],"step":x["word_step"],
             "f1":x["f1"],"overlap":x["overlap"],
             "projected":x["projected_count"],"clipped":x["clipped_source_pixels"]}
            for x in translation_evaluations],
        "per_step":[{"reset":x["reset_index"],"step":x["word_step"],
                     "action":x["native_action"],"f1":x["f1"],
                     "overlap":x["overlap"],"projected":x["projected_count"],
                     "target":x["target_count"],"clipped":x["clipped_source_pixels"],
                     "exact":x["exact"]} for x in other_steps],
        "record":str(args.out),
        "raw":str(args.out.with_suffix(".npz")),
    },sort_keys=True))


if __name__=="__main__":
    main()
