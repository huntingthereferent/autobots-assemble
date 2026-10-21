"""Authentic original SDK level4: does changing height bypass left-bar movement limit?

Original source-native run #39625230030 proved that the separate
stage4 left-middle red 27px bar at initial x20..28,y32..34 moves left
to x17..25 after ACTION3, x14..22 after a second ACTION3, and remains
x14..22 after 3rd and 4th left commands in the tested initial height.
Original source new palette6 reaches x11..13 at y32 but does not
touch the missing left-side cup bbox x5..10,y35..43. Earlier stage4
probes restored the OTHER THREE visually full cups by moving the
right-middle bar LEFT1, all official level4 NOT_FINISHED.

This frozen finite trial changes the vertical position of the separate
left-middle 27px bar BEFORE/AFTER the two effective left movements to
see whether additional original left movement becomes observable. All
native actions are actual Arcade(OperationMode.NORMAL) source steps,
no inferred collision law or toy fluid model. Only original official
levels_completed>=5 or WIN advances.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_left_cup_trial import native_visual
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

RIGHT="6@46,33 3"
LEFT="6@24,33 "
def candidate(middle_move,upper_move="",right=RIGHT):
    return " ".join(v for v in (right,LEFT+middle_move,upper_move,"5") if v)

FROZEN=(
    ("left2_parent",candidate("3 3")),
    ("left3_parent_limit",candidate("3 3 3")),
    ("left4_parent_limit",candidate("3 3 3 3")),
    ("up1_then_left3",candidate("1 3 3 3")),
    ("up1_then_left4",candidate("1 3 3 3 3")),
    ("up2_then_left3",candidate("1 1 3 3 3")),
    ("down1_then_left3",candidate("2 3 3 3")),
    ("down1_then_left4",candidate("2 3 3 3 3")),
    ("down2_then_left3",candidate("2 2 3 3 3")),
    ("left2_up1_left2",candidate("3 3 1 3 3")),
    ("left2_up2_left2",candidate("3 3 1 1 3 3")),
    ("left2_down1_left2",candidate("3 3 2 3 3")),
    ("left2_down2_left2",candidate("3 3 2 2 3 3")),
    ("left2_up1_left1",candidate("3 3 1 3")),
    ("left2_down1_left1",candidate("3 3 2 3")),
    ("left1_up1_left3",candidate("3 1 3 3 3")),
    ("left1_down1_left3",candidate("3 2 3 3 3")),
    ("left2_right1_left3",candidate("3 3 4 3 3 3")),
    ("left2_up1_right1_left2",candidate("3 3 1 4 3 3")),
    ("left2_up1_left2_top_left1",candidate("3 3 1 3 3",upper_move="6@34,21 3")),
    ("left2_down1_left2_top_left1",candidate("3 3 2 3 3",upper_move="6@34,21 3")),
    ("right_left2_and_left2_up1_left2",candidate("3 3 1 3 3",right="6@46,33 3 3")),
)
assert len(FROZEN)==22==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           and len(parse_plan(w))<=15 for n,w in FROZEN)

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    receipts=[];raw={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,frames=run_case(case,witness,entry,word)
            root=frames["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pour=frames.get("stage4_"+str(n))
            pre=frames.get("stage4_"+str(n-1),frames["entry3_34"])[-1]
            vis=native_visual(root,pre,pour) if pour is not None else None
            native_movement=[
                {"index":a["index"],"action":a["genuine_original_action"],
                 "actual_source_preclick_pixel":a["original_source_pixel_before_click"],
                 "source_after_blake2b16":a["source_frame_after_blake2b16"]}
                for a in sdk["genuine_original_stage4_action_ledger"]
                if a["genuine_original_action"] in (1,2,3,4,6)
            ]
            row={
                "precommitted_original_source_case":case,
                "native_original_independent_witness":witness,
                "authentic_stage4_sdk_word":word,
                "official_original_final_level":sdk["true_original_sdk_final_level"],
                "official_original_final_state":sdk["true_original_sdk_final_state"],
                "actual_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "source_original_visual_metrics":vis,
                "original_native_source_movement_receipts":native_movement,
                "complete_original_stage4_actions":sdk["genuine_original_stage4_action_ledger"],
            }
            receipts.append(row)
            for key,stack in frames.items():raw[f"{case}_{witness}_{key}"]=stack
            print("ORIGINAL_SP80_STAGE4_VERTICAL_BYPASS_CASE "+json.dumps({
                "case":case,"witness":witness,"official_level":row["official_original_final_level"],
                "official_state":row["official_original_final_state"],
                "source":vis,
            },sort_keys=True),flush=True)
    if len(receipts)!=44 or len(roots)!=1:
        raise AssertionError("Genuine original stage4 independent entry mismatch")
    for case,_ in FROZEN:
        pair=[r for r in receipts if r["precommitted_original_source_case"]==case]
        if len(pair)!=2 or pair[0]["official_original_final_level"]!=pair[1]["official_original_final_level"] or pair[0]["official_original_final_state"]!=pair[1]["official_original_final_state"] or pair[0]["source_original_visual_metrics"]!=pair[1]["source_original_visual_metrics"]:
            raise AssertionError("Actual independent source case mismatch: "+case)
    successful=[{
        "case":r["precommitted_original_source_case"],"witness":r["native_original_independent_witness"],
        "word":r["authentic_stage4_sdk_word"],"level":r["official_original_final_level"],
        "state":r["official_original_final_state"]}
        for r in receipts if r["actual_original_level5_or_WIN"]]
    visible_side=[
        {"case":r["precommitted_original_source_case"],
         "witness":r["native_original_independent_witness"],
         "left_visual_pixels":r["source_original_visual_metrics"]["native_max_source_palette11to13_pixels_per_cup"]["left_lateral"]}
        for r in receipts if r["source_original_visual_metrics"] is not None
        and r["source_original_visual_metrics"]["native_max_source_palette11to13_pixels_per_cup"]["left_lateral"]>0
    ]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_LEFT_BAR_VERTICAL_BYPASS",
        "native_original_antecedent_run":39625230030,
        "genuine_original_sdk_reset_games":len(receipts),
        "prospectively_frozen_stage4_source_words":FROZEN,
        "real_sdk_level4_entry_blake2b16":next(iter(roots)),
        "native_official_level5_or_WIN_count":len(successful),
        "official_original_level5_source_progress":successful,
        "source_any_left_lateral_cup_visual_change":visible_side,
        "native_original_official_level_counts":dict(Counter(str(r["official_original_final_level"]) for r in receipts)),
        "native_original_official_state_counts":dict(Counter(str(r["official_original_final_state"]) for r in receipts)),
        "actual_original_sdk_frame_action_receipts":receipts,
        "limits":"Original SDK levels_completed>=5/WIN is the only official advancement; source pixel masks are not hidden objective/physics. Preserve all native frames NPZ, other lanes/rights unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_STAGE4_VERTICAL_BYPASS_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_stage4_source_words","actual_original_sdk_frame_action_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
