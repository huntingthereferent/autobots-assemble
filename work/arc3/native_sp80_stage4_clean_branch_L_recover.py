"""Genuine original SDK SP80 level4: restore lateral cup from clean branch.

Original run #39633351640 found a new ORIGINAL source state:
right-middle LEFT1, separate left-middle DOWN3/LEFT2, and L-shaped
LEFT5/UP1 => three top cups visibly fill, the left lateral cup has
0 palette11->13 changes, and no tested original left-border change.
The same L pose with the left-middle bar held fills all FOUR source
cup windows, but the native left x2..4 border flashes at frame12;
all cases remain official level4.

This is a bounded source counterfactual: hold the observed clean
middle DOWN3/LEFT2 state and vary ONLY original selected L-shaped
LEFT3..6 and UP0..3, with two closely related clean middle controls.
Measure original SDK level5/WIN, genuine selected source component
position, four cup timings and palette border transitions. No
inferred fluid engine or surrogate WIN classifier.
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
MIDDLE_CLEAN="6@24,33 2 2 2 3 3"
MIDDLE_D3L3="6@24,33 2 2 2 3 3 3"
MIDDLE_D4L2="6@24,33 2 2 2 2 3 3"
CUP={
    "left_lateral":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
def program(middle,left,up):
    assert 3<=left<=6 and 0<=up<=3
    L=" ".join(["6@34,42",*["3"]*left,*["1"]*up])
    return " ".join((RIGHT,middle,L,"5"))
FROZEN=(
    *((f"clean_mid_Lleft{l}_up{u}",program(MIDDLE_CLEAN,l,u))
      for l in (3,4,5,6) for u in (0,1,2,3)),
    *((f"middleD3L3_Lleft{l}_up{u}",program(MIDDLE_D3L3,l,u))
      for l in (4,5) for u in (1,2)),
    *((f"middleD4L2_Lleft{l}_up{u}",program(MIDDLE_D4L2,l,u))
      for l in (4,5) for u in (1,2)),
)
assert len(FROZEN)==24==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           and len(parse_plan(w))<=22 for _,w in FROZEN)

def selected(frame):
    return [
        {"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"]==9 and 19<=c["bbox"][1]<=53
    ]
def read_actual_original(root,pre,poured):
    if root.shape!=(64,64) or pre.shape!=(64,64) or poured.ndim!=3 or poured.shape[1:]!=(64,64):
        raise AssertionError("Actual original SDK 64x64 source frames required")
    first={name:None for name in CUP}
    maximum={name:0 for name in CUP}
    first_left_border=None
    flashes=[];previous=False
    first_lateral_new6=None
    all_simultaneous=None
    for t,frame in enumerate(poured):
        blue=(pre!=6)&(frame==6)
        if first_lateral_new6 is None and blue[35:44,5:11].any():
            ys,xs=np.nonzero(blue[35:44,5:11])
            first_lateral_new6={"frame":t,"original_source_yx":[[int(y+35),int(x+5)] for y,x in zip(ys,xs)]}
        full=0
        for k,(x0,y0,x1,y1) in CUP.items():
            original=(root[y0:y1+1,x0:x1+1]==11)
            if int(original.sum())!=45:raise AssertionError("Real source root cup moved")
            amount=int(np.count_nonzero(original&(frame[y0:y1+1,x0:x1+1]==13)))
            maximum[k]=max(maximum[k],amount)
            if amount==45 and first[k] is None:first[k]=t
            full+=int(amount==45)
        if full==4 and all_simultaneous is None:all_simultaneous=t
        mask=(pre[2:62,2:5]!=frame[2:62,2:5])
        active=bool(mask.any())
        if active and not previous:flashes.append(t)
        previous=active
        if active and first_left_border is None:
            first_left_border={
                "original_sdk_frame":t,
                "actual_native_source_changed_pixels":int(mask.sum()),
                "native_palette14_pixels":int(np.count_nonzero((pre[2:62,2:5]==1)&(frame[2:62,2:5]==14)))
            }
    return {
        "real_source_prepour_hash":hash_frame(pre),
        "real_source_pour_final_hash":hash_frame(poured[-1]),
        "original_sdk_pour_animation_frame_count":len(poured),
        "original_source_cup_first_full_frames":first,
        "source_cup_max_changed_to13":maximum,
        "first_four_simultaneous_cup_pixels":all_simultaneous,
        "first_genuine_new6_in_left_cup":first_lateral_new6,
        "first_native_left_border_color_transition":first_left_border,
        "actual_native_left_border_flash_episodes":flashes,
        "real_native_prepour_selected_object_components":selected(pre),
        "boundary":"Original source pixels are observations; they do not independently prove a fluid engine loss or win.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];frames_all={};roots=set()
    for case,word in FROZEN:
        parts=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(len(parts)-1)][-1]
            poured=raw["stage4_"+str(len(parts))]
            observed=read_actual_original(root,pre,poured)
            native_move=[
                {"step":e["index"],"action":e["genuine_original_action"],
                 "original_native_click":e["real_native_click_xy"],
                 "actual_source_pixel_at_click":e["original_source_pixel_before_click"],
                 "selected_source_bbox_after":selected(raw["stage4_"+str(e["index"])][-1]),
                 "actual_source_hash_after":e["source_frame_after_blake2b16"]}
                for e in sdk["genuine_original_stage4_action_ledger"]
                if e["genuine_original_action"] in (1,2,3,4,6)
            ]
            row={
                "predeclared_native_source_case":case,
                "independent_original_sdk_witness":witness,
                "real_original_stage4_word":word,
                "genuine_original_sdk_final_level":sdk["true_original_sdk_final_level"],
                "genuine_original_sdk_final_state":sdk["true_original_sdk_final_state"],
                "official_native_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "actual_original_frame_observations":observed,
                "original_sdk_selected_source_step_receipts":native_move,
                "all_actual_original_native_action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            records.append(row)
            for k,f in raw.items():frames_all[f"{case}_{witness}_{k}"]=f
            print("ORIGINAL_SP80_CLEAN_BRANCH_L_CASE "+json.dumps({
                "case":case,"witness":witness,
                "sdk_level":row["genuine_original_sdk_final_level"],
                "sdk_state":row["genuine_original_sdk_final_state"],
                "source":observed,
            },sort_keys=True),flush=True)
    if len(records)!=48 or len(roots)!=1:raise AssertionError("Missing genuine original SDK A/B entries")
    for case,_ in FROZEN:
        pair=[v for v in records if v["predeclared_native_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["genuine_original_sdk_final_level"]!=pair[1]["genuine_original_sdk_final_level"]
            or pair[0]["genuine_original_sdk_final_state"]!=pair[1]["genuine_original_sdk_final_state"]
            or pair[0]["actual_original_frame_observations"]!=pair[1]["actual_original_frame_observations"]
            or pair[0]["original_sdk_selected_source_step_receipts"]!=pair[1]["original_sdk_selected_source_step_receipts"]
        ):raise AssertionError("Independent source entry mismatch "+case)
    progress=[{
        "case":r["predeclared_native_source_case"],"witness":r["independent_original_sdk_witness"],
        "original_sdk_stage4_word":r["real_original_stage4_word"],
        "official_level":r["genuine_original_sdk_final_level"],
        "official_state":r["genuine_original_sdk_final_state"]}
        for r in records if r["official_native_level5_or_WIN"]
    ]
    four=[{
        "case":r["predeclared_native_source_case"],"witness":r["independent_original_sdk_witness"],
        "left_border":r["actual_original_frame_observations"]["first_native_left_border_color_transition"]}
        for r in records if r["actual_original_frame_observations"]["first_four_simultaneous_cup_pixels"] is not None]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_CLEAN_MIDDLE_BRANCH_LATERAL_RESTORATION",
        "authentic_source_antecedent_run":39633351640,
        "original_sdk_independent_fresh_resets":len(records),
        "prospectively_frozen_original_words":FROZEN,
        "real_original_level4_root_hash":next(iter(roots)),
        "genuine_original_level5_or_WIN_count":len(progress),
        "actual_original_sdk_progresses":progress,
        "visually_four_cup_native_cases":four,
        "true_original_sdk_level_histogram":dict(Counter(str(v["genuine_original_sdk_final_level"]) for v in records)),
        "true_original_sdk_state_histogram":dict(Counter(str(v["genuine_original_sdk_final_state"]) for v in records)),
        "original_native_full_receipts":records,
        "limits":"Only SDK levels_completed>=5/WIN proves progression; visually complete cup windows and border changes are partial source observations. Full original SDK returned frames preserved.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames_all)
    print("ORIGINAL_SP80_CLEAN_BRANCH_L_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("prospectively_frozen_original_words","original_native_full_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
