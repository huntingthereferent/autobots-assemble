"""Independent original SP80 ACTION5 SDK animation temporal-signature holdout.

PR #183 retained 2,258 real SDK-returned 64x64 frames. All 20 tested
stage1 ACTION5 responses were 22 frames, with frozen native color6
ramp and color11 blink sequences. This follow-up freezes the EXACT
source-observed temporal signatures before running different,
independently reset original-game action histories.

This is a hypothesis TEST, not a rule encoded into the native game:
counterexamples are recorded rather than causing the worker to
falsely declare a win or drop evidence. The original SDK's level
counter and WIN/GAME_OVER remain the only legitimate objective signals.

Every native ACTION6 click has a real (x,y) data object; all actual
SDK-returned arrays and full original color transitions are preserved.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

PLANS=(
    ("lower_select_mixed_move","6@32,25 1 4 3 5"),
    ("upper_select_mixed_move","6@12,17 2 3 1 5"),
    ("lower_upper_mixed_move","6@32,25 6@12,17 3 3 1 5"),
    ("upper_lower_mixed_move","6@12,17 6@32,25 4 4 2 5"),
    ("contact_then_click_move","1 1 1 6@32,25 2 2 5"),
    ("upper_select_up_right","6@12,17 1 1 4 4 5"),
    ("lower_with_two_ACTION5","6@32,25 1 5 4 5"),
    ("upper_with_two_ACTION5","6@12,17 3 5 4 5"),
    ("late_right24_then_ACTION5"," ".join(["4"]*24+["5"])),
    ("late_up24_then_ACTION5"," ".join(["1"]*24+["5"])),
)
RESETS=2

# SOURCE-FROZEN from independent PR #183 BEFORE this experiment.
# Frames numbered 0..21 (not elapsed seconds).
FROZEN_ACTION5_COLOR6_COUNTS=tuple(
    [16*i for i in range(1,15)]+[224]*7+[16])
FROZEN_ACTION5_COLOR11_COUNTS=tuple(
    [240]*15+[0,240,0,240,0,0,240])
assert len(FROZEN_ACTION5_COLOR6_COUNTS)==22
assert len(FROZEN_ACTION5_COLOR11_COUNTS)==22
assert len(PLANS)==len(set(name for name,_ in PLANS))==10
assert RESETS==2
assert all(any(a==5 for a,_ in parse_plan(p)) for _,p in PLANS)
assert all(a!=6 or xy is not None for _,program in PLANS
           for a,xy in parse_plan(program))


def phase_counts(stack,color):
    return [int(np.count_nonzero(frame==color)) for frame in stack]


def inspect_original_ACTION5_frames(record,raw):
    events=[]
    for e in record["real_sdk_observation_ledger"]:
        if e["phase"]!="context" or e["native_action_id"]!=5:
            continue
        key="context_"+str(e["phase_action_number"])
        if key not in raw or "source_animation" not in e:
            events.append({"source_sdk_context_action":e["phase_action_number"],
                           "status":"UNKNOWN_SOURCE_FRAME_STACK_NOT_RETURNED",
                           "original_SDK_state":e["original_source_state_after"],
                           "original_SDK_level":e["original_source_level_after"]})
            continue
        stack=raw[key]
        counts6=phase_counts(stack,6)
        counts11=phase_counts(stack,11)
        counts9=phase_counts(stack,9)
        valid_full=tuple(stack.shape[1:])==(64,64)
        after=e["original_source_state_after"]
        if not valid_full:
            raise AssertionError("Original native frame shape changed after admission")
        if len(stack)!=e["source_animation"]["true_original_returned_frames"]:
            raise AssertionError("Real NPZ frame stack diverges from source event JSON")
        entry={
            "source_sdk_context_action":e["phase_action_number"],
            "real_native_response_frame_shape":list(stack.shape),
            "original_sdk_state":after,
            "original_sdk_levels_completed":e["original_source_level_after"],
            "real_original_color6_counts_by_returned_frame":counts6,
            "real_original_color11_counts_by_returned_frame":counts11,
            "real_original_color9_counts_by_returned_frame":counts9,
            "frozen_hypothesis_H1_22_returned_frames":len(stack)==22,
            "frozen_hypothesis_H2_color6_counts_match":tuple(counts6)==FROZEN_ACTION5_COLOR6_COUNTS,
            "frozen_hypothesis_H3_color11_blink_counts_match":tuple(counts11)==FROZEN_ACTION5_COLOR11_COUNTS,
            "frozen_hypothesis_H4_selected_color9_absent_intermediate":all(c==0 for c in counts9[:-1]),
            "original_sdk_returned_transient_native_pixels":e["source_animation"]["original_transient_pixels_returning_to_old_color"],
            "native_last_image_changed_pixel_count":e["source_animation"]["original_before_to_final_pixel_count"],
            "source_frame_order_and_deltas_preserved":True,
        }
        events.append(entry)
    return events


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    source,arrays=[],{}
    for name,program in PLANS:
        for replicate in range(RESETS):
            actual,frames=one(name,program,replicate)
            actual["new_original_ACTION5_temporal_validation"]=inspect_original_ACTION5_frames(actual,frames)
            source.append(actual)
            for phase,array in frames.items():
                arrays[f"{name}_reset{replicate}_{phase}"]=array

    all5=[event for trial in source for event in trial["new_original_ACTION5_temporal_validation"]]
    valid5=[e for e in all5 if "frozen_hypothesis_H1_22_returned_frames" in e]
    flags=(
        "frozen_hypothesis_H1_22_returned_frames",
        "frozen_hypothesis_H2_color6_counts_match",
        "frozen_hypothesis_H3_color11_blink_counts_match",
        "frozen_hypothesis_H4_selected_color9_absent_intermediate",
    )
    metrics={flag:{
        "observed_source_events":len(valid5),
        "matched":sum(bool(e[flag]) for e in valid5),
        "counterexamples":[{
            "trial":trial["name"],"replicate":trial["replicate"],
            "context_action":e["source_sdk_context_action"]
        } for trial in source for e in trial["new_original_ACTION5_temporal_validation"]
          if flag in e and not e[flag]],
    } for flag in flags}
    comparisons={}
    for name,program in PLANS:
        trials=[x for x in source if x["name"]==name]
        comparisons[name]={
            "original_actions":program,
            "replicate_native_states":[t["original_last_source_state"] for t in trials],
            "replicate_native_levels":[t["original_last_source_level"] for t in trials],
            "replicate_native_dispositions":[t["actual_source_disposition"] for t in trials],
            "returned_ACTION5_frame_counts":[{
                "context_action":e["source_sdk_context_action"],
                "returned_frames":e.get("real_native_response_frame_shape",[None])[0],
                "color6_counts":e.get("real_original_color6_counts_by_returned_frame"),
                "color11_counts":e.get("real_original_color11_counts_by_returned_frame"),
                "color9_counts":e.get("real_original_color9_counts_by_returned_frame"),
            } for t in trials for e in t["new_original_ACTION5_temporal_validation"]],
        }
    out={
        "kind":"SP80_GENUINE_ORIGINAL_NATIVE_HOLDOUT_ACTION5_TEMPORAL_SIGNATURE",
        "frozen_preceding_source":"PR183 original native SDK frames, artifact 12191772198",
        "predeclared_ACTION5_frame_signatures":{
            "num_frames":22,
            "source_color6_counts":FROZEN_ACTION5_COLOR6_COUNTS,
            "source_color11_counts":FROZEN_ACTION5_COLOR11_COUNTS,
            "color9_zeros_on_intermediate":True,
        },
        "predeclared_original_game_native_programs":PLANS,
        "genuine_resets_per_program":RESETS,
        "true_native_source_resets":len(source),
        "original_native_sdk_actions":sum(t["actual_native_calls"] for t in source),
        "source_new_valid_ACTION5_events":len(valid5),
        "source_new_total_returned_ACTION5_images":sum(
            e["real_native_response_frame_shape"][0] for e in valid5),
        "source_actual_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in source),
        "native_dispositions":dict(Counter(t["actual_source_disposition"] for t in source)),
        "frozen_source_hypothesis_results":metrics,
        "original_per_program":comparisons,
        "genuine_source_native_trial_evidence":source,
        "limits":"Out-of-sample genuine SDK observation; H1-H4 apply to tested stage1 ACTION5 only. Frame counts and pixel counts are not clock time, source objective or hidden engine mechanism. Source levels_completed/WIN only objective evidence. Full original returned frame stacks retained.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_ACTION5_TEMPORAL_HOLDOUT "+json.dumps({
        k:v for k,v in out.items() if k not in ("genuine_source_native_trial_evidence","original_per_program")
    },sort_keys=True))
    if len(source)!=len(PLANS)*RESETS:
        raise AssertionError("Not all native games reset")


if __name__=="__main__":
    main()
