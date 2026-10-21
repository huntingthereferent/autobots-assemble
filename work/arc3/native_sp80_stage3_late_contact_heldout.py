"""Actual original SP80 SDK heldout: upstream contact around frame27->28.

Original run #39557242249: selected upper right2/down1, other upper
down1, middle right4, receiving lower-left10/up1, bottom right1 gave
four source cup visual regions changed on native frame27 and tested
source y59..62 boundary first changing frame28. No official advancement.
This bounded heldout trial varies ONLY existing upper-bar positions
around that true source arrangement. It does NOT decode fluid physics,
simulate the game or use pixel colors as a winner oracle.
"""
from __future__ import annotations

import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

SEL="6@20,18 4 4 2"
OTHER="6@40,18 2"
MID="6@10,30 4 4 4 4"
RECEIVER="6@46,33 1 "+" ".join(["3"]*10)
BOTTOM="6@40,42 4"
CUPS=((8,16),(26,34),(38,46),(50,58))

def proposal(selected,other):
    return " ".join(p for p in (selected,other,MID,RECEIVER,BOTTOM,"5") if p)

FROZEN=(
    ("parent_frame27_28",proposal(SEL,OTHER)),
    ("other_held_clean_control",proposal(SEL,"")),
    ("selected_right1_down1",proposal("6@20,18 4 2",OTHER)),
    ("selected_right3_down1",proposal("6@20,18 4 4 4 2",OTHER)),
    ("selected_right4_down1",proposal("6@20,18 4 4 4 4 2",OTHER)),
    ("selected_right2_held",proposal("6@20,18 4 4",OTHER)),
    ("selected_right2_up1",proposal("6@20,18 4 4 1",OTHER)),
    ("selected_right2_down2",proposal("6@20,18 4 4 2 2",OTHER)),
    ("other_down1_left1",proposal(SEL,"6@40,18 2 3")),
    ("other_down1_right1",proposal(SEL,"6@40,18 2 4")),
    ("other_down2",proposal(SEL,"6@40,18 2 2")),
    ("other_down3",proposal(SEL,"6@40,18 2 2 2")),
    ("selected_right1_other_down1_left1",proposal("6@20,18 4 2","6@40,18 2 3")),
    ("selected_right3_other_down1_right1",proposal("6@20,18 4 4 4 2","6@40,18 2 4")),
)
assert len(FROZEN)==14==len(set(name for name,word in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(w))<=32 and
    parse_plan(w)[-1][0]==5 and
    sum(a==5 for a,xy in parse_plan(w))==1 and
    all(xy is not None for a,xy in parse_plan(w) if a==6)
    for name,w in FROZEN
)

def native_observation(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3:
        raise AssertionError("Expected genuine original 64x64 source frames")
    cup_first=[None]*4
    four_first=None;boundary_first=None
    x58_right_first=None
    first_other_contact=None
    max_cups=0
    for t,frame in enumerate(frames):
        if frame.shape!=pre.shape:
            raise AssertionError("Source SDK frame shape changed")
        color6=(pre!=6)&(frame==6)
        if first_other_contact is None and color6[19,38:62].any():
            first_other_contact={
                "frame":t,
                "real_native_new_color6_x":[int(x) for x in np.flatnonzero(color6[19,38:62])+38],
            }
        if x58_right_first is None and color6[58,50:62].any():
            x58_right_first={
                "frame":t,
                "real_native_new_color6_x":[int(x) for x in np.flatnonzero(color6[58,50:62])+50],
            }
        colored=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUPS
        ]
        for i,n in enumerate(colored):
            if n==45 and cup_first[i] is None:cup_first[i]=t
        count=sum(n==45 for n in colored)
        max_cups=max(max_cups,count)
        if count==4 and four_first is None:four_first=t
        changed=pre[59:63,2:62]!=frame[59:63,2:62]
        if changed.any() and boundary_first is None:
            boundary_first={
                "frame":t,
                "changed_tested_native_pixels":int(changed.sum()),
                "source_new_color6_x_at_y58":[int(x) for x in np.flatnonzero(color6[58])],
            }
    bar_components=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and c["bbox"][1]<=53
    ]
    return {
        "original_source_pre_pour_blake2b16":hash_frame(pre),
        "original_source_after_pour_blake2b16":hash_frame(frames[-1]),
        "original_native_animation_frame_count":len(frames),
        "original_source_prepour_selected_components":bar_components,
        "first_other_upper_y19_right_half_source_color6":first_other_contact,
        "first_new_right_source_color6_at_y58":x58_right_first,
        "first_full_source_cup_region_frames":cup_first,
        "max_simultaneously_full_visual_cups":max_cups,
        "first_four_simultaneous_source_cups_frame":four_first,
        "first_observed_source_y59_62_boundary_change":boundary_first,
        "observed_test_region_unchanged":boundary_first is None,
        "observational_limit":"Visual signals and tested boundary color are not original game rules or validated leak causes.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,frames=real_trial(witness,entry,case,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            poured=frames.get("stage3_"+str(n))
            before=frames.get("stage3_"+str(n-1),frames["entry2_11"])[-1]
            source=native_observation(before,poured) if poured is not None else None
            row={
                "prospective_source_case":case,
                "genuine_source_witness":witness,
                "real_original_sdk_action_word":word,
                "original_sdk_official_level":sdk["official_original_final_level"],
                "original_sdk_official_state":sdk["official_original_final_state"],
                "original_sdk_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "native_original_source_observations":source,
                "actual_original_sdk_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in sdk["full_original_sdk_action_events"]],
            }
            rows.append(row)
            for k,arr in frames.items():arrays[f"{case}_{witness}_{k}"]=arr
            print("ORIGINAL_SP80_LATE_CONTACT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_source_level":row["original_sdk_official_level"],
                "official_source_state":row["original_sdk_official_state"],
                "actual_source_observation":source,
            },sort_keys=True),flush=True)
    if len(rows)!=28 or len(roots)!=1:
        raise AssertionError("Missing original SDK independent level3 source witnesses")
    success=[
        {"case":r["prospective_source_case"],"witness":r["genuine_source_witness"],
         "official_level":r["original_sdk_official_level"],
         "official_state":r["original_sdk_official_state"],
         "true_original_word":r["real_original_sdk_action_word"]}
        for r in rows if r["original_sdk_level4_or_WIN"]
    ]
    visual_four_no_boundary=[
        {"case":r["prospective_source_case"],"witness":r["genuine_source_witness"]}
        for r in rows if r["native_original_source_observations"] is not None
        and r["native_original_source_observations"]["max_simultaneously_full_visual_cups"]==4
        and r["native_original_source_observations"]["observed_test_region_unchanged"]
    ]
    summary={
        "kind":"ORIGINAL_SP80_STAGE3_UPPER_HELDOUT_LATE_CONTACT",
        "authentic_antecedent_source_run":39557242249,
        "genuine_original_sdk_reset_games":len(rows),
        "frozen_original_source_words":FROZEN,
        "verified_native_original_stage3_root_blake2b16":next(iter(roots)),
        "official_original_level4_or_WIN_count":len(success),
        "actual_original_game_progress":success,
        "visual_four_cups_no_test_bottom_change":visual_four_no_boundary,
        "official_original_level_counts":dict(Counter(str(r["original_sdk_official_level"]) for r in rows)),
        "official_original_state_counts":dict(Counter(str(r["original_sdk_official_state"]) for r in rows)),
        "true_original_sdk_records":rows,
        "limits":"Only actual original SDK level>=4 or WIN is a win. Color6, four visual cups and tested y59–62 boundary region are observations, not causal engine semantics. Native raw frames archived NPZ; other lanes/licensing untouched.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_LATE_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("frozen_original_source_words","true_original_sdk_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
