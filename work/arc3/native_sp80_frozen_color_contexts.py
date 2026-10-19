"""Official native SP80: frozen geometry vs actual color transitions, new contexts.

Prior independent SP80 experiment fitted TWO candidate native changed-mask
registrations on ACTION4 of 454545 only:
  T: identity then shift (dx,dy)=(8,20)
  R: reflect_y then shift (dx,dy)=(8,-8)
Both scored F1=.96992 on subsequent 454545 ACTION4 changes.
Neither explains all pixels or proves any Window48/F3 correspondence.

NEW TEST (predeclared before collecting a single new native frame):
  - Additional context words, including ACTION4 after repeated ACTION4 and
    after ACTION5; ACTION5-only control.
  - Each word tested on real original level0 from a fresh reset, AND
    on genuine level1 after independently witnessed 454545 native prefix.
  - TWO independently reset runs per word and level.
  - Both geometry rules and a no-shift negative control are FROZEN; no
    fitted parameters or word changes after observing the native game.
  - Test not only changed-cell overlap but actual native (old_color,new_color)
    transition labels at mapped pixels. Record clipping and residual colors.
  - Every action gets a native level count, actual SDK state and image hash.
  - Interrupted nonstandard/withdrawn-action trials stay UNKNOWN; no null
    fallback frame, synthetic game, imported puzzle solution, or game win.

This is an empirical SP80 study. It does not identify mathematical source
A/B, a rooted Window48 state map or native hidden-state equivalence.
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

from .native_sp80_stage_transfer import frame_view, hash_grid
from .native_sp80_stage_geometry import d4

GAME="sp80"
STAGE1_PREFIX="454545"
# Specific frozen new action contexts: 4 after 4, after 5, and
# after combinations not previously used for geometry fitting.
CONTEXT_WORDS=("4","44","54","544","444","5454","5")
INDEPENDENT_RESETS=2
FROZEN_MAPS=(
    ("translation_only","identity",8,20),
    ("reflection_plus_shift","reflect_y",8,-8),
    ("identity_baseline","identity",0,0),
)


def advertised(obs):
    return {int(getattr(x,"value",x))
            for x in (getattr(obs,"available_actions",[]) or [])}


def classify_original_native_terminal(observation):
    """Classify explicit original SDK state, not returned frame shape."""
    state=getattr(observation,"state",None)
    name=str(getattr(state,"name",state)).rsplit(".",1)[-1]
    if name=="WIN":
        return "NATIVE_TERMINAL_WIN"
    if name=="GAME_OVER":
        return "NATIVE_TERMINAL_GAME_OVER"
    return None


def steps_on_real_game(arcade,word,stage,replicate):
    env=arcade.make(GAME)
    if env is None: raise RuntimeError("real SP80 not available")
    obs=env.reset()
    root,info=frame_view(obs)
    if root is None: raise RuntimeError("root is not a complete native frame")
    origin_hash=hash_grid(root)
    frames=[root]
    actions=0
    prefix_ok=stage==0
    transitions=[]
    native_errors=[]
    full_word=(STAGE1_PREFIX if stage==1 else "")+word
    boundary=len(STAGE1_PREFIX) if stage==1 else 0
    stage_root_hash=origin_hash if stage==0 else None
    stage_root_index=0 if stage==0 else None
    interrupted=None
    original_native_terminal=None
    for i,letter in enumerate(full_word,1):
        control=int(letter)
        if control not in advertised(obs):
            interrupted="UNKNOWN_ACTION_WITHDRAWN"
            native_errors.append({"at":i,"reason":interrupted})
            break
        try:
            after_obs=env.step(getattr(GameAction,"ACTION"+letter))
            actions+=1
        except Exception as exc:
            interrupted="UNKNOWN_NATIVE_EXCEPTION"
            native_errors.append({"at":i,"reason":interrupted,
                                  "class":type(exc).__name__,
                                  "message":str(exc)[:220]})
            break
        if after_obs is None:
            interrupted="UNKNOWN_NULL_NATIVE_RESPONSE"
            break
        next_grid,shape=frame_view(after_obs)
        level=int(getattr(after_obs,"levels_completed",0))
        state=str(getattr(after_obs,"state",None))
        if next_grid is None:
            classification=classify_original_native_terminal(after_obs)
            interrupted=classification or "UNKNOWN_NONSTANDARD_FRAME"
            original_native_terminal=({
                "native_action_index":i,
                "context_action_step":i-boundary if i>boundary else None,
                "state":state,"level":level,
                "frame_available":False,
                "source_shape":shape,
            } if classification else None)
            native_errors.append({"at":i,"level":level,"state":state,
                                  "source_shape":shape})
            break
        frames.append(next_grid)
        transitions.append({
            "step":i,
            "phase":"OBSERVED_STAGE1_ENTRY" if i<=boundary
                    else f"LEVEL{stage}_CONTEXT",
            "action":control,
            "level":level,"state":state,
            "before_hash":hash_grid(frames[-2]),
            "after_hash":hash_grid(next_grid),
            "changed_native_cells":int(np.count_nonzero(frames[-2]!=next_grid)),
        })
        obs=after_obs
        classification=classify_original_native_terminal(after_obs)
        if classification:
            original_native_terminal={
                "native_action_index":i,
                "context_action_step":i-boundary if i>boundary else None,
                "state":state,"level":level,
                "frame_available":True,
                "full_native_frame_hash":hash_grid(next_grid),
            }
            interrupted=classification
            break
        if stage==1 and i<=boundary:
            if (i<boundary and level!=0) or (i==boundary and level!=1):
                interrupted="UNKNOWN_STAGE1_PREFIX_NOT_REPRODUCED"
                break
            if i==boundary:
                prefix_ok=True
                stage_root_hash=hash_grid(next_grid)
                stage_root_index=len(frames)-1
        elif level!=stage:
            interrupted="UNKNOWN_CONTEXT_LEVEL_CHANGED"
            break

    completed=(
        interrupted is None and len(transitions)==len(full_word)
        and prefix_ok)
    return {
        "word":word,"level":stage,"replicate":replicate,
        "root_hash":origin_hash,"stage_root_hash":stage_root_hash,
        "stage_root_index":stage_root_index,
        "real_native_actions":actions,
        "status":"COMPLETE" if completed else interrupted,
        "complete":completed,
        "frame_count":len(frames),
        "transition_records":transitions,
        "terminal_observation":original_native_terminal,
        "errors":native_errors,
    },np.stack(frames)


def changed_triplets(a,b):
    ys,xs=np.nonzero(a!=b)
    return {(int(x),int(y)):(int(a[y,x]),int(b[y,x]))
            for y,x in zip(ys,xs)}


def compare_transitions(src,dst,rule):
    name,kind,dx,dy=rule
    predicted={}
    clipped=[]
    for (x,y),colors in sorted(src.items()):
        xx,yy=d4((x,y),kind)
        target=(xx+dx,yy+dy)
        if 0<=target[0]<64 and 0<=target[1]<64:
            if target in predicted:
                raise AssertionError("D4 plus shift mapped multiple source cells together")
            predicted[target]=colors
        else:
            clipped.append({"source_xy":[x,y],
                            "native_from_to":list(colors),
                            "mapped_xy":list(target)})
    pset=set(predicted)
    actual=set(dst)
    overlap=pset&actual
    matching_labels={p for p in overlap if predicted[p]==dst[p]}
    labels_mismatched=overlap-matching_labels
    false_positive=pset-actual
    missed=actual-pset
    matches=[
        {"xy":list(p),"source_native_from_to":list(predicted[p]),
         "target_native_from_to":list(dst[p])}
        for p in sorted(labels_mismatched)
    ]
    def samples(points,owner):
        return [{"xy":list(p),"native_from_to":list(owner[p])}
                for p in sorted(points)[:12]]
    denominator=len(pset)+len(actual)
    return {
        "rule":name,"geometry":kind,"shift":[dx,dy],
        "source_changed_count":len(src),
        "target_changed_count":len(dst),
        "projected_in_bounds":len(pset),"source_clipped_count":len(clipped),
        "geometry_overlap":len(overlap),
        "geometry_mask_f1":2*len(overlap)/denominator if denominator else 1,
        "exact_mask":pset==actual and not clipped,
        "same_exact_native_color_transition_count":len(matching_labels),
        "overlap_native_color_labels_disagree_count":len(labels_mismatched),
        "from_native_color_matched_count":sum(
            predicted[p][0]==dst[p][0] for p in overlap),
        "to_native_color_matched_count":sum(
            predicted[p][1]==dst[p][1] for p in overlap),
        "unpredicted_target_count":len(missed),
        "predicted_nonchange_count":len(false_positive),
        "sample_unpredicted_target_pixels":samples(missed,dst),
        "sample_predicted_but_no_change":samples(false_positive,predicted),
        "sample_native_color_transition_mismatches":matches[:12],
        "sample_clipped_source_pixels":clipped[:12],
        "actual_target_native_color_exchange_counts":[
            {"from":a,"to":b,"count":n}
            for (a,b),n in sorted(Counter(dst.values()).items())],
        "source_native_color_exchange_counts":[
            {"from":a,"to":b,"count":n}
            for (a,b),n in sorted(Counter(src.values()).items())],
    }


def compare_pair(level0,level1,arrays):
    word=level0["word"]
    assert word==level1["word"]
    n=len(word)
    d0=level0["stage_root_index"]
    d1=level1["stage_root_index"]
    f0=arrays["level0"];f1=arrays["level1"]
    evaluations=[]
    for idx,action in enumerate(word):
        src=changed_triplets(f0[d0+idx],f0[d0+idx+1])
        dst=changed_triplets(f1[d1+idx],f1[d1+idx+1])
        models=[compare_transitions(src,dst,rule) for rule in FROZEN_MAPS]
        evaluations.append({
            "position_in_word":idx+1,"native_action":int(action),
            "source_level0_frame_before_hash":hash_grid(f0[d0+idx]),
            "target_level1_frame_before_hash":hash_grid(f1[d1+idx]),
            "model_comparisons":models,
        })
    return evaluations


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-frozen-native-color-contexts.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    arrays={}
    pair_results=[]
    for word in CONTEXT_WORDS:
        for reset in range(INDEPENDENT_RESETS):
            pair={}
            pair_arr={}
            for stage in (0,1):
                row,raw=steps_on_real_game(arcade,word,stage,reset)
                records.append(row)
                arrays[f"word_{word}_reset_{reset}_level{stage}"]=raw
                pair[stage]=row
                pair_arr[f"level{stage}"]=raw
            comparables=(pair[0]["complete"] and pair[1]["complete"])
            observations=compare_pair(pair[0],pair[1],pair_arr) if comparables else []
            pair_results.append({
                "word":word,"reset":reset,
                "both_stage_trajectories_complete":comparables,
                "level0_status":pair[0]["status"],
                "level1_status":pair[1]["status"],
                "effects":observations,
            })
    action4=[m for r in pair_results for e in r["effects"]
             if e["native_action"]==4 for m in e["model_comparisons"]]
    action5=[m for r in pair_results for e in r["effects"]
             if e["native_action"]==5 for m in e["model_comparisons"]]
    def summary(items):
        scores={}
        for name,_,_,_ in FROZEN_MAPS:
            rows=[x for x in items if x["rule"]==name]
            if not rows: continue
            overlap=sum(x["geometry_overlap"] for x in rows)
            same_label=sum(x["same_exact_native_color_transition_count"]
                           for x in rows)
            scores[name]={
                "native_transition_comparisons":len(rows),
                "total_geometry_overlap":overlap,
                "total_exact_from_to_label_matches":same_label,
                "label_match_fraction_at_overlapping_changed_pixels":
                    same_label/overlap if overlap else None,
                "mean_mask_f1":sum(x["geometry_mask_f1"] for x in rows)/len(rows),
                "total_source_clipped":sum(x["source_clipped_count"] for x in rows),
                "total_unpredicted_target_pixels":
                    sum(x["unpredicted_target_count"] for x in rows),
                "exact_mask_comparisons":sum(x["exact_mask"] for x in rows),
            }
        return scores
    def action4_residuals(model):
        rows=[
            (p,e,m)
            for p in pair_results for e in p["effects"]
            if e["native_action"]==4
            for m in e["model_comparisons"] if m["rule"]==model
        ]
        misses=Counter()
        clips=Counter()
        missing_colors=Counter()
        all_nonpredicted=[]
        for p,e,m in rows:
            for item in m["sample_unpredicted_target_pixels"]:
                x,y=item["xy"];a,b=item["native_from_to"]
                misses[(x,y,a,b)]+=1
                missing_colors[(a,b)]+=1
                all_nonpredicted.append({
                    "word":p["word"],"reset":p["reset"],
                    "step":e["position_in_word"],
                    "xy":[x,y],"native_color_change":[a,b],
                })
            for item in m["sample_clipped_source_pixels"]:
                x,y=item["source_xy"];a,b=item["native_from_to"]
                clips[(x,y,a,b)]+=1
        return {
            "native_action4_events":len(rows),
            "all_unpredicted_targets":all_nonpredicted,
            "unpredicted_native_color_pair_counts":[
                {"from":int(a),"to":int(b),"occurrences":int(n)}
                for (a,b),n in sorted(missing_colors.items())],
            "unpredicted_target_xy_native_color_frequency":[
                {"xy":[int(x),int(y)],
                 "from":int(a),"to":int(b),"occurrences":int(n)}
                for (x,y,a,b),n in sorted(misses.items())],
            "clipped_source_xy_native_color_frequency":[
                {"xy":[int(x),int(y)],
                 "from":int(a),"to":int(b),"occurrences":int(n)}
                for (x,y,a,b),n in sorted(clips.items())],
        }

    outcome={
        "kind":"SP80_FROZEN_SPATIAL_MODELS_NATIVE_COLOR_TRANSITIONS_NEW_CONTEXTS",
        "action4_residuals_translation_only":action4_residuals("translation_only"),
        "action4_residuals_reflection":action4_residuals("reflection_plus_shift"),
        "game":GAME,"source":"official native arc-agi Arcade NORMAL",
        "math_context":"original Window48 48 F3 laws; no native action correspondence",
        "prior_experiment":"WINDOW48_SP80_HELDOUT_GEOMETRY_2026-10-18.md",
        "frozen_prior_models":[{"name":n,"d4":k,"shift":[dx,dy]}
                               for n,k,dx,dy in FROZEN_MAPS],
        "new_context_words":list(CONTEXT_WORDS),
        "independent_resets_per_word_per_stage":INDEPENDENT_RESETS,
        "total_native_environment_actions":
            sum(x["real_native_actions"] for x in records),
        "actual_native_root_and_action_observations":records,
        "paired_new_context_evidence":pair_results,
        "comparably_complete_context_pairs":
            sum(r["both_stage_trajectories_complete"] for r in pair_results),
        "action4_new_context_aggregates":summary(action4),
        "action5_negative_control_aggregates":summary(action5),
        "boundary":(
            "Exact unchanged native pixel transition labels (from,to) are "
            "tested separately from changed-cell mask geometry. Fitted "
            "geometry is held fixed from earlier experiment; no new fitting, "
            "source-color-to-F3 conversion or ARC heuristic solver. "
            "Same public game fresh resets are replication, not unseen "
            "game generalization. Native level progress and F3-48 "
            "rooted conjugacy are distinct and not established here."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_FROZEN_COLOR_CONTEXTS "+json.dumps({
        "new_contexts":list(CONTEXT_WORDS),
        "native_actions":outcome["total_native_environment_actions"],
        "native_reset_count":len(records),
        "complete_pairs":outcome["comparably_complete_context_pairs"],
        "pair_count":len(pair_results),
        "action4":outcome["action4_new_context_aggregates"],
        "action5_control":outcome["action5_negative_control_aggregates"],
        "action4_residuals_translation_only":
            outcome["action4_residuals_translation_only"],
        "action4_residuals_reflection":
            outcome["action4_residuals_reflection"],
        "incomplete_pairs":[{"word":r["word"],"replicate":r["reset"],
                             "level0_status":r["level0_status"],
                             "level1_status":r["level1_status"]}
                            for r in pair_results if not r["both_stage_trajectories_complete"]],
        "word_action4":[{"word":r["word"],"reset":r["reset"],
                         "effects":[{"step":e["position_in_word"],
                           "models":[{"name":m["rule"],
                                      "geometry_overlap":m["geometry_overlap"],
                                      "actual_target_count":m["target_changed_count"],
                                      "native_transition_labels_equal":
                                          m["same_exact_native_color_transition_count"],
                                      "label_mismatch_count":
                                          m["overlap_native_color_labels_disagree_count"],
                                      "clipped":m["source_clipped_count"]}
                                     for m in e["model_comparisons"]]}
                          for e in r["effects"] if e["native_action"]==4]}
                        for r in pair_results if r["both_stage_trajectories_complete"]],
        "json":str(args.out),"raw":str(args.out.with_suffix(".npz"))
    },sort_keys=True))
    if not pair_results:
        raise RuntimeError("no native trials")


if __name__=="__main__":
    main()
