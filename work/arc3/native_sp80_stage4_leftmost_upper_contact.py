"""Original Arcade.NORMAL SP80 level4: test x11..13 top-left overshoot contact.

Independently returned original 64x64 SDK frame stacks in native runs
#39636174534 and #39636999616 show source palette6 first reaching
x11..13/y5 at animation frame20 across two clean all-four-cup native
parents, while the entire top border flashes source palette1->14
at frame21. Right-middle LEFT2 removes the x56..58/y5 source strand,
but NOT this leftmost upper strand or the top border event.

This source test targets a genuinely untested placement: the distinct
real upper selectable 36px bar at original bbox x29..40/y20..22 has
only been moved LEFT1..3 in these clean parent arrangements. With the
two independently observed four-cup source constructions fixed, move
the bar LEFT4..8 and selected nearby UP/DOWN choices, measuring exact
native selected geometry, x11..13/y5 first arrivals, full cup11->13
transitions, and ALL source border flashes. Do not infer hidden game
physics or claim image-only level progress.
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

RIGHT="6@46,33 3"
TOP_CLICK="6@34,21"
PARENTS=(
    ("D3L2_L3U2","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1"),
    ("D4L2_L4U2","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1"),
)
TOP_MOVES=(
    ("left3","3 3 3"),
    ("left4","3 3 3 3"),
    ("left5","3 3 3 3 3"),
    ("left6","3 3 3 3 3 3"),
    ("left7","3 3 3 3 3 3 3"),
    ("left8","3 3 3 3 3 3 3 3"),
    ("left4_up1","3 3 3 3 1"),
    ("left5_up1","3 3 3 3 3 1"),
    ("left5_down1","3 3 3 3 3 2"),
    ("left6_up1","3 3 3 3 3 3 1"),
    ("left6_down1","3 3 3 3 3 3 2"),
    ("up1_before_left6","1 3 3 3 3 3 3"),
)
FROZEN=tuple(
    (f"{parent}_top_{name}"," ".join((RIGHT,mid,L,TOP_CLICK+" "+moves,"5")))
    for parent,mid,L in PARENTS for name,moves in TOP_MOVES
)
assert len(FROZEN)==24==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=28
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word in FROZEN
)
CUPS={
    "left_lateral":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
BORDERS={
    "left":(slice(2,62),slice(2,5)),
    "right":(slice(2,62),slice(59,62)),
    "top":(slice(2,5),slice(2,62)),
    "bottom":(slice(59,62),slice(2,62)),
}
UPPER_SITES={
    "leftmost_outside_cup":(slice(5,8),slice(11,14)),
    "top_left_cup_other_side":(slice(5,8),slice(26,29)),
    "upper_right_outside":(slice(5,8),slice(56,59)),
}

def selected(frame):
    return [
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"]==9 and 12<=c["bbox"][1]<=56
    ]

def measured_actual_native(root,pre,animation):
    if (root.shape!=(64,64) or pre.shape!=(64,64)
        or animation.ndim!=3 or animation.shape[1:]!=(64,64)):
        raise AssertionError("Genuine original SDK 64x64 native frames required")
    first_full={k:None for k in CUPS}
    max_pixels={k:0 for k in CUPS}
    first_four=None
    first_border={k:None for k in BORDERS}
    border_episodes={k:[] for k in BORDERS}
    border_active={k:False for k in BORDERS}
    first_upper_site={k:None for k in UPPER_SITES}
    for t,frame in enumerate(animation):
        extra6=(pre!=6)&(frame==6)
        for name,(ys,xs) in UPPER_SITES.items():
            if first_upper_site[name] is None and extra6[ys,xs].any():
                yy,xx=np.nonzero(extra6[ys,xs])
                first_upper_site[name]={
                    "native_original_frame":t,
                    "real_native_yx":[[int(y+ys.start),int(x+xs.start)] for y,x in zip(yy,xx)]
                }
        count_full=0
        for name,(x0,y0,x1,y1) in CUPS.items():
            original=root[y0:y1+1,x0:x1+1]==11
            if int(original.sum())!=45:
                raise AssertionError("Original native SDK level4 cup root changed")
            n=int(np.count_nonzero(original & (frame[y0:y1+1,x0:x1+1]==13)))
            max_pixels[name]=max(max_pixels[name],n)
            if n==45 and first_full[name] is None:first_full[name]=t
            count_full+=int(n==45)
        if count_full==4 and first_four is None:first_four=t
        for name,(ys,xs) in BORDERS.items():
            change=pre[ys,xs]!=frame[ys,xs]
            active=bool(change.any())
            if active and not border_active[name]:border_episodes[name].append(t)
            border_active[name]=active
            if active and first_border[name] is None:
                old=pre[ys,xs][change]
                new=frame[ys,xs][change]
                transitions,counts=np.unique(np.stack((old,new),axis=1),axis=0,return_counts=True)
                first_border[name]={
                    "native_original_frame":t,
                    "changed_original_source_pixels":int(change.sum()),
                    "native_palette_transitions":[[int(v[0]),int(v[1]),int(c)] for v,c in zip(transitions,counts)]
                }
    return {
        "original_native_prepour_blake2b16":hash_frame(pre),
        "original_native_after_pour_blake2b16":hash_frame(animation[-1]),
        "source_sdk_returned_animation_frame_count":len(animation),
        "original_source_cup_first_full_frames":first_full,
        "original_source_cup_max_palette13_pixels":max_pixels,
        "native_first_simultaneously_full_four_cups":first_four,
        "native_first_source_border_changes":first_border,
        "native_source_border_change_episodes":border_episodes,
        "first_original_color6_at_3_upper_sites":first_upper_site,
        "original_native_prepour_selected_objects":selected(pre),
        "scope":"Actual SDK returned pixel observations are not decoded engine physics or official advancement.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];source_arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            result,source=run_case(case,witness,entry,word)
            roots.add(result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=source["entry3_34"][-1]
            pre=source["stage4_"+str(n-1)][-1]
            animation=source["stage4_"+str(n)]
            observed=measured_actual_native(root,pre,animation)
            actions=[
                {
                    "original_sdk_step":ev["index"],
                    "actual_native_action":ev["genuine_original_action"],
                    "actual_native_click_xy":ev["real_native_click_xy"],
                    "original_native_click_palette":ev["original_source_pixel_before_click"],
                    "source_selected_after":selected(source["stage4_"+str(ev["index"])][-1]),
                    "source_frame_after":ev["source_frame_after_blake2b16"],
                }
                for ev in result["genuine_original_stage4_action_ledger"]
                if ev["genuine_original_action"] in (1,2,3,4,6)
            ]
            if not any(
                x["actual_native_click_xy"]==[34,21] and x["original_native_click_palette"]==8
                for x in actions
            ):
                raise AssertionError("Native original TOP bar selection did not occur")
            record={
                "prospectively_frozen_source_case":case,
                "true_independent_native_witness":witness,
                "actual_original_stage4_source_word":word,
                "original_official_final_level":result["true_original_sdk_final_level"],
                "original_official_final_state":result["true_original_sdk_final_state"],
                "actual_sdk_level5_or_WIN":result["official_original_level5_or_WIN"],
                "source_pixel_observations":observed,
                "true_original_selected_movement_receipts":actions,
                "all_genuine_sdk_action_receipts":result["genuine_original_stage4_action_ledger"],
            }
            records.append(record)
            for k,arr in source.items():
                source_arrays[f"{case}_{witness}_{k}"]=arr
            print("ORIGINAL_SP80_UPPER_LEFTMOST_CONTACT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":record["original_official_final_level"],
                "official_state":record["original_official_final_state"],
                "source":observed,
            },sort_keys=True),flush=True)
    if len(records)!=48 or len(roots)!=1:
        raise AssertionError("Missing independent original source SDK level4 witnesses")
    for case,_ in FROZEN:
        pair=[r for r in records if r["prospectively_frozen_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["original_official_final_level"]!=pair[1]["original_official_final_level"]
            or pair[0]["original_official_final_state"]!=pair[1]["original_official_final_state"]
            or pair[0]["source_pixel_observations"]!=pair[1]["source_pixel_observations"]
            or pair[0]["true_original_selected_movement_receipts"]!=pair[1]["true_original_selected_movement_receipts"]
        ):raise AssertionError("Original SDK independent witness discrepancy "+case)
    gains=[
        {"case":r["prospectively_frozen_source_case"],
         "witness":r["true_independent_native_witness"],
         "native_original_word":r["actual_original_stage4_source_word"],
         "official_level":r["original_official_final_level"],
         "official_state":r["original_official_final_state"]}
        for r in records if r["actual_sdk_level5_or_WIN"]
    ]
    clean_four=[
        {"case":r["prospectively_frozen_source_case"],
         "witness":r["true_independent_native_witness"],
         "first_borders":r["source_pixel_observations"]["native_first_source_border_changes"],
         "first_upper_sites":r["source_pixel_observations"]["first_original_color6_at_3_upper_sites"]}
        for r in records
        if r["source_pixel_observations"]["native_first_simultaneously_full_four_cups"] is not None
    ]
    out={
        "kind":"ORIGINAL_SP80_LEVEL4_LEFTMOST_UPPER_STREAM_NEAR_TOP_BAR",
        "genuine_original_antecedent_runs":[39636174534,39636999616],
        "actual_independent_original_sdk_resets":len(records),
        "prospectively_frozen_original_words":FROZEN,
        "same_original_native_level4_root_blake2b16":next(iter(roots)),
        "real_original_sdk_level5_or_WIN_count":len(gains),
        "native_official_level5_cases":gains,
        "visual_four_cups_with_source_upper_site_and_borders":clean_four,
        "official_original_sdk_level_histogram":dict(Counter(str(r["original_official_final_level"]) for r in records)),
        "official_original_sdk_state_histogram":dict(Counter(str(r["original_official_final_state"]) for r in records)),
        "authentic_native_original_source_receipts":records,
        "limits":"Official original SDK level>=5/WIN alone establishes progress. Source streams, cup pixels and border flashes are observational and cannot independently prove flow physics or SDK win. Original native frames retained in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_arrays)
    print("ORIGINAL_SP80_UPPER_LEFTMOST_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in out.items()
        if k not in ("prospectively_frozen_original_words","authentic_native_original_source_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
