"""Original SDK SP80 stage3: recover missing THIRD cup from clean higher catcher.

Authentic original SP80 native run #39595959890 (PR #359) found an
important threshold with all upstream pieces held constant:
  bottom catcher right1/up2 -> visually full cups [21,8,27,27],
                                y59..62 boundary first changes frame28;
  bottom catcher right1/up3 -> full cups [21,8,None,27],
                                no measured bottom boundary changes.
The THIRD source cup x38..46, not the fourth x50..58, is missing at
up3. This disproves the naive 'missing fourth cup' interpretation.

Hold the exact clean source right1/up3 catcher in this new
prospectively frozen experiment and vary only closely grounded
upstream five-selectable-class interventions to restore source cup3
without losing the original clean bottom boundary. The guide's
pour/spill descriptions are background only, NOT reconstructed physics.
Only original Arcade.NORMAL SDK levels_completed>=4 or WIN counts.
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

UPPER_SELECTED="6@20,18 4 4 2"
UPPER_OTHER="6@40,18 2"
MIDDLE="6@10,30 4 4 4 4"
LOWER="6@46,33 1 "+" ".join(["3"]*10)
BOTTOM_UP2="6@40,42 4 1 1"
BOTTOM_UP3="6@40,42 4 1 1 1"
BOTTOM_UP4="6@40,42 4 1 1 1 1"
CUP_WINDOWS=((8,16),(26,34),(38,46),(50,58))
SOURCE_ROWS=(19,26,29,32,35,41,47,52,56,58)

def script(upper_selected=UPPER_SELECTED,other=UPPER_OTHER,
           middle=MIDDLE,receiver=LOWER,bottom=BOTTOM_UP3):
    return " ".join(x for x in
       (upper_selected,other,middle,receiver,bottom,"5") if x)

FROZEN=(
    ("dirty_four_cup_up2_control",script(bottom=BOTTOM_UP2)),
    ("clean_missing_third_up3_parent",script()),
    ("clean_up4_parent",script(bottom=BOTTOM_UP4)),

    # Vary source upper contact only; independently seen legal movements.
    ("upper_selected_right1_down1",script(upper_selected="6@20,18 4 2")),
    ("upper_selected_right3_down1",script(upper_selected="6@20,18 4 4 4 2")),
    ("upper_selected_right2_held_height",script(upper_selected="6@20,18 4 4")),
    ("upper_selected_right2_down2",script(upper_selected="6@20,18 4 4 2 2")),

    # Other upper piece controls the extra right source branch in PR #353.
    ("other_upper_held",script(other="")),
    ("other_upper_down2",script(other="6@40,18 2 2")),
    ("other_upper_down1_left1",script(other="6@40,18 2 3")),
    ("other_upper_down1_right1",script(other="6@40,18 2 4")),

    # Movable middle marker is one linked selected assembly, not two bars.
    ("linked_middle_right3",script(middle="6@10,30 4 4 4")),
    ("linked_middle_right5",script(middle="6@10,30 4 4 4 4 4")),
    ("linked_middle_up1",script(middle=MIDDLE+" 1")),
    ("linked_middle_down1",script(middle=MIDDLE+" 2")),

    # Lower source receiving bar remains left, with near-parent adjustments.
    ("lower_held_height_left10",script(receiver="6@46,33 "+" ".join(["3"]*10))),
    ("lower_up2_left10",script(receiver="6@46,33 1 1 "+" ".join(["3"]*10))),
    ("lower_up1_left9",script(receiver="6@46,33 1 "+" ".join(["3"]*9))),
    ("lower_up1_left11",script(receiver="6@46,33 1 "+" ".join(["3"]*11))),

    # Small couplings, source-grounded nearby routes only.
    ("upper_right1_middle_right5",script(upper_selected="6@20,18 4 2",middle="6@10,30 4 4 4 4 4")),
    ("upper_right3_middle_right3",script(upper_selected="6@20,18 4 4 4 2",middle="6@10,30 4 4 4")),
    ("other_down2_middle_up1",script(other="6@40,18 2 2",middle=MIDDLE+" 1")),
    ("other_down1_left1_middle_right5",script(other="6@40,18 2 3",middle="6@10,30 4 4 4 4 4")),

    # One order contrast with same nominal moves; native source is oracle.
    ("bottom_up3_before_right1",script(bottom="6@40,42 1 1 1 4")),
    ("lower_held_middle_right3_up3",script(receiver="6@46,33 "+" ".join(["3"]*10),middle="6@10,30 4 4 4")),
)
assert len(FROZEN)==25==len(set(n for n,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=38
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word in FROZEN
)

def intervals(xs):
    xs=list(map(int,xs))
    if not xs:return []
    result=[];start=prev=xs[0]
    for x in xs[1:]:
        if x>prev+1:
            result.append([start,prev]);start=x
        prev=x
    result.append([start,prev])
    return result

def measure_actual_source(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Missing authentic original SDK 64x64 frames")
    first_full=[None]*4;first_four=None;max_full=0
    first_spill=None;spill_episodes=[];prior_spill=False
    first_new_at_rows={str(y):None for y in SOURCE_ROWS}
    first_third_color13=None;third_max=0
    for t,frame in enumerate(frames):
        new6=(pre!=6)&(frame==6)
        for y in SOURCE_ROWS:
            xs=np.flatnonzero(new6[y])
            if first_new_at_rows[str(y)] is None and xs.size:
                first_new_at_rows[str(y)]={"frame":t,"new_source_palette6_x_intervals":intervals(xs)}
        n=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUP_WINDOWS
        ]
        for i,c in enumerate(n):
            if c==45 and first_full[i] is None:first_full[i]=t
        if n[2]>third_max:
            third_max=n[2]
            first_third_color13={"frame":t,"changed_native_pixels":n[2]}
        full=sum(v==45 for v in n)
        max_full=max(max_full,full)
        if full==4 and first_four is None:first_four=t
        changed=pre[59:63,2:62]!=frame[59:63,2:62]
        spill=bool(changed.any())
        if spill and not prior_spill:spill_episodes.append(t)
        prior_spill=spill
        if spill and first_spill is None:
            first_spill={
                "frame":t,
                "changed_source_bottom_test_pixels":int(changed.sum()),
                "new_palette6_y58_intervals":intervals(np.flatnonzero(new6[58])),
            }
    source_comps=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and 14<=c["bbox"][1]<=54
    ]
    return {
        "genuine_sdk_pre_pour_blake2b16":hash_frame(pre),
        "genuine_sdk_after_pour_blake2b16":hash_frame(frames[-1]),
        "original_pour_frame_count":len(frames),
        "original_source_prepour_selected_components":source_comps,
        "first_observed_full_cup_11to13_frames":first_full,
        "observed_third_cup_max_changed_pixels":third_max,
        "observed_third_cup_first_max_source_frame":first_third_color13,
        "max_simultaneous_full_cup_regions":max_full,
        "first_all_four_source_cup_regions_full":first_four,
        "first_tested_bottom_region_change":first_spill,
        "observed_source_bottom_color_change_episodes":spill_episodes,
        "first_source_new_color6_at_rows":first_new_at_rows,
        "source_limit":"Screen-only source evidence: palette13, bottom region and visible caps do not define SDK win or hidden fluid dynamics.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=real_trial(witness,entry,case,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            frames=stacks.get("stage3_"+str(n))
            prior=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            metrics=measure_actual_source(prior,frames) if frames is not None else None
            rec={
                "precommitted_source_trial":case,
                "actual_original_sdk_witness":witness,
                "original_native_action_word":word,
                "official_source_level":sdk["official_original_final_level"],
                "official_source_state":sdk["official_original_final_state"],
                "native_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "native_source_disposition":sdk["trial_disposition"],
                "genuine_original_pixel_observations":metrics,
                "actual_original_sdk_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in sdk["original_stage3_intervention_events"]],
            }
            records.append(rec)
            for k,stack in stacks.items():arrays[f"{case}_{witness}_{k}"]=stack
            print("ORIGINAL_SP80_THIRD_CUP_CLEAN_CASE "+json.dumps({
                "case":case,"witness":witness,
                "native_level":rec["official_source_level"],
                "native_state":rec["official_source_state"],
                "observed":metrics,
            },sort_keys=True),flush=True)
    if len(records)!=50 or len(roots)!=1:
        raise AssertionError("Actual original SDK independent witnesses missing")
    for case,_ in FROZEN:
        pair=[r for r in records if r["precommitted_source_trial"]==case]
        if len(pair)!=2:raise AssertionError("Expected independent A/B original witnesses")
        ma=pair[0]["genuine_original_pixel_observations"]
        mb=pair[1]["genuine_original_pixel_observations"]
        if (pair[0]["official_source_level"]!=pair[1]["official_source_level"]
            or pair[0]["official_source_state"]!=pair[1]["official_source_state"]
            or ma!=mb):
            raise AssertionError("Actual original source witnesses differ: "+case)
    gains=[
        {"case":r["precommitted_source_trial"],"witness":r["actual_original_sdk_witness"],
         "word":r["original_native_action_word"],"sdk_level":r["official_source_level"],
         "sdk_state":r["official_source_state"]}
        for r in records if r["native_level4_or_WIN"]
    ]
    four_no_tested_bottom=[
        {"case":r["precommitted_source_trial"],"witness":r["actual_original_sdk_witness"]}
        for r in records if r["genuine_original_pixel_observations"] is not None
        and r["genuine_original_pixel_observations"]["first_all_four_source_cup_regions_full"] is not None
        and r["genuine_original_pixel_observations"]["first_tested_bottom_region_change"] is None
    ]
    summary={
        "kind":"ACTUAL_ORIGINAL_SP80_STAGE3_RESTORE_THIRD_WITHOUT_SPILL",
        "native_sdk_parent_trial":39595959890,
        "independently_reset_original_SDK_games":len(records),
        "frozen_original_sdk_programs":FROZEN,
        "verified_original_stage3_root_blake2b16":next(iter(roots)),
        "original_sdk_level4_or_WIN_count":len(gains),
        "actual_source_progress_witnesses":gains,
        "visual_only_four_cup_no_tested_bottom":four_no_tested_bottom,
        "native_original_level_histogram":dict(Counter(str(r["official_source_level"]) for r in records)),
        "native_original_state_histogram":dict(Counter(str(r["official_source_state"]) for r in records)),
        "actual_original_sdk_receipts":records,
        "limits":"Only authentic Arcade.NORMAL SP80 levels_completed>=4 or WIN proves advancement. Color windows and y59..62 source boundary are partial observations. All true SDK 64x64 frames retained; no private engine conjectures or other lane/license changes.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_THIRD_CUP_CLEAN_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("frozen_original_sdk_programs","actual_original_sdk_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
