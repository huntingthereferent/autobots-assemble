"""Authentic original SDK SP80 level4: find source route to missing LEFT cup.

PR #365 proved genuine native stage3 -> level4 on both A/B witnesses.
PR #367 froze the original SDK entrance, actual level4 screen, and
initial bounded probes. In run #39624132483, the original left/middle
cups along the TOP of level4 visibly fill, while the left-side cup and
top-right cup remain visually empty in the untouched first ACTION5.
Selecting the right middle source bar at x46,y33 and moving LEFT one
true native ACTION3 fills the TOP-RIGHT cup too. The left-side cup
x5..10/y35..43 is still missing. Official SDK remains level4.

This finite native study fixes that actual three-cup level4 state,
varies one upstream original source piece at a time, and records
whether true source palette11->13 coverage appears in the missing
left-side cup. Do not infer hidden mechanics from visual pathways:
only original SDK levels_completed>=5 or WIN is advancement.
"""
from __future__ import annotations

import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

# Source native stage4 source initial position witnesses:
# x46,33 selected right 45px middle bar; ACTION3 moves it left once.
# x24,33 separate left 27px middle bar; x34,21 top 36px bar.
RIGHT_LEFT1="6@46,33 3"
LEFT_TARGET="6@24,33 "
TOP_TARGET="6@34,21 "

def program(left="",upper="",right=RIGHT_LEFT1):
    return " ".join(p for p in (right,left,upper,"5") if p)

def moves(target,action,count):
    return target+" ".join([str(action)]*count)

FROZEN=(
    ("verified_right_middle_left1_three_cup",program()),
    ("right_middle_left2",program(right="6@46,33 3 3")),
    ("right_middle_left3",program(right="6@46,33 3 3 3")),
    ("left_middle_left1",program(left=moves(LEFT_TARGET,3,1))),
    ("left_middle_left2",program(left=moves(LEFT_TARGET,3,2))),
    ("left_middle_left3",program(left=moves(LEFT_TARGET,3,3))),
    ("left_middle_left4",program(left=moves(LEFT_TARGET,3,4))),
    ("left_middle_right1",program(left=moves(LEFT_TARGET,4,1))),
    ("left_middle_right2",program(left=moves(LEFT_TARGET,4,2))),
    ("left_middle_up1",program(left=moves(LEFT_TARGET,1,1))),
    ("left_middle_down1",program(left=moves(LEFT_TARGET,2,1))),
    ("left_middle_down2",program(left=moves(LEFT_TARGET,2,2))),
    ("top_bar_left1",program(upper=moves(TOP_TARGET,3,1))),
    ("top_bar_left2",program(upper=moves(TOP_TARGET,3,2))),
    ("top_bar_left3",program(upper=moves(TOP_TARGET,3,3))),
    ("top_bar_right1",program(upper=moves(TOP_TARGET,4,1))),
    ("top_bar_up1",program(upper=moves(TOP_TARGET,1,1))),
    ("top_bar_down1",program(upper=moves(TOP_TARGET,2,1))),
    ("top_bar_down2",program(upper=moves(TOP_TARGET,2,2))),
    ("left_middle_left2_top_left1",program(
        left=moves(LEFT_TARGET,3,2),upper=moves(TOP_TARGET,3,1))),
    ("left_middle_left3_top_left2",program(
        left=moves(LEFT_TARGET,3,3),upper=moves(TOP_TARGET,3,2))),
    ("left_middle_down1_top_left1",program(
        left=moves(LEFT_TARGET,2,1),upper=moves(TOP_TARGET,3,1))),
    ("right_left2_and_left_middle_left2",program(
        right="6@46,33 3 3",left=moves(LEFT_TARGET,3,2))),
    ("right_left2_and_top_left1",program(
        right="6@46,33 3 3",upper=moves(TOP_TARGET,3,1))),
)
assert len(FROZEN)==24==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    and len(parse_plan(word))<=13
    for _,word in FROZEN
)

def intervals(xs):
    xs=list(map(int,xs))
    if not xs:return []
    out=[];lo=hi=xs[0]
    for x in xs[1:]:
        if x>hi+1:
            out.append([lo,hi]);lo=x
        hi=x
    out.append([lo,hi])
    return out

def native_visual(readonly_root,pre,animation):
    if readonly_root.shape!=(64,64) or pre.shape!=(64,64) or animation.ndim!=3 or animation.shape[1:]!=(64,64):
        raise AssertionError("Require actual original 64x64 returned SDK source frames")
    cups=[c for c in color_components(readonly_root) if c["palette"]==11]
    if len(cups)!=4 or any(c["pixels"]!=45 for c in cups):
        raise AssertionError("Original level4 cup inventory changed")
    cups=sorted(cups,key=lambda c:(c["bbox"][1],c["bbox"][0]))
    names=["top_left","top_middle","top_right","left_lateral"]
    assert [tuple(c["bbox"]) for c in cups]==[
        (17,5,25,10),(35,5,43,10),(47,5,55,10),(5,35,10,43)
    ]
    seen={n:None for n in names}
    max_per={n:0 for n in names}
    maximum=0
    native_new_source_at_left={str(y):None for y in (17,20,23,29,32,35,38,41,44,47,50,53,56)}
    native_new_source_at_upper={str(y):None for y in (5,8,11,17,20)}
    for i,frame in enumerate(animation):
        new=(pre!=6)&(frame==6)
        for y in (17,20,23,29,32,35,38,41,44,47,50,53,56):
            xs=np.flatnonzero(new[y,5:17])+5
            if xs.size and native_new_source_at_left[str(y)] is None:
                native_new_source_at_left[str(y)]={"sdk_frame":i,"real_new_source_color6_x":intervals(xs)}
        for y in (5,8,11,17,20):
            xs=np.flatnonzero(new[y,12:60])+12
            if xs.size and native_new_source_at_upper[str(y)] is None:
                native_new_source_at_upper[str(y)]={"sdk_frame":i,"real_new_source_color6_x":intervals(xs)}
        filled=0
        for name,c in zip(names,cups):
            x0,y0,x1,y1=c["bbox"]
            n=int(np.count_nonzero(
                (readonly_root[y0:y1+1,x0:x1+1]==11)
                &(frame[y0:y1+1,x0:x1+1]==13)
            ))
            max_per[name]=max(max_per[name],n)
            if n==c["pixels"] and seen[name] is None:seen[name]=i
            filled+=int(n==c["pixels"])
        maximum=max(maximum,filled)
    return {
        "authentic_original_sdk_prepour_blake2b16":hash_frame(pre),
        "authentic_original_sdk_final_frame_blake2b16":hash_frame(animation[-1]),
        "actual_original_sdk_pour_frame_count":len(animation),
        "true_sdk_cup_source_bboxes":{name:c["bbox"] for name,c in zip(names,cups)},
        "native_first_full_visual_cup_frame":seen,
        "native_max_source_palette11to13_pixels_per_cup":max_per,
        "native_max_simultaneous_full_cup_region_count":maximum,
        "first_new_native_palette6_near_left_side_by_row":native_new_source_at_left,
        "first_new_native_palette6_near_upper_cups_by_row":native_new_source_at_upper,
        "actual_source_prepour_selected_components":[
            {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
            for c in color_components(pre)
            if c["palette"] in (4,8,9,15) and 15<=c["bbox"][1]<=51
        ],
        "observation_only":"Original SDK source pixel regions are not private game objectives/physics. Only official level>=5 or WIN qualifies.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];raw={};roots=set()
    for case,word in FROZEN:
        parts=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            trial,stacks=run_case(case,witness,entry,word)
            root=stacks["entry3_34"][-1]
            roots.add(trial["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            poured=stacks.get("stage4_"+str(len(parts)))
            prior=stacks.get("stage4_"+str(len(parts)-1),stacks["entry3_34"])[-1]
            observed=native_visual(root,prior,poured) if poured is not None else None
            r={
                "prospective_original_source_case":case,
                "genuine_independent_source_witness":witness,
                "real_original_stage4_word":word,
                "original_sdk_official_final_level":trial["true_original_sdk_final_level"],
                "original_sdk_official_final_state":trial["true_original_sdk_final_state"],
                "actual_original_level5_or_WIN":trial["official_original_level5_or_WIN"],
                "actual_original_stage4_source_observations":observed,
                "original_source_level4_actions":trial["genuine_original_stage4_action_ledger"],
            }
            records.append(r)
            for phase,stack in stacks.items():raw[f"{case}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_STAGE4_LEFT_CUP_CASE "+json.dumps({
                "case":case,"witness":witness,
                "sdk_final_level":r["original_sdk_official_final_level"],
                "sdk_final_state":r["original_sdk_official_final_state"],
                "source":observed
            },sort_keys=True),flush=True)
    if len(records)!=48 or len(roots)!=1:
        raise AssertionError("Missing genuine independent original SDK level4 source reset")
    for case,_ in FROZEN:
        pair=[r for r in records if r["prospective_original_source_case"]==case]
        if len(pair)!=2 or pair[0]["original_sdk_official_final_level"]!=pair[1]["original_sdk_official_final_level"] or pair[0]["original_sdk_official_final_state"]!=pair[1]["original_sdk_official_final_state"] or pair[0]["actual_original_stage4_source_observations"]!=pair[1]["actual_original_stage4_source_observations"]:
            raise AssertionError("Original SDK A/B source discrepancy "+case)
    successes=[{
        "case":r["prospective_original_source_case"],
        "witness":r["genuine_independent_source_witness"],
        "source_native_stage4_word":r["real_original_stage4_word"],
        "level":r["original_sdk_official_final_level"],
        "state":r["original_sdk_official_final_state"]}
        for r in records if r["actual_original_level5_or_WIN"]]
    visual_four=[
        {"case":r["prospective_original_source_case"],"witness":r["genuine_independent_source_witness"]}
        for r in records if r["actual_original_stage4_source_observations"] is not None
        and r["actual_original_stage4_source_observations"]["native_max_simultaneous_full_cup_region_count"]==4]
    result={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_LEFT_LATERAL_CUP_SOURCE_INVESTIGATION",
        "authentic_original_sdk_stage4_inventory_run":39624132483,
        "genuine_original_independent_stage4_reset_games":len(records),
        "original_source_fixed_three_cup_middle_right_left1":RIGHT_LEFT1,
        "prospectively_frozen_stage4_native_words":FROZEN,
        "original_verified_level4_root_blake2b16":next(iter(roots)),
        "official_source_level5_or_WIN_count":len(successes),
        "actual_native_original_level5_advances":successes,
        "source_four_cup_visual_cases":visual_four,
        "original_sdk_true_level_histogram":dict(Counter(str(r["original_sdk_official_final_level"]) for r in records)),
        "original_sdk_true_state_histogram":dict(Counter(str(r["original_sdk_official_final_state"]) for r in records)),
        "full_original_sdk_stage4_receipts":records,
        "limits":"Screen color6 and cup11to13 changes measure actual original SDK frames, not decoded source objective or inferred physics. Only official SDK level>=5/WIN advances. Preserve raw native arrays in NPZ, other lanes/rights untouched.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_STAGE4_LEFT_CUP_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("prospectively_frozen_stage4_native_words","full_original_sdk_stage4_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
