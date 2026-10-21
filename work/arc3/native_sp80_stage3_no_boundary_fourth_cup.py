"""Genuine original SP80 stage3 upstream route toward fourth cup without bottom-edge change.

Continuation of original SDK results PRs #334, #335 and #336.
Run #39551239285: fixing the lower-right bar at ten original ACTION3
left movements and the original bottom bar at two ACTION4 right
movements gives three observed fully changed palette11->13 cup
regions and NO measured change on source y59..62 bottom boundary,
both original source entry witnesses. With bottom right one, four cups
change but native boundary changes before fourth cup. Neither is WIN.

This prospective finite native test fixes the observed no-boundary
two-bar configuration and varies *upstream upper-source* placement.
Original Arcade.NORMAL SP80 source only; no guessed game mechanics.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

MID4="6@10,30 4 4 4 4"
MID3="6@10,30 4 4 4"
MID5="6@10,30 4 4 4 4 4"
LOWER10="6@46,33 "+" ".join(["3"]*10)
BOTTOM_RIGHT1="6@40,42 4"
BOTTOM_RIGHT2="6@40,42 4 4"
BOTTOM_RIGHT3="6@40,42 4 4 4"

def shift(click, action, steps):
    return ("6@%d,%d " % click)+" ".join([str(action)]*steps)

def program(*sequences):
    return " ".join(s for s in (*sequences,"5") if s)

BASE=(MID4,LOWER10,BOTTOM_RIGHT2)

# One intervention dimension at a time, then a few source-specific
# coupled contrasts near the actual source no-boundary branch.
FROZEN=(
    ("no_boundary_parent_right2",program(*BASE)),
    ("parent_right1_four_cup_control",program(MID4,LOWER10,BOTTOM_RIGHT1)),
    ("parent_right3_no_boundary_control",program(MID4,LOWER10,BOTTOM_RIGHT3)),
    ("upper_selected_left1",program(shift((20,18),3,1),*BASE)),
    ("upper_selected_left2",program(shift((20,18),3,2),*BASE)),
    ("upper_selected_left3",program(shift((20,18),3,3),*BASE)),
    ("upper_selected_left4",program(shift((20,18),3,4),*BASE)),
    ("upper_selected_right1",program(shift((20,18),4,1),*BASE)),
    ("upper_selected_right2",program(shift((20,18),4,2),*BASE)),
    ("upper_selected_right3",program(shift((20,18),4,3),*BASE)),
    ("upper_selected_up1",program(shift((20,18),1,1),*BASE)),
    ("upper_selected_up2",program(shift((20,18),1,2),*BASE)),
    ("upper_selected_down1",program(shift((20,18),2,1),*BASE)),
    ("upper_selected_down2",program(shift((20,18),2,2),*BASE)),
    ("upper_right_left1",program(shift((40,18),3,1),*BASE)),
    ("upper_right_left2",program(shift((40,18),3,2),*BASE)),
    ("upper_right_left3",program(shift((40,18),3,3),*BASE)),
    ("upper_right_right1",program(shift((40,18),4,1),*BASE)),
    ("upper_right_right2",program(shift((40,18),4,2),*BASE)),
    ("upper_right_up1",program(shift((40,18),1,1),*BASE)),
    ("upper_right_down1",program(shift((40,18),2,1),*BASE)),
    ("upper_left1_rightbar_left1",program(shift((20,18),3,1),shift((40,18),3,1),*BASE)),
    ("upper_left2_rightbar_left2",program(shift((20,18),3,2),shift((40,18),3,2),*BASE)),
    ("upper_right1_rightbar_left1",program(shift((20,18),4,1),shift((40,18),3,1),*BASE)),
    ("upper_right2_rightbar_left2",program(shift((20,18),4,2),shift((40,18),3,2),*BASE)),
    ("mid3_same_two_bar_no_boundary",program(MID3,LOWER10,BOTTOM_RIGHT2)),
    ("mid5_same_two_bar_no_boundary",program(MID5,LOWER10,BOTTOM_RIGHT2)),
    ("bottom_first_no_boundary",program(BOTTOM_RIGHT2,MID4,LOWER10)),
    ("lower_first_no_boundary",program(LOWER10,MID4,BOTTOM_RIGHT2)),
)
assert len(FROZEN)==29==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,_ in parse_plan(word))==1
    and len(parse_plan(word))<=32
    for _,word in FROZEN
)
CUPS=((8,16),(26,34),(38,46),(50,58))

def source_measure(pre,animation):
    if pre.shape!=(64,64):
        raise AssertionError("Missing real original 64x64 pre-pour frame")
    bottom_event=None
    four_at=None
    cup_first=[None]*4
    maxima=[0]*4
    max_simultaneous=0
    boundary_changed_at_any_point=False
    for t,frame in enumerate(animation):
        if frame.shape!=pre.shape:
            raise AssertionError("Native SDK returned wrong frame geometry")
        counts=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUPS
        ]
        for i,count in enumerate(counts):
            maxima[i]=max(maxima[i],count)
            if count==45 and cup_first[i] is None:cup_first[i]=t
        simultaneous=sum(x==45 for x in counts)
        max_simultaneous=max(max_simultaneous,simultaneous)
        if four_at is None and simultaneous==4:four_at=t
        changed=pre[59:63,2:62]!=frame[59:63,2:62]
        if np.any(changed):
            boundary_changed_at_any_point=True
            if bottom_event is None:
                bottom_event={
                    "actual_original_animation_frame":t,
                    "changed_bottom_pixels":int(changed.sum()),
                    "original_new_color6_x_at_y58":[
                        int(i) for i in np.where(
                            (pre[58]!=6)&(frame[58]==6)
                        )[0]
                    ],
                }
    selected=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (8,9) and 15<=c["bbox"][1]<=44
    ]
    return {
        "actual_source_pre_pour_blake2b16":hash_frame(pre),
        "actual_source_post_pour_blake2b16":hash_frame(animation[-1]),
        "actual_original_sdk_animation_frames":len(animation),
        "original_source_selectable_bboxes":selected,
        "first_bottom_boundary_change":bottom_event,
        "any_observed_bottom_y59_62_pixel_change":boundary_changed_at_any_point,
        "original_cup11_to13_max_counts":maxima,
        "original_cup_first_full_change_frame":cup_first,
        "first_simultaneous_four_cup_frame":four_at,
        "max_simultaneously_fully_changed_cup_regions":max_simultaneous,
        "boundary":"These are original returned pixel observations, not a leak detector or objective.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    records=[];native_arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            row,frames=real_trial(witness,entry,case,word)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            poured=frames.get("stage3_"+str(n))
            before=frames.get("stage3_"+str(n-1),frames["entry2_11"])[-1]
            metrics=source_measure(before,poured) if poured is not None else None
            rec={
                "native_source_case":case,
                "independent_original_game_witness":witness,
                "original_native_word":word,
                "actual_original_level_after":row["official_original_final_level"],
                "actual_original_state_after":row["official_original_final_state"],
                "original_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "original_sdk_trial_disposition":row["trial_disposition"],
                "observed_original_one_pour":metrics,
                "real_original_sdk_actions":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in row["full_original_sdk_action_events"]],
            }
            records.append(rec)
            for step,arr in frames.items():
                native_arrays[f"{case}_{witness}_{step}"]=arr
            print("ORIGINAL_SP80_UPSTREAM_SOURCE_CASE "+json.dumps({
                "case":case,"witness":witness,
                "native_level":rec["actual_original_level_after"],
                "native_state":rec["actual_original_state_after"],
                "actual_source":metrics,
            },sort_keys=True),flush=True)
    if len(records)!=58 or len(roots)!=1:
        raise AssertionError("Original SP80 source roots or independent reset roster missing")
    successes=[{
        "case":r["native_source_case"],
        "witness":r["independent_original_game_witness"],
        "word":r["original_native_word"],
        "original_level":r["actual_original_level_after"],
        "original_state":r["actual_original_state_after"]}
        for r in records if r["original_sdk_level4_or_WIN"]]
    summary={
        "kind":"ORIGINAL_SP80_LEVEL3_UPSTREAM_FOURTH_CUP_NO_BOUNDARY",
        "authentic_source_antecedents":[39549622886,39550721172,39551239285],
        "original_native_independent_sdk_reset_games":len(records),
        "prospective_original_native_words":FROZEN,
        "identical_original_stage3_root_blake2b16":next(iter(roots)),
        "real_original_level4_or_WIN_count":len(successes),
        "actual_source_successes":successes,
        "official_original_last_level_counts":dict(Counter(str(r["actual_original_level_after"]) for r in records)),
        "official_original_last_state_counts":dict(Counter(r["actual_original_state_after"] for r in records)),
        "real_original_sdk_source_records":records,
        "boundary":"A no-change y59-62 region does not prove zero spill or success. Four changed cup regions do not prove level completion. Only genuine SDK level>=4/WIN reports progress. All original SDK frame arrays retained in NPZ; no new physics, F3 mapping, engine, license or other lanes.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**native_arrays)
    print("ORIGINAL_SP80_UPSTREAM_SOURCE_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("prospective_original_native_words","real_original_sdk_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
