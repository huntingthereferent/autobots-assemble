"""Genuine original SP80 stage3 finite upstream-coupling trial.

Source-bound continuation of original Arcade.NORMAL CI #39552468947 and
#39553167522. Verified source 4/4-cup animation still fails official
level4. Right/down bottom-bar motion reached source x50..61 / y47..49
saturation and diminished cup coverage. Changing the same bar more is
not a new experiment.

Freeze independent upstream three-position mid-spout shifts, three
horizontal lower-bar positions, two observed upper-source configurations,
and bottom +2/+3 near the measured source boundary. This does NOT model
undocumented engine rules, reconstruct a substitute game, or assert that
cup/boundary colors are a source objective. Only actual original SDK
levels_completed>=4 or WIN counts as progress.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

# Both upper interventions were directly witnessed in the original native
# #39552468947 four-cup transient signals with late source boundary.
UPPER=(
    ("selected_right2","6@20,18 4 4"),
    ("other_left2","6@40,18 3 3"),
)
CUPS=((8,16),(26,34),(38,46),(50,58))

def horizontal(click, action, n):
    return "6@%d,%d "%click+" ".join([str(action)]*n)

def plan(upper, mid, lower, bottom):
    return " ".join((
        upper,
        horizontal((10,30),4,mid),
        horizontal((46,33),3,lower),
        horizontal((40,42),4,bottom),
        "5",
    ))

# All 36 crossed plans are prospectively declared; do not select a winner
# based on the source color-feedback measure and silently skip negatives.
FROZEN=tuple(
    (f"{u}_mid{m}_lowerleft{l}_bottomright{b}",plan(word,m,l,b))
    for u,word in UPPER
    for m in (3,4,5)
    for l in (9,10,11)
    for b in (2,3)
)+(
    ("no_upper_mid4_lowerleft10_bottomright2",
     " ".join((
         horizontal((10,30),4,4),horizontal((46,33),3,10),
         horizontal((40,42),4,2),"5"))),
    ("no_upper_mid4_lowerleft10_bottomright3",
     " ".join((
         horizontal((10,30),4,4),horizontal((46,33),3,10),
         horizontal((40,42),4,3),"5"))),
)
assert len(FROZEN)==38==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(word))<=32
    and parse_plan(word)[-1][0]==5
    and sum(a==5 for a,_ in parse_plan(word))==1
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word in FROZEN
)

def actual_frame_metrics(pre, frames):
    if pre.shape!=(64,64):
        raise AssertionError("Unexpected genuine source frame shape")
    first_full=[None]*4
    first_simultaneous_four=None
    first_bottom_change=None
    max_simultaneous=0
    # This is a source pixel comparison, not a simulator's fluid model.
    for t, frame in enumerate(frames):
        if frame.shape!=(64,64):
            raise AssertionError("Unexpected returned SDK frame shape")
        cups=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&
                (frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUPS
        ]
        for i,count in enumerate(cups):
            if count==45 and first_full[i] is None:first_full[i]=t
        now=sum(v==45 for v in cups)
        max_simultaneous=max(max_simultaneous,now)
        if now==4 and first_simultaneous_four is None:
            first_simultaneous_four=t
        changed=(pre[59:63,2:62]!=frame[59:63,2:62])
        if changed.any() and first_bottom_change is None:
            first_bottom_change={
                "native_returned_frame_index":t,
                "actual_source_bottom_changed_pixels":int(changed.sum()),
                "observed_new_source_palette6_x_at_y58":[int(x) for x
                    in np.where((pre[58]!=6)&(frame[58]==6))[0]],
            }
    bars=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (8,9) and 15<=c["bbox"][1]<=49
    ]
    return {
        "true_original_pre_pour_blake2b16":hash_frame(pre),
        "true_original_final_pour_blake2b16":hash_frame(frames[-1]),
        "actual_original_SDK_pour_frame_count":len(frames),
        "source_pre_pour_palette8_9_component_bboxes":bars,
        "first_per_cup_palette11_to13_full_frames":first_full,
        "first_simultaneous_four_cup_source_frame":first_simultaneous_four,
        "max_simultaneous_source_full_cups":max_simultaneous,
        "first_observed_bottom_y59_62_boundary_change":first_bottom_change,
        "no_observed_bottom_test_region_change":first_bottom_change is None,
        "source_boundary":"This does NOT prove no spill or infer engine win conditions.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    all_rows=[];all_raw={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,stage1_word in STAGE1_WITNESSES:
            original,stacks=real_trial(witness,stage1_word,case,word)
            roots.add(original["original_verified_stage3_root"]["original_source_sha256"])
            pour=stacks.get("stage3_"+str(n))
            pre=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            measurements=actual_frame_metrics(pre,pour) if pour is not None else None
            rec={
                "precommitted_native_control":case,
                "independent_source_witness":witness,
                "exact_original_sdk_word":word,
                "official_original_final_level":original["official_original_final_level"],
                "official_original_final_state":original["official_original_final_state"],
                "actual_original_sdk_level4_or_WIN":original["official_original_level4_or_WIN"],
                "native_sdk_disposition":original["trial_disposition"],
                "original_native_visual_observations":measurements,
                "genuine_original_sdk_action_receipts":[
                    {k:v for k,v in event.items()
                     if k!="full_original_source_frame_ledger"}
                    for event in original["full_original_sdk_action_events"]
                ],
            }
            all_rows.append(rec)
            for phase,arr in stacks.items():
                all_raw[f"{case}_{witness}_{phase}"]=arr
            print("ORIGINAL_SP80_UPSTREAM_JOINT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "sdk_level":rec["official_original_final_level"],
                "sdk_state":rec["official_original_final_state"],
                "visual":measurements,
            },sort_keys=True),flush=True)
    if len(all_rows)!=76 or len(roots)!=1:
        raise AssertionError("Actual independent source SDK witness mismatch")
    successes=[
        {"case":r["precommitted_native_control"],"witness":r["independent_source_witness"],
         "level":r["official_original_final_level"],"state":r["official_original_final_state"],
         "true_original_source_word":r["exact_original_sdk_word"]}
        for r in all_rows if r["actual_original_sdk_level4_or_WIN"]
    ]
    visually_full_and_no_boundary=[
        {"case":r["precommitted_native_control"],"witness":r["independent_source_witness"]}
        for r in all_rows if r["original_native_visual_observations"] is not None
        and r["original_native_visual_observations"]["max_simultaneous_source_full_cups"]==4
        and r["original_native_visual_observations"]["no_observed_bottom_test_region_change"]
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_UPSTREAM_PAIRWISE_ROUTING_RELATIONS",
        "actual_source_native_antecedents":[39551239285,39552468947,39553167522],
        "authentic_independently_reset_original_sdk_games":len(all_rows),
        "prospectively_frozen_original_native_words":FROZEN,
        "real_source_stage3_entry_blake2b16":next(iter(roots),
        ),
        "original_sdk_official_level4_or_WIN_count":len(successes),
        "actual_native_sdk_success_witnesses":successes,
        "visual_only_four_cups_without_test_region_change":visually_full_and_no_boundary,
        "original_sdk_official_level_histogram":dict(Counter(str(x["official_original_final_level"]) for x in all_rows)),
        "original_sdk_official_state_histogram":dict(Counter(str(x["official_original_final_state"]) for x in all_rows)),
        "original_sdk_native_receipts":all_rows,
        "limits":"Source pixels are observations, not game physics, or hidden objective. Only genuine native SDK level>=4 or WIN establishes progress. Raw SDK arrays in NPZ; F3, WORLD, NIH, ownership and separate lanes unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_raw)
    print("ORIGINAL_SP80_UPSTREAM_JOINT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_original_native_words","original_sdk_native_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
