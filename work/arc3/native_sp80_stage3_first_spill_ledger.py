"""Original-SDK SP80 level3 first spill-contact and failure-feedback ledger.

The verified original native run #39557791993 independently reproduced
four cup palette11->13 regions at returned frame27 and the tested
y59..62 boundary palette1->14 transition at frame28. Independent raw
NPZ inspection found new source-color6 pixels x35..37/y58 concurrent
with that first boundary signal, followed by alternating source frame
line-color changes before all liquid cleared.

The public SP80 mechanics guide documents spill-line flashing and
missed-cup blinking after failed pours. This investigation records
whether the original SDK actually returns those signatures and tests
a small predeclared set of EXISTING lower receiver and bottom bar moves
near that specific x35..37 path. Neither pixel cue nor external guide
replaces the genuine SDK official level4/WIN oracle.
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

UPPER="6@20,18 4 4 2 6@40,18 2"
MID="6@10,30 4 4 4 4"
LEFT="3"
BOTTOM="6@40,42"
CUP_RANGES=((8,16),(26,34),(38,46),(50,58))

def receiver(left_steps=10,up=1):
    return "6@46,33 "+" ".join(["1"]*up+["3"]*left_steps)

def bottom(right=1,vertical=None):
    return " ".join([BOTTOM]+(["4"]*right)+([] if vertical is None else [str(vertical)]))

def word(lower,bott,mid=MID,upper=UPPER):
    return " ".join([upper,mid,lower,bott,"5"])

# All source actions are predeclared. Every session starts a *new*
# genuine source SP80 environment and reaches the same verified level3.
FROZEN=(
    ("source_parent_27_28",word(receiver(10,1),bottom(1))),
    ("source_parent_held_receiver",word(receiver(10,0),bottom(1))),
    ("source_parent_bottom_right2",word(receiver(10,1),bottom(2))),
    ("source_left9_bottom1",word(receiver(9,1),bottom(1))),
    ("source_left11_bottom1",word(receiver(11,1),bottom(1))),
    ("source_left9_bottom2",word(receiver(9,1),bottom(2))),
    ("source_left11_bottom2",word(receiver(11,1),bottom(2))),
    ("source_receiver_up2_bottom1",word(receiver(10,2),bottom(1))),
    ("source_receiver_down1_bottom1",word("6@46,33 2 "+" ".join([LEFT]*10),bottom(1))),
    ("source_bottom_held",word(receiver(10,1),BOTTOM)),
    ("source_bottom_up1",word(receiver(10,1),bottom(1,1))),
    ("source_bottom_down1",word(receiver(10,1),bottom(1,2))),
    ("source_mid_up1",word(receiver(10,1),bottom(1),MID+" 1")),
    ("source_mid_down1",word(receiver(10,1),bottom(1),MID+" 2")),
    ("source_other_upper_held_control",word(receiver(10,1),bottom(1),upper="6@20,18 4 4 2")),
)
assert len(FROZEN)==15==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(program)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(program))==1
    and all(xy is not None for a,xy in parse_plan(program) if a==6)
    and len(parse_plan(program))<=38
    for _,program in FROZEN
)

def intervals(indices):
    indices=list(map(int,indices))
    if not indices:return []
    out=[]
    begin=last=indices[0]
    for x in indices[1:]:
        if x!=last+1:
            out.append([begin,last]);begin=x
        last=x
    out.append([begin,last])
    return out

def source_failure_ledger(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Genuine original source stack required")
    baseline_bottom=pre[59:63,2:62]
    bottom_status=[]
    cups_initial_full=[None]*4
    source_colors_cups=[]
    first_four=None
    first_boundary=None
    no_new_blue_at_first=None
    for t,frame in enumerate(frames):
        # Only observed source pixel contrast, not decoded engine fluid.
        border=frame[59:63,2:62]
        changed=baseline_bottom!=border
        bottom_status.append(bool(changed.any()))
        cup_status=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&
                (frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUP_RANGES
        ]
        source_colors_cups.append(cup_status)
        for j,count in enumerate(cup_status):
            if cups_initial_full[j] is None and count==45:
                cups_initial_full[j]=t
        if first_four is None and sum(x==45 for x in cup_status)==4:
            first_four=t
        if first_boundary is None and changed.any():
            pairs,n=np.unique(np.stack((baseline_bottom[changed],border[changed]),axis=1),axis=0,return_counts=True)
            new6=(pre!=6)&(frame==6)
            first_boundary={
                "original_frame_index":t,
                "genuine_changed_bottom_test_pixels":int(changed.sum()),
                "actual_bottom_source_palette_transitions":[
                    [int(pair[0]),int(pair[1]),int(k)] for pair,k in zip(pairs,n)
                ],
                "new_original_source_color6_x_at_y58":intervals(np.flatnonzero(new6[58])),
                "new_original_source_color6_x_at_y57":intervals(np.flatnonzero(new6[57])),
                "new_original_source_color6_x_at_y56":intervals(np.flatnonzero(new6[56])),
            }
    episodes=[]
    for t,active in enumerate(bottom_status):
        if active and (t==0 or not bottom_status[t-1]):episodes.append(t)
    final_feedback_frames=[
        {"source_frame":int(i),
         "bottom_test_region_changed":bottom_status[i],
         "source_cup_11to13_counts":source_colors_cups[i]}
        for i in range(max(0,len(frames)-10),len(frames))
    ]
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and c["bbox"][1]<=53
    ]
    return {
        "actual_source_prepour_blake2b16":hash_frame(pre),
        "actual_source_pour_final_blake2b16":hash_frame(frames[-1]),
        "original_sdk_frame_count":len(frames),
        "actual_source_selectable_pre_pour_components":components,
        "first_four_simultaneously_visual_cup_regions":first_four,
        "original_first_full_source_cup_region_frames":cups_initial_full,
        "first_genuine_source_bottom_line_change":first_boundary,
        "observed_source_bottom_change_episodes":episodes,
        "last_original_source_feedback_frames":final_feedback_frames,
        "no_tested_bottom_transition":first_boundary is None,
        "note":"Source screenshot colors and feedback timing only; guide's spill blink rule is context, never a substitute SDK win test.",
    }

def self_test():
    assert intervals(np.array([3,4,5,9,11,12]))==[[3,5],[9,9],[11,12]]
    a=np.full((64,64),12,dtype=np.uint8)
    a[59:63,2:62]=1
    frames=np.stack([a.copy() for _ in range(7)])
    frames[1,58,35:38]=6
    frames[1,59:62,2:62]=14
    frames[3,58,35:38]=6
    frames[3,59:62,2:62]=14
    record=source_failure_ledger(a,frames)
    assert record["observed_source_bottom_change_episodes"]==[1,3]
    assert record["first_genuine_source_bottom_line_change"]["new_original_source_color6_x_at_y58"]==[[35,37]]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    self_test()
    rows=[];actual_arrays={};roots=set()
    for case,plan in FROZEN:
        n=len(parse_plan(plan))
        for witness,entry in STAGE1_WITNESSES:
            row,stacks=real_trial(witness,entry,case,plan)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            returned=stacks.get("stage3_"+str(n))
            previous=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            observed=source_failure_ledger(previous,returned) if returned is not None else None
            receipt={
                "predeclared_genuine_source_case":case,
                "independent_native_source_witness":witness,
                "genuine_original_sdk_action_plan":plan,
                "official_original_sdk_level":row["official_original_final_level"],
                "official_original_sdk_state":row["official_original_final_state"],
                "official_original_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "original_sdk_disposition":row["trial_disposition"],
                "true_original_source_failure_feedback":observed,
                "genuine_sdk_action_receipts":[
                    {k:v for k,v in ev.items() if k!="full_original_source_frame_ledger"}
                    for ev in row["full_original_sdk_action_events"]],
            }
            rows.append(receipt)
            for k,arr in stacks.items():
                actual_arrays[f"{case}_{witness}_{k}"]=arr
            print("ORIGINAL_SP80_FIRST_SPILL_LEDGER_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":receipt["official_original_sdk_level"],
                "official_state":receipt["official_original_sdk_state"],
                "native_source_readout":observed,
            },sort_keys=True),flush=True)
    if len(rows)!=30 or len(roots)!=1:
        raise AssertionError("Missing genuine independent original SDK entry witnesses")
    success=[{
        "case":r["predeclared_genuine_source_case"],
        "witness":r["independent_native_source_witness"],
        "word":r["genuine_original_sdk_action_plan"],
        "official_level":r["official_original_sdk_level"],
        "official_state":r["official_original_sdk_state"]}
        for r in rows if r["official_original_sdk_level4_or_WIN"]
    ]
    source_four_no_boundary=[
        {"case":r["predeclared_genuine_source_case"],"witness":r["independent_native_source_witness"]}
        for r in rows if r["true_original_source_failure_feedback"] is not None
        and r["true_original_source_failure_feedback"]["first_four_simultaneously_visual_cup_regions"] is not None
        and r["true_original_source_failure_feedback"]["no_tested_bottom_transition"]
    ]
    result={
        "kind":"ORIGINAL_SP80_STAGE3_FIRST_SPILL_CONTACT_AND_NATIVE_FEEDBACK",
        "authentic_sdk_antecedent_trial":39557791993,
        "original_sdk_reset_games":len(rows),
        "prospectively_frozen_source_words":FROZEN,
        "stage3_source_entry_blake2b16":next(iter(roots)),
        "official_level4_or_WIN_count":len(success),
        "actual_native_original_level_advances":success,
        "source_visual_four_cups_without_tested_boundary":source_four_no_boundary,
        "official_sdk_level_histogram":dict(Counter(str(r["official_original_sdk_level"]) for r in rows)),
        "official_sdk_state_histogram":dict(Counter(str(r["official_original_sdk_state"]) for r in rows)),
        "true_original_sdk_trial_receipts":rows,
        "limits":"Original source frames and official SDK levels/states are preserved. External guide describes blink cues but this test merely measures rendered pixel sequences; color 14 and palette13 not declared engine success or failure rule. Never infer physical mechanism or change any other research lane.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**actual_arrays)
    print("ORIGINAL_SP80_FIRST_SPILL_LEDGER_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("prospectively_frozen_source_words","true_original_sdk_trial_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
