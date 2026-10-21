"""Original SP80 SDK: independently move middle-center bar before spout-bar overlap.

The genuine stage3 entry source map shows separate red 3-cell bars at
x8..16 and x20..28 around a palette4 movable-spout marker x17..19.
The most-used verified near-miss moves the LEFT marked bar right4
onto the middle-center bar, causing visual overlap. Previous broad
placement trials did NOT isolate prior native movement of the other
middle-center object.

This predeclared finite intervention clicks ORIGINAL middle-center
source coordinate x22,y30 while the objects are still separated,
moves only that selected original bar, THEN selects the spout-bearing
left bar x10,y30 and places it by four original right movements.
The actual original SDK pixel clicked/selection/levels/action ledger
and ALL frames are the evidence; not assumptions about identity,
which piece stays selected or a hidden fluid model.

Only genuine SDK levels_completed>=4 or WIN is progress.
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

UPPERS="6@20,18 4 4 2 6@40,18 2"
SPOUTBAR="6@10,30 4 4 4 4"
RECEIVER="6@46,33 1 "+" ".join(["3"]*10)
BOTTOM="6@40,42 4"
CUPS=((8,16),(26,34),(38,46),(50,58))

def center(direction,count):
    return "6@22,30 "+" ".join([str(direction)]*count)

def word(moved="",extra=""):
    return " ".join(v for v in (UPPERS,moved,SPOUTBAR,RECEIVER,BOTTOM,extra,"5") if v)

FROZEN=(
    ("overlap_without_center_move",word()),
    ("center_click_only",word("6@22,30")),
    ("center_right1_before_overlap",word(center(4,1))),
    ("center_right2_before_overlap",word(center(4,2))),
    ("center_right3_before_overlap",word(center(4,3))),
    ("center_left1_before_overlap",word(center(3,1))),
    ("center_left2_before_overlap",word(center(3,2))),
    ("center_left3_before_overlap",word(center(3,3))),
    ("center_up1_before_overlap",word(center(1,1))),
    ("center_up2_before_overlap",word(center(1,2))),
    ("center_down1_before_overlap",word(center(2,1))),
    ("center_down2_before_overlap",word(center(2,2))),
    # Post-overlap click is a deliberate independent control. The actual
    # selected object/pixel is not presumed from the coordinate.
    ("center_click_after_overlap",word(extra="6@22,30")),
)
assert len(FROZEN)==13==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(s))<=36 and
    parse_plan(s)[-1][0]==5 and
    sum(a==5 for a,xy in parse_plan(s))==1 and
    all(xy is not None for a,xy in parse_plan(s) if a==6)
    for _,s in FROZEN
)

def screenshot_metrics(pre,animation):
    if pre.shape!=(64,64) or animation.ndim!=3 or animation.shape[1:]!=(64,64):
        raise AssertionError("Actual original 64x64 frame stack required")
    four_at=None
    first_bottom=None
    ever_cups=[None]*4
    max_four=0
    for t,screen in enumerate(animation):
        colored=[
            int(np.count_nonzero(
                (pre[53:59,l:r+1]==11)&(screen[53:59,l:r+1]==13)
            )) for l,r in CUPS
        ]
        for i,v in enumerate(colored):
            if v==45 and ever_cups[i] is None:ever_cups[i]=t
        m=sum(v==45 for v in colored)
        max_four=max(max_four,m)
        if m==4 and four_at is None:four_at=t
        edge=(pre[59:63,2:62]!=screen[59:63,2:62])
        if edge.any() and first_bottom is None:
            first_bottom={
                "genuine_animation_frame":t,
                "actual_changed_source_bottom_test_pixels":int(edge.sum()),
                "native_new_palette6_y58_x":[int(i) for i in np.flatnonzero(
                    (pre[58]!=6)&(screen[58]==6)
                )],
            }
    geometry=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9)
        and 15<=c["bbox"][1]<=53
    ]
    return {
        "original_native_prepour_blake2b16":hash_frame(pre),
        "original_native_after_pour_blake2b16":hash_frame(animation[-1]),
        "native_source_animation_count":len(animation),
        "source_middle_and_upper_pre_pour_components":geometry,
        "first_true_four_visual_source_cups_same_frame":four_at,
        "first_original_bottom_test_region_transition":first_bottom,
        "observed_source_cup_first_full_frames":ever_cups,
        "max_simultaneous_observed_source_cup_regions":max_four,
        "not_a_win_or_physical_oracle":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];stacks_out={};roots=set()
    for name,program in FROZEN:
        parts=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            original,stacks=real_trial(witness,entry,name,program)
            roots.add(original["original_verified_stage3_root"]["original_source_sha256"])
            pour=stacks.get("stage3_"+str(len(parts)))
            prior=stacks.get("stage3_"+str(len(parts)-1),stacks["entry2_11"])[-1]
            metrics=screenshot_metrics(prior,pour) if pour is not None else None
            # Actual native click and per-step before/after source hashes
            # expose whether x22,y30 selected another object vs overlap.
            original_steps=[
                {k:v for k,v in ev.items() if k!="full_original_source_frame_ledger"}
                for ev in original["original_stage3_intervention_events"]
            ]
            source_center_clicks=[
                {
                    "index":ev["index"],
                    "original_pixel_at_click":ev.get("actual_source_preclick_palette"),
                    "actual_before_sha":ev.get("actual_source_before_sha"),
                    "actual_after_sha":ev.get("actual_source_after_sha"),
                    "original_sdk_level_after":ev.get("official_source_level_after"),
                }
                for ev in original_steps
                if ev.get("original_action")==6
                and ev.get("original_click_xy")==[22,30]
            ]
            row={
                "precommitted_original_source_case":name,
                "authentic_independent_source_witness":witness,
                "original_sdk_word":program,
                "true_sdk_official_final_level":original["official_original_final_level"],
                "true_sdk_official_final_state":original["official_original_final_state"],
                "original_sdk_level4_or_WIN":original["official_original_level4_or_WIN"],
                "real_sdk_trial_disposition":original["trial_disposition"],
                "actual_center_click_source_receipts":source_center_clicks,
                "actual_original_source_animation_metrics":metrics,
                "original_native_step_ledger":original_steps,
            }
            rows.append(row)
            for phase,stack in stacks.items():
                stacks_out[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_INDEPENDENT_CENTER_CASE "+json.dumps({
                "case":name,"witness":witness,
                "official_level":row["true_sdk_official_final_level"],
                "official_state":row["true_sdk_official_final_state"],
                "center_click_receipts":source_center_clicks,
                "native_visual":metrics,
            },sort_keys=True),flush=True)
    if len(rows)!=26 or len(roots)!=1:
        raise AssertionError("Missing independent original source SDK entries")
    wins=[
        {"case":r["precommitted_original_source_case"],
         "witness":r["authentic_independent_source_witness"],
         "word":r["original_sdk_word"],
         "official_level":r["true_sdk_official_final_level"],
         "official_state":r["true_sdk_official_final_state"]}
        for r in rows if r["original_sdk_level4_or_WIN"]
    ]
    four_wo_bottom=[
        {"case":r["precommitted_original_source_case"],"witness":r["authentic_independent_source_witness"]}
        for r in rows if r["actual_original_source_animation_metrics"] is not None
        and r["actual_original_source_animation_metrics"]["first_true_four_visual_source_cups_same_frame"] is not None
        and r["actual_original_source_animation_metrics"]["first_original_bottom_test_region_transition"] is None
    ]
    summary={
        "kind":"ORIGINAL_SP80_STAGE3_SEPARATE_CENTER_PIECE_BEFORE_OVERLAP",
        "authentic_source_antecedents":[39557242249,39557791993,39559137233],
        "native_original_sdk_game_resets":len(rows),
        "prospectively_frozen_original_sdk_words":FROZEN,
        "genuine_original_source_root_blake2b16":next(iter(roots)),
        "official_original_sdk_level4_or_WIN_count":len(wins),
        "native_source_successes":wins,
        "observed_four_cups_no_tested_bottom_change":four_wo_bottom,
        "true_source_level_histogram":dict(Counter(str(r["true_sdk_official_final_level"]) for r in rows)),
        "true_source_state_histogram":dict(Counter(str(r["true_sdk_official_final_state"]) for r in rows)),
        "actual_original_sdk_receipts":rows,
        "limit":"Click identity must be grounded in SDK observed pre-click pixel/animation, not presumed. Only original SDK level>=4 or WIN proves progress. Pixel colors are bounded source observations. Preserve complete native arrays in NPZ, all research lanes and rights unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks_out)
    print("ORIGINAL_SP80_INDEPENDENT_CENTER_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_original_sdk_words","actual_original_sdk_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
