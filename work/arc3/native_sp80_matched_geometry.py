"""Original SP80 native: matched action age, different selected-bar geometry.

Prior independent original SDK studies:
- Stage1 ACTION5 response stacks have 22/23/26/28 real returned frames.
- 42 ACTION5 calls with exactly same pre-action *interior* across
  differing row63/history all returned 22 with identical color6/color11
  traces, without establishing generality or hidden-state equivalence.

NEW prospective contrast: three *coordinate-selected* source objects,
each with the SAME native ACTION6 count and identical ACTION1..4 suffix
and ACTION5 placement. Every selected bar has source pixel coordinates
actually witnessed at native root. Preserve native pre-ACTION5 entire
screen, interior, row63 hashes and all returned SDK animation images.

No claim these placements solve SP80: official SDK level2/WIN alone
counts as progress. Always retain failed comparisons and raw evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_action5_temporal_factorial import temporal_events
from .native_sp80_multi_select import parse_plan

TARGETS=(
    ("original_selected_color9",(24,37)),
    ("lower_color8",(32,25)),
    ("upper_color8",(12,17)),
)
SUFFIXES=(
    ("up_then_right","1 4"),
    ("right_then_up","4 1"),
    ("two_right","4 4"),
    ("down_then_right","2 4"),
    ("two_left","3 3"),
    ("up_then_down","1 2"),
    ("up_right_down","1 4 2"),
    ("two_right_down","4 4 2"),
)
PLANS=tuple(
 (target+"_"+suffix,f"6@{xy[0]},{xy[1]} {actions} 5")
 for target,xy in TARGETS for suffix,actions in SUFFIXES
)
RESETS=2
assert len(PLANS)==24 and len({n for n,_ in PLANS})==24
assert RESETS==2
assert all(any(a==6 and xy is not None for a,xy in parse_plan(w))
           and parse_plan(w)[-1][0]==5 for _,w in PLANS)


def compare_by_equal_prefix(trials):
    groups=defaultdict(list)
    for t in trials:
        plan=t["name"]
        target=next(n for n,_ in TARGETS if plan.startswith(n+"_"))
        suffix=plan[len(target)+1:]
        entries=[e for e in t["source_actual_A5_examination"]
                 if "real_sdk_returned_frame_count" in e]
        for e in entries:
            groups[suffix].append({
                "source_target":target,
                "actual_program":t["source_native_program"],
                "replicate":t["replicate"],
                "native_A5_step":e["context_action"],
                "original_preaction_interior_hash":e["original_preaction_interior_y1_to62_hash"],
                "original_preaction_entire_screen_hash":e["original_preaction_full_64x64_hash"],
                "original_preaction_row63_hash":e["original_preaction_row63_hash"],
                "source_native_A5_returned_frames":e["real_sdk_returned_frame_count"],
                "source_color6_animation_counts":e["source_color6_counts_per_frame"],
                "source_color11_animation_counts":e["source_color11_counts_per_frame"],
                "original_final_level":t["original_last_source_level"],
                "original_final_state":t["original_last_source_state"],
            })
    return {suffix:{
       "actual_source_events":len(events),
       "predeclared_native_targets":sorted({e["source_target"] for e in events}),
       "source_A5_context_steps":sorted({e["native_A5_step"] for e in events}),
       "different_native_preaction_interiors":len({
           e["original_preaction_interior_hash"] for e in events}),
       "different_native_preaction_entire_screens":len({
           e["original_preaction_entire_screen_hash"] for e in events}),
       "different_native_row63_states":len({
           e["original_preaction_row63_hash"] for e in events}),
       "original_A5_frame_count_frequencies":dict(Counter(
           str(e["source_native_A5_returned_frames"]) for e in events)),
       "different_color6_temporal_sequences":len({
           tuple(e["source_color6_animation_counts"]) for e in events}),
       "different_color11_temporal_sequences":len({
           tuple(e["source_color11_animation_counts"]) for e in events}),
       "original_source_events":events,
    } for suffix,events in groups.items()}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,source_frames=[],{}
    for name,word in PLANS:
        for replicate in range(RESETS):
            trial,frames=one(name,word,replicate)
            trial["source_actual_A5_examination"]=temporal_events(trial,frames)
            trials.append(trial)
            for phase,stack in frames.items():
                source_frames[f"{name}_reset{replicate}_{phase}"]=stack

    actual5=[e for t in trials for e in t["source_actual_A5_examination"]
             if "real_sdk_returned_frame_count" in e]
    groups=compare_by_equal_prefix(trials)
    result={
      "kind":"ORIGINAL_SP80_MATCHED_ACTION_AGE_SOURCE_GEOMETRY_VARIATION",
      "source_predeclared_coordinate_targets":TARGETS,
      "source_predeclared_equal_movement_suffixes":SUFFIXES,
      "frozen_original_native_programs":PLANS,
      "new_independent_native_resets_per_program":RESETS,
      "actual_original_game_resets":len(trials),
      "actual_original_sdk_action_calls":sum(t["actual_native_calls"] for t in trials),
      "real_original_ACTION5_events":len(actual5),
      "actual_original_A5_frame_length_frequency":dict(Counter(
         str(e["real_sdk_returned_frame_count"]) for e in actual5)),
      "original_native_stage2_or_WIN":sum(int(t["native_level2_or_win"]) for t in trials),
      "source_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
      "equal_age_target_contrasts":groups,
      "original_native_full_source_trial_evidence":trials,
      "limits":"Official original SP80 SDK with proper coordinate ACTION6. Matched SDK step count does not establish identical hidden state, selected bar identity or objective. All true original returned frame arrays retained. Only levels_completed >=2 or SDK WIN constitutes source-native game progress.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_frames)
    print("SP80_NATIVE_GEOMETRY_MATCH "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("equal_age_target_contrasts","original_native_full_source_trial_evidence")
    },sort_keys=True))
    if len(trials)!=len(PLANS)*RESETS:
       raise RuntimeError("Missing prospectively required real original resets")


if __name__=="__main__":
    main()
