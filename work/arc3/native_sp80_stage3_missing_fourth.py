"""Original SP80 stage3: restore missing rightmost source cup from clean trace.

Native original SDK #39556154686 observed selected upper bar down1,
middle held/down1, lower bar left10 and bottom right2: three full
source cup-color regions, NO source y59..62 bottom boundary changes,
missing cup region x50..58. Also first two disjoint new source palette6
x intervals at y19 not seen in those returned frames. These are only
source observations, NOT a win oracle or decoded game physics.

Direct intervention: preserve measured clean candidate, shift the OTHER
original upper source bar (click 40,18), test whether fourth source
branch becomes visible without observed boundary change. One genuine
SDK ACTION5 per fresh original Arcade.NORMAL game. Official level>=4 or
WIN alone means game progression.
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

SELECTED_DOWN1="6@20,18 4 4 2"
MID_HELD="6@10,30 4 4 4 4"
MID_DOWN1="6@10,30 4 4 4 4 2"
LOWER_LEFT10="6@46,33 "+" ".join(["3"]*10)
BOTTOM_RIGHT2="6@40,42 4 4"
CUPS=((8,16),(26,34),(38,46),(50,58))

OTHER=(
    ("left1","6@40,18 3"),
    ("left2","6@40,18 3 3"),
    ("right1","6@40,18 4"),
    ("up1","6@40,18 1"),
    ("down1","6@40,18 2"),
    ("down2","6@40,18 2 2"),
)
MIDDLE=(("mid_held",MID_HELD),("mid_down1",MID_DOWN1))

def plan(other,mid):
    return " ".join(x for x in (SELECTED_DOWN1,other,mid,LOWER_LEFT10,BOTTOM_RIGHT2,"5") if x)

FROZEN=tuple(
    (f"other_{other_name}_{mid_name}",plan(movement,mid))
    for other_name,movement in OTHER
    for mid_name,mid in MIDDLE
)+(
    ("clean_missing_cup_parent_held",plan("",MID_HELD)),
    ("clean_missing_cup_parent_down1",plan("",MID_DOWN1)),
)
assert len(FROZEN)==14==len(set(name for name,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,_ in parse_plan(word))==1
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    and len(parse_plan(word))<=32
    for _,word in FROZEN
)

def runs(x):
    if x.size==0:return []
    out=[];start=prev=int(x[0])
    for val in x[1:]:
        val=int(val)
        if val>prev+1:
            out.append([start,prev]);start=val
        prev=val
    out.append([start,prev])
    return out

def measure_native(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3:
        raise AssertionError("Original SDK 64x64 source frame not returned")
    first_boundary=None;first_four=None
    first_two_y19=None
    first_cups=[None]*4;max_full=0
    first_new_right_y19=None
    for t,frame in enumerate(frames):
        if frame.shape!=pre.shape:
            raise AssertionError("Source frame shape changed")
        y19=runs(np.flatnonzero((pre[19]!=6)&(frame[19]==6)))
        if len(y19)>=2 and first_two_y19 is None:
            first_two_y19={"frame":t,"original_source_disjoint_x_intervals":y19}
        if first_new_right_y19 is None:
            xs=[r for r in y19 if r[0]>=32]
            if xs:first_new_right_y19={"frame":t,"original_source_x_intervals":xs}
        counts=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (frame[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for i,v in enumerate(counts):
            if v==45 and first_cups[i] is None:first_cups[i]=t
        full=sum(v==45 for v in counts)
        max_full=max(max_full,full)
        if full==4 and first_four is None:first_four=t
        edge=(pre[59:63,2:62]!=frame[59:63,2:62])
        if first_boundary is None and edge.any():
            first_boundary={
                "frame":t,
                "native_pixel_change_count":int(edge.sum()),
                "new_original_palette6_x_at_y58":[int(i) for i in
                    np.flatnonzero((pre[58]!=6)&(frame[58]==6))],
            }
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and c["bbox"][1]<=53
    ]
    return {
        "native_pre_pour_frame_blake2b16":hash_frame(pre),
        "native_final_pour_frame_blake2b16":hash_frame(frames[-1]),
        "actual_original_sdk_frame_count":len(frames),
        "source_palette4_8_9_pre_pour_bboxes":components,
        "first_two_disjoint_source6_intervals_at_y19":first_two_y19,
        "first_right_hand_source6_interval_at_y19":first_new_right_y19,
        "first_each_of_four_source_cups_full_frames":first_cups,
        "first_simultaneous_four_source_cup_frame":first_four,
        "max_simultaneously_full_source_cup_regions":max_full,
        "first_observed_original_y59_62_bottom_pixel_change":first_boundary,
        "observed_test_bottom_region_unchanged":first_boundary is None,
        "boundary":"All observations are original SDK returned source pixels, not a causal leak rule, physics model or official game objective.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            original,stacks=real_trial(witness,entry,case,word)
            roots.add(original["original_verified_stage3_root"]["original_source_sha256"])
            frames=stacks.get("stage3_"+str(n))
            pre=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            metrics=measure_native(pre,frames) if frames is not None else None
            row={
                "frozen_original_sdk_case":case,
                "independent_real_native_witness":witness,
                "true_original_action_word":word,
                "original_sdk_official_level":original["official_original_final_level"],
                "original_sdk_official_state":original["official_original_final_state"],
                "original_sdk_level4_or_WIN":original["official_original_level4_or_WIN"],
                "true_original_sdk_disposition":original["trial_disposition"],
                "native_source_original_measurements":metrics,
                "actual_sdk_native_action_receipts":[
                    {k:v for k,v in event.items() if k!="full_original_source_frame_ledger"}
                    for event in original["full_original_sdk_action_events"]],
            }
            rows.append(row)
            for step,arr in stacks.items():
                arrays[f"{case}_{witness}_{step}"]=arr
            print("ORIGINAL_SP80_MISSING_FOURTH_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":row["original_sdk_official_level"],
                "official_state":row["original_sdk_official_state"],
                "observed_source":metrics,
            },sort_keys=True),flush=True)
    if len(rows)!=28 or len(roots)!=1:
        raise AssertionError("Genuine independent original SDK source witnesses missing")
    gains=[{
        "case":r["frozen_original_sdk_case"],
        "witness":r["independent_real_native_witness"],
        "official_level":r["original_sdk_official_level"],
        "official_state":r["original_sdk_official_state"],
        "original_word":r["true_original_action_word"]}
        for r in rows if r["original_sdk_level4_or_WIN"]
    ]
    four_without_boundary=[
        {"case":r["frozen_original_sdk_case"],"witness":r["independent_real_native_witness"]}
        for r in rows if r["native_source_original_measurements"] is not None
        and r["native_source_original_measurements"]["max_simultaneously_full_source_cup_regions"]==4
        and r["native_source_original_measurements"]["observed_test_bottom_region_unchanged"]
    ]
    result={
        "kind":"TRUE_ORIGINAL_SP80_STAGE3_MISSING_FOURTH_CUP_UPPER_BRANCH",
        "source_native_antecedent_run":39556154686,
        "independently_reset_original_sdk_games":len(rows),
        "frozen_original_sdk_words":FROZEN,
        "verified_stage3_source_root_blake2b16":next(iter(roots)),
        "official_sdk_level4_or_WIN_count":len(gains),
        "actual_native_sdk_progress_cases":gains,
        "source_four_cup_no_tested_bottom_change":four_without_boundary,
        "official_original_sdk_level_histogram":dict(Counter(str(r["original_sdk_official_level"]) for r in rows)),
        "official_original_sdk_state_histogram":dict(Counter(str(r["original_sdk_official_state"]) for r in rows)),
        "original_native_sdk_records":rows,
        "limitations":"Only real SDK official level>=4 or WIN is level completion. Colors, intervals and absence of change on a fixed y59-62 region are partial observable proxies, not original game rules. Original SDK full frame stacks in NPZ; no replacement engine, private inference, or changes to other lanes and rights.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_MISSING_FOURTH_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("frozen_original_sdk_words","original_native_sdk_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
