"""Original SP80: same native pre-action interior, varied history and boundary.

The independently source-replayed prior ACTION5 holdouts witnessed genuine
SDK animation lengths 22,23,26,28. They did not establish that an
identical current visible interior determines temporal output.

Freeze 16 distinct native stage1 programs before executing new
original Arcade.NORMAL games. 12/21 and 34/43 were previously
observed to restore interior pixels on the genuine stage1 root;
their native action histories and bottom-row timing still differ.
Use the actual original SDK full obs.frame return stacks. Group only
BYTE-IDENTICAL original pre-ACTION5 interior arrays by hash and inspect
actual bottom-row divergence, prior ACTION5 and full return sequence.

No inferred hidden state, no cloned game, no refitted template, no win
claim from source pixels. Original SDK WIN/level counter only objective.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_action5_temporal_factorial import temporal_events
from .native_sp80_multi_select import parse_plan

PROGRAMS=(
 ("root_A5","5"),
 ("pair12_A5","1 2 5"),
 ("pair21_A5","2 1 5"),
 ("pair34_A5","3 4 5"),
 ("pair43_A5","4 3 5"),
 ("pair1212_A5","1 2 1 2 5"),
 ("pair3434_A5","3 4 3 4 5"),
 ("pair1234_A5","1 2 3 4 5"),
 ("pair3412_A5","3 4 1 2 5"),
 ("pair1221_A5","1 2 2 1 5"),
 ("pair3443_A5","3 4 4 3 5"),
 ("root_A5A5","5 5"),
 ("pair12_A5A5","1 2 5 5"),
 ("pair34_A5A5","3 4 5 5"),
 ("A5_pair12_A5","5 1 2 5"),
 ("A5_pair34_A5","5 3 4 5"),
)
RESETS=2
assert len(PROGRAMS)==len(set(n for n,_ in PROGRAMS))==16
assert RESETS==2
assert all(any(a==5 for a,_ in parse_plan(p)) and all(a<=5 for a,_ in parse_plan(p))
           for _,p in PROGRAMS)


def describe_matching_interiors(records):
    groups=defaultdict(list)
    for t in records:
        for e in t["actual_NATIVE_ACTION5_temporal_observations"]:
            if "real_sdk_returned_frame_count" not in e:continue
            groups[e["original_preaction_interior_y1_to62_hash"]].append({
                "source_word":t["name"],
                "original_replicate":t["replicate"],
                "prior_ACTION5_count":e["genuine_prior_ACTION5_count"],
                "before_entire_screen":e["original_preaction_full_64x64_hash"],
                "before_native_y63":e["original_preaction_row63_hash"],
                "frame_count":e["real_sdk_returned_frame_count"],
                "source_color6_frame_series":e["source_color6_counts_per_frame"],
                "source_color11_frame_series":e["source_color11_counts_per_frame"],
                "source_color9_frame_series":e["source_color9_counts_per_frame"],
                "source_action_step":e["context_action"],
            })
    comparable=[]
    for hash_,observations in groups.items():
        words={x["source_word"] for x in observations}
        if len(words)<2:continue
        series={(tuple(x["source_color6_frame_series"]),
                  tuple(x["source_color11_frame_series"]))
                for x in observations}
        counts={x["frame_count"] for x in observations}
        boundaries={x["before_native_y63"] for x in observations}
        full={x["before_entire_screen"] for x in observations}
        comparable.append({
            "pre_A5_original_interior_hash":hash_,
            "source_events":len(observations),
            "different_histories":sorted(words),
            "distinct_preaction_native_row63_hash_count":len(boundaries),
            "distinct_preaction_full_screen_hash_count":len(full),
            "different_returned_A5_frame_lengths":sorted(counts),
            "distinct_original_color6_color11_frame_series":len(series),
            "source_level1_history_comparisons":observations,
        })
    return comparable


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records,stacks=[],{}
    for name,program in PROGRAMS:
        for replicate in range(RESETS):
            trial,raw=one(name,program,replicate)
            trial["actual_NATIVE_ACTION5_temporal_observations"]=temporal_events(trial,raw)
            records.append(trial)
            for key,arr in raw.items():
                stacks[f"{name}_reset{replicate}_{key}"]=arr
    all5=[e for r in records for e in r["actual_NATIVE_ACTION5_temporal_observations"]]
    valid5=[e for e in all5 if "real_sdk_returned_frame_count" in e]
    matching=describe_matching_interiors(records)
    counterexamples=[{
        "interior":x["pre_A5_original_interior_hash"],
        "source_histories":x["different_histories"],
        "different_frame_lengths":x["different_returned_A5_frame_lengths"],
        "different_color_series":x["distinct_original_color6_color11_frame_series"],
    } for x in matching if len(x["different_returned_A5_frame_lengths"])>1
        or x["distinct_original_color6_color11_frame_series"]>1]
    result={
        "kind":"ORIGINAL_SP80_EQUAL_PREACTION_INTERIOR_DIFFERENT_HISTORY_NATIVE_A5",
        "prospectively_fixed_original_source_programs":PROGRAMS,
        "independent_native_resets_per_program":RESETS,
        "genuine_native_original_games":len(records),
        "valid_original_native_action_responses":sum(r["actual_native_calls"] for r in records),
        "valid_original_ACTION5_events":len(valid5),
        "actual_A5_returned_frame_length_frequencies":dict(Counter(
            str(e["real_sdk_returned_frame_count"]) for e in valid5)),
        "source_SDK_level2_or_WIN":sum(int(r["native_level2_or_win"]) for r in records),
        "actual_source_native_dispositions":dict(Counter(r["actual_source_disposition"] for r in records)),
        "matched_exact_preaction_interior_groups":matching,
        "matched_interior_temporal_counterexamples":counterexamples,
        "genuine_source_original_trial_evidence":records,
        "limits":"Only original public Arcade.NORMAL SDK. Source exact interior hash does not prove complete screen/hidden state equality. Returned frame counts and pixel series are only native observations; level2/WIN is the sole game success criterion. All source frames saved as NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_EXACT_INTERIOR_HOLDOUT "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("matched_exact_preaction_interior_groups","genuine_source_original_trial_evidence")
    },sort_keys=True))
    if len(records)!=len(PROGRAMS)*RESETS:
        raise AssertionError("Missing independently reset original SDK game")


if __name__=="__main__":
    main()
