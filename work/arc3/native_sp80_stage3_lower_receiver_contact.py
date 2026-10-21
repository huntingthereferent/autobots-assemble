"""Actual original SP80 SDK: vertical receiver contact after fourth-cup restoration.

This targeted native trial follows PR #344 original run #39556575290:
the actual original upper-selected right2/down1 and other-upper down1
movement restores all four visible cup11->13 regions at source frame29,
then original y59..62 boundary changes at frame30. With other-upper held
the 4th region never fully changes, but measured test boundary stays
unchanged. The actual source frames show the extra rightward palette6
path before the bottom event.

Vary the receiving lower-right original bar height, or bottom catcher's
height, without changing verified upstream source pair. Test source
movement and order, not a guessed mechanical fluid model. Only original
SDK official level>=4 or WIN proves advancement. No leaked game source
or simulation is used.
"""
from __future__ import annotations

import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

UPPER_SELECTED="6@20,18 4 4 2"
OTHER_DOWN="6@40,18 2"
MID_RIGHT4="6@10,30 4 4 4 4"
LOWER_LEFT10=" ".join(["3"]*10)
CUP_RANGES=((8,16),(26,34),(38,46),(50,58))
OBSERVE_RIGHT=((19,32),(29,50),(41,53),(52,56),(58,56))

def lower(direction=None,count=0,vertical_first=True):
    horizontal=LOWER_LEFT10
    vertical=" ".join([str(direction)]*count)
    if vertical_first:
        return " ".join(p for p in ("6@46,33",vertical,horizontal) if p)
    return " ".join(p for p in ("6@46,33",horizontal,vertical) if p)

def bottom(right=2,vertical=None):
    steps=["4"]*right
    if vertical is not None:
        steps.append(str(vertical))
    return " ".join(["6@40,42",*steps])

def word(upper,lower_word,bottom_word):
    return " ".join(p for p in [upper,MID_RIGHT4,lower_word,bottom_word,"5"] if p)

FULL_UPPER=" ".join([UPPER_SELECTED,OTHER_DOWN])
FROZEN=(
    ("four_cup_late_boundary_parent",word(FULL_UPPER,lower(),bottom())),
    ("clean_three_cup_parent",word(UPPER_SELECTED,lower(),bottom())),
    *(
        (
            f"receiver_{tag}{n}_{'before' if earlier else 'after'}",
            word(FULL_UPPER,lower(direction,n,earlier),bottom())
        )
        for tag,direction in (("up",1),("down",2))
        for n in (1,2,3)
        for earlier in (True,False)
    ),
    *(
        (
            f"receiver_{tag}1_bottom_right{right}",
            word(FULL_UPPER,lower(direction,1),bottom(right))
        )
        for tag,direction in (("up",1),("down",2))
        for right in (1,3)
    ),
    *(
        (
            f"parent_bottom_{tag}1",
            word(FULL_UPPER,lower(),bottom(2,vertical))
        )
        for tag,vertical in (("up",1),("down",2))
    ),
    *(
        (
            f"clean_parent_receiver_{tag}1",
            word(UPPER_SELECTED,lower(direction,1),bottom())
        )
        for tag,direction in (("up",1),("down",2))
    ),
)
assert len(FROZEN)==22==len(set(name for name,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(program))<=32 and
    parse_plan(program)[-1][0]==5 and
    sum(action==5 for action,xy in parse_plan(program))==1 and
    all(xy is not None for action,xy in parse_plan(program) if action==6)
    for _,program in FROZEN
)

def observed_source(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3:
        raise AssertionError("Missing actual original SDK 64x64 animation")
    first_right={f"y{y}_xgte{x}":None for y,x in OBSERVE_RIGHT}
    first_cups=[None]*4
    first_four=None
    first_bottom=None
    max_cups=0
    for time,frame in enumerate(frames):
        if frame.shape!=pre.shape:
            raise AssertionError("Original source returned shape mismatch")
        new_blue=(pre!=6)&(frame==6)
        for y,x in OBSERVE_RIGHT:
            key=f"y{y}_xgte{x}"
            indices=np.flatnonzero(new_blue[y,x:])+x
            if first_right[key] is None and indices.size:
                first_right[key]={
                    "source_frame":time,
                    "original_native_new_blue_x":[int(v) for v in indices],
                }
        counts=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUP_RANGES
        ]
        for idx,value in enumerate(counts):
            if value==45 and first_cups[idx] is None:first_cups[idx]=time
        score=sum(value==45 for value in counts)
        max_cups=max(max_cups,score)
        if first_four is None and score==4:first_four=time
        diff=pre[59:63,2:62]!=frame[59:63,2:62]
        if diff.any() and first_bottom is None:
            first_bottom={
                "source_frame":time,
                "changed_original_native_test_region_pixel_count":int(diff.sum()),
                "observed_original_new_palette6_x_y58":[
                    int(v) for v in np.flatnonzero(new_blue[58])
                ],
            }
    comps=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and c["bbox"][1]<=52
    ]
    return {
        "authentic_original_prepour_blake2b16":hash_frame(pre),
        "authentic_original_postpour_blake2b16":hash_frame(frames[-1]),
        "original_sdk_returned_animation_frames":len(frames),
        "original_source_palette4_8_9_before_pour":comps,
        "first_native_new_palette6_on_right_observation_rows":first_right,
        "first_visual_per_cup_region_palette11_to13_frames":first_cups,
        "first_four_visual_cup_regions_same_frame":first_four,
        "max_simultaneous_visual_cup_regions":max_cups,
        "first_observed_tested_y59_62_boundary_change":first_bottom,
        "tested_source_bottom_region_unchanged":first_bottom is None,
        "limitation":"These are observed native pixel changes, NOT decoded leak semantics, engine physics or a success predicate.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    records=[];original_arrays={};roots=set()
    for name,program in FROZEN:
        n=len(parse_plan(program))
        for witness,entry in STAGE1_WITNESSES:
            sdk,source_arrays=real_trial(witness,entry,name,program)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            actual=source_arrays.get("stage3_"+str(n))
            pre=source_arrays.get("stage3_"+str(n-1),source_arrays["entry2_11"])[-1]
            metrics=observed_source(pre,actual) if actual is not None else None
            row={
                "frozen_source_plan":name,
                "original_independent_witness":witness,
                "actual_original_sdk_word":program,
                "official_native_level":sdk["official_original_final_level"],
                "official_native_state":sdk["official_original_final_state"],
                "official_original_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "true_original_sdk_disposition":sdk["trial_disposition"],
                "source_original_visual_records":metrics,
                "original_native_action_receipts":[
                    {k:v for k,v in event.items() if k!="full_original_source_frame_ledger"}
                    for event in sdk["full_original_sdk_action_events"]
                ],
            }
            records.append(row)
            for step,arr in source_arrays.items():
                original_arrays[f"{name}_{witness}_{step}"]=arr
            print("ORIGINAL_SP80_LOWER_CONTACT_CASE "+json.dumps({
                "case":name,"witness":witness,
                "sdk_level":row["official_native_level"],
                "sdk_state":row["official_native_state"],
                "source_observed":metrics,
            },sort_keys=True),flush=True)
    if len(records)!=44 or len(roots)!=1:
        raise AssertionError("Actual independent original SDK witnesses missing")
    official_success=[
        {"case":r["frozen_source_plan"],"witness":r["original_independent_witness"],
        "level":r["official_native_level"],"state":r["official_native_state"],
        "original_native_word":r["actual_original_sdk_word"]}
        for r in records if r["official_original_level4_or_WIN"]
    ]
    visual_four_no_tested_bottom=[
        {"case":r["frozen_source_plan"],"witness":r["original_independent_witness"]}
        for r in records if r["source_original_visual_records"] is not None
        and r["source_original_visual_records"]["max_simultaneous_visual_cup_regions"]==4
        and r["source_original_visual_records"]["tested_source_bottom_region_unchanged"]
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_LOWER_RECEIVER_VERTICAL_CONTACT",
        "source_antecedent_native_runs":[39556154686,39556575290],
        "genuine_independently_reset_original_sdk_games":len(records),
        "prospectively_frozen_original_sdk_words":FROZEN,
        "original_verified_stage3_root_blake2b16":next(iter(roots)),
        "actual_original_level4_or_WIN_count":len(official_success),
        "official_true_source_level_advances":official_success,
        "visual_only_four_cups_no_tested_bottom":visual_four_no_tested_bottom,
        "official_original_end_level_counts":dict(Counter(str(r["official_native_level"]) for r in records)),
        "official_original_end_state_counts":dict(Counter(str(r["official_native_state"]) for r in records)),
        "source_original_sdk_records":records,
        "boundary":"Only authentic SDK official levels>=4 or WIN prove progress. Palette6 and cup color and unchanged tested y59–62 pixels are partial source observations, never the game objective. Preserve original 64x64 SDK returns in NPZ. No changes to other lanes or original All Rights Reserved intent.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**original_arrays)
    print("ORIGINAL_SP80_LOWER_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_original_sdk_words","source_original_sdk_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
