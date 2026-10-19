"""Original SP80 ACTION5 temporal-factor contrasts after six real frame-count counterexamples.

Held-out original SDK experiment #184 falsified global 22-frame ACTION5:
upper->lower selection with 442 generated 23 frames; repeated ACTION5
generated 28 frames. Here freeze matched selection ORDER and movement
SUFFIX, and compare prior-ACTION5 timing within actual SDK stage1.

No invented source state equality or assumption of causality: save
PRE-action entire original source interior and boundary frame SHA
separately; after all native trials, group exactly matching interiors
and check source frame counts and animation pulse. Preserve every SDK
returned image, every pixel/color frame transition, SDK state and level.
Every ACTION6 supplies explicit native data={'x':x,'y':y}.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from hashlib import blake2b
from pathlib import Path
import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

PAIRS=(
    ("upper_lower_only","6@12,17 6@32,25 5"),
    ("lower_upper_only","6@32,25 6@12,17 5"),
    ("upper_lower_442","6@12,17 6@32,25 4 4 2 5"),
    ("lower_upper_442","6@32,25 6@12,17 4 4 2 5"),
    ("upper_lower_331","6@12,17 6@32,25 3 3 1 5"),
    ("lower_upper_331","6@32,25 6@12,17 3 3 1 5"),
    ("upper_lower_244","6@12,17 6@32,25 2 4 4 5"),
    ("lower_upper_244","6@32,25 6@12,17 2 4 4 5"),
)
REPEATED=(
    ("lower_1_55","6@32,25 1 5 5"),
    ("lower_1_545","6@32,25 1 5 4 5"),
    ("lower_14_55","6@32,25 1 4 5 5"),
    ("lower_14_545","6@32,25 1 4 5 4 5"),
    ("upper_3_55","6@12,17 3 5 5"),
    ("upper_3_545","6@12,17 3 5 4 5"),
    ("upper_34_55","6@12,17 3 4 5 5"),
    ("upper_34_545","6@12,17 3 4 5 4 5"),
)
PLANS=PAIRS+REPEATED
RESETS=2
assert len(PLANS)==len(set(name for name,_ in PLANS))==16
assert all(any(n==5 for n,xy in parse_plan(w)) and all(
    n!=6 or xy is not None for n,xy in parse_plan(w)) for _,w in PLANS)


def hashed(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()


def temporal_events(trial,source):
    output=[]
    for e in trial["real_sdk_observation_ledger"]:
        if e["phase"]!="context" or e["native_action_id"]!=5:
            continue
        index=e["phase_action_number"]
        key="context_"+str(index)
        if key not in source or "source_animation" not in e:
            output.append({"context_action":index,"state":"UNKNOWN_SOURCE_STACK"})
            continue
        before=source["entry_6"][-1] if index==1 else source["context_"+str(index-1)][-1]
        stack=source[key]
        if len(stack)!=e["source_animation"]["true_original_returned_frames"]:
            raise AssertionError("Original native source JSON/NPZ returned frame mismatch")
        results={
            "context_action":index,
            "real_sdk_returned_frame_count":len(stack),
            "original_preaction_full_64x64_hash":hashed(before),
            "original_preaction_interior_y1_to62_hash":hashed(before[1:63]),
            "original_preaction_row63_hash":hashed(before[63]),
            "genuine_prior_ACTION5_count":sum(
                x["native_action_id"]==5 and x["phase"]=="context" and
                x["phase_action_number"]<index for x in trial["real_sdk_observation_ledger"]),
            "source_color6_counts_per_frame":[int(np.count_nonzero(f==6)) for f in stack],
            "source_color11_counts_per_frame":[int(np.count_nonzero(f==11)) for f in stack],
            "source_color9_counts_per_frame":[int(np.count_nonzero(f==9)) for f in stack],
            "source_sdk_state_after":e["original_source_state_after"],
            "source_sdk_levels_after":e["original_source_level_after"],
            "original_transient_return_to_source_precolor":e["source_animation"]["original_transient_pixels_returning_to_old_color"],
            "source_last_frame_hash":hashed(stack[-1]),
        }
        output.append(results)
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    evidence,arrays=[],{}
    for name,actions in PLANS:
        for replicate in range(RESETS):
            trial,actual=one(name,actions,replicate)
            trial["native_ACTION5_temporal_examination"]=temporal_events(trial,actual)
            evidence.append(trial)
            for key,arr in actual.items():
                arrays[f"{name}_reset{replicate}_{key}"]=arr

    grouped=defaultdict(list)
    outcome={}
    for trial in evidence:
        results=trial["native_ACTION5_temporal_examination"]
        outcome.setdefault(trial["name"],[]).append({
            "replicate":trial["replicate"],
            "real_native_actions":trial["actual_native_calls"],
            "SDK_levels_completed":trial["original_last_source_level"],
            "SDK_game_state":trial["original_last_source_state"],
            "native_terminal_disposition":trial["actual_source_disposition"],
            "actual_ACTION5_returned_frame_counts":[
                r.get("real_sdk_returned_frame_count") for r in results],
            "actual_native_ACTION5_temporal_events":results,
        })
        for event in results:
            if "real_sdk_returned_frame_count" not in event:continue
            k=event["original_preaction_interior_y1_to62_hash"]
            grouped[k].append({
                "trial":trial["name"],
                "replicate":trial["replicate"],
                "prior_ACTION5":event["genuine_prior_ACTION5_count"],
                "native_preaction_y63":event["original_preaction_row63_hash"],
                "source_frames":event["real_sdk_returned_frame_count"],
                "source_color6_counts":event["source_color6_counts_per_frame"],
            })

    observed_matching_interior=[]
    for key,group in grouped.items():
        distinct_words={g["trial"] for g in group}
        if len(distinct_words)<2:continue
        observed_matching_interior.append({
            "source_preaction_interior_digest":key,
            "independent_game_events":len(group),
            "different_words":sorted(distinct_words),
            "different_native_frame_counts":sorted({g["source_frames"] for g in group}),
            "distinct_color6_phase_sequences":len({
                tuple(g["source_color6_counts"]) for g in group}),
            "observed_source_events":group,
        })

    all5=[e for t in evidence for e in t["native_ACTION5_temporal_examination"]]
    valid=[e for e in all5 if "real_sdk_returned_frame_count" in e]
    output={
        "kind":"GENUINE_ORIGINAL_SP80_ACTION5_SELECTION_ORDER_AND_PRIOR_ACTION5_FACTORIAL",
        "native_source_predeclared_selection_order_controls":PAIRS,
        "native_source_predeclared_prior_ACTION5_controls":REPEATED,
        "independently_reset_source_games_per_control":RESETS,
        "real_original_SDK_resets":len(evidence),
        "actual_native_action_responses":sum(e["actual_native_calls"] for e in evidence),
        "genuine_original_ACTION5_responses":len(valid),
        "original_SDK_ACTION5_returned_frame_counts":dict(Counter(
            str(e["real_sdk_returned_frame_count"]) for e in valid)),
        "observed_first_ACTION5_frame_counts":dict(Counter(str(e["real_sdk_returned_frame_count"]) for e in valid
            if e["genuine_prior_ACTION5_count"]==0)),
        "observed_subsequent_ACTION5_frame_counts":dict(Counter(str(e["real_sdk_returned_frame_count"]) for e in valid
            if e["genuine_prior_ACTION5_count"]>0)),
        "genuine_level2_or_WIN":sum(int(e["native_level2_or_win"]) for e in evidence),
        "native_source_dispositions":dict(Counter(e["actual_source_disposition"] for e in evidence)),
        "source_exact_same_preaction_interior_comparisons":observed_matching_interior,
        "real_native_programs":outcome,
        "complete_original_SDK_source_evidence":evidence,
        "limitations":"Original Arcade.NORMAL source only. All returned frames preserved and all ACTION6 coordinates explicit. Selection order and prior ACTION5 histories are tested, not assumed sufficient causes of animation-length changes; matching interior does not imply matching full native state or hidden state. Only source SDK level2 or WIN is game progress.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_ACTION5_FACTORIAL "+json.dumps({
        k:v for k,v in output.items() if k not in
            ("complete_original_SDK_source_evidence","real_native_programs","source_exact_same_preaction_interior_comparisons")
    },sort_keys=True))
    if len(evidence)!=len(PLANS)*RESETS:
        raise AssertionError("Missing original native source reset")


if __name__=="__main__":
    main()
