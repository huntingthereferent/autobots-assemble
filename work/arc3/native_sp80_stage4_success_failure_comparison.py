"""Contrast true SP80 level3->4 SDK success against level4 nonprogress.

Original arcade NORMAL SDK replays the complete verified level0..3 entry.
Two frozen level4 pour controls use identical original stage3 successful
transition; all return 64x64 source stacks, original SDK receipts and NPZ.
No assertion that matching palette counts imply the same private rule.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case, STAGE3_WINNER
from .native_sp80_stage4_lower_L_boundary import LOWER, UPPER_POUR
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_stage4_top_left_source_contrast import CUPS

FROZEN=(
    ("four_cup_transient", " ".join((LOWER,UPPER_POUR))),
    ("three_cup_negative", " ".join((LOWER,"3",UPPER_POUR))),
)

def frame_signature(pre,stack,after_receipt):
    if pre.shape!=(64,64) or stack.ndim!=3 or stack.shape[1:]!=(64,64) or len(stack)<2:
        raise AssertionError("Expected actual original returned SDK stack of 64x64")
    counts=[]
    for f in stack:
        colors=dict(Counter(str(int(c)) for c in np.asarray(f).ravel()))
        counts.append({
            "palette13":int(np.count_nonzero(f==13)),
            "palette14":int(np.count_nonzero(f==14)),
            "changed_from_pre":int(np.count_nonzero(f!=pre)),
            "changed_from_previous":None,
            "hash":hash_frame(f),
        })
    for i in range(1,len(counts)):
        counts[i]["changed_from_previous"]=int(np.count_nonzero(stack[i]!=stack[i-1]))
    last=stack[-1]
    pos=np.argwhere(last!=pre)
    return {
        "original_action_receipt":{
            "phase":after_receipt["phase"],
            "genuine_original_action":after_receipt["genuine_original_action"],
            "sdk_level_before":after_receipt["original_sdk_level_before"],
            "sdk_level_after":after_receipt["original_sdk_level_after"],
            "sdk_state_before":after_receipt["original_sdk_state_before"],
            "sdk_state_after":after_receipt["original_sdk_state_after"],
            "returned_frames":after_receipt["original_sdk_frame_stack_count"],
        },
        "source_stack_frames":len(stack),
        "source_prepour_hash":hash_frame(pre),
        "native_returned_final_hash":hash_frame(last),
        "native_final_vs_prepour_pixel_count":int(np.count_nonzero(last!=pre)),
        "native_final_vs_prepour_bbox_xyxy":([int(pos[:,1].min()),int(pos[:,0].min()),
                                              int(pos[:,1].max()),int(pos[:,0].max())] if len(pos) else None),
        "source_frame_signatures":counts,
        "last_two_palette13":[counts[-2]["palette13"],counts[-1]["palette13"]],
        "last_two_changed_from_previous":[counts[-2]["changed_from_previous"],counts[-1]["changed_from_previous"]],
    }

def stage4_cups(root,stack):
    observations={}
    for label,(x0,y0,x1,y1) in CUPS.items():
        mask=root[y0:y1+1,x0:x1+1]==11
        if int(mask.sum())!=45:raise AssertionError("Authentic stage4 45px root mask missing")
        counts=[int(np.count_nonzero(mask & (f[y0:y1+1,x0:x1+1]==13))) for f in stack]
        observations[label]={
            "native_first_full":next((i for i,v in enumerate(counts) if v==45),None),
            "native_last_full":next((i for i in range(len(counts)-1,-1,-1) if counts[i]==45),None),
            "source_last_two_cup_palette13":[counts[-2],counts[-1]],
        }
    return observations

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    native_rows=[];stacks={};root_hashes=set()
    n3=len(parse_plan(STAGE3_WINNER))
    if n3!=34:raise AssertionError("Frozen independently verified original stage3 word changed")
    for condition,word in FROZEN:
        n4=len(parse_plan(word))
        if parse_plan(word)[-1][0]!=5:raise AssertionError("Native stage4 should end on actual ACTION5")
        for witness,entry in STAGE1_WITNESSES:
            native,frames=run_case(condition,witness,entry,word)
            receipts=native["full_native_stage4_entry_receipts"]["entry3"]
            winning_receipt=receipts[-1]
            stage3_pre=frames["entry3_"+str(n3-1)][-1]
            success_frames=frames["entry3_"+str(n3)]
            stage4_root=success_frames[-1]
            stage4_pre=frames["stage4_"+str(n4-1)][-1]
            failure_frames=frames["stage4_"+str(n4)]
            stage4_receipt=native["genuine_original_stage4_action_ledger"][-1]
            if (winning_receipt["original_sdk_level_before"],
                winning_receipt["original_sdk_level_after"],
                winning_receipt["genuine_original_action"])!=(3,4,5):
                raise AssertionError("Source SDK level3->4 success absent")
            if (stage4_receipt["original_sdk_level_before"],
                stage4_receipt["original_sdk_level_after"],
                stage4_receipt["genuine_original_action"])!=(4,4,5):
                raise AssertionError("Expected actual stage4 nonadvance ACTION5")
            if hash_frame(stage4_root)!=native["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"]:
                raise AssertionError("Successful original stage3 terminal frame is not native stage4 entrance")
            root_hashes.add(hash_frame(stage4_root))
            positive=frame_signature(stage3_pre,success_frames,winning_receipt)
            negative=frame_signature(stage4_pre,failure_frames,stage4_receipt)
            row={
                "condition":condition,"witness":witness,
                "genuine_stage3_success":positive,
                "genuine_stage4_nonadvance":negative,
                "same_original_sdk_level4_root":hash_frame(stage4_root),
                "source_stage4_cups":stage4_cups(stage4_root,failure_frames),
                "actual_original_final_level":native["true_original_sdk_final_level"],
                "actual_original_final_state":native["true_original_sdk_final_state"],
                "source_stage3_success_terminal_equals_stage4_entry":True,
            }
            native_rows.append(row)
            for key,frame in frames.items():stacks[condition+"_"+witness+"_"+key]=frame
            print("ARC4_SUCCESS_FAILURE_PAIR "+json.dumps({
                "condition":condition,"witness":witness,
                "actual_stage3_sdk_transition":[3,4],
                "actual_stage4_sdk_transition":[4,4],
                "success_last_two_palette13":positive["last_two_palette13"],
                "nonadvance_last_two_palette13":negative["last_two_palette13"],
                "success_native_frames":positive["source_stack_frames"],
                "nonadvance_native_frames":negative["source_stack_frames"],
                "final_success_hash":positive["native_returned_final_hash"],
                "final_nonadvance_hash":negative["native_returned_final_hash"],
            },sort_keys=True),flush=True)
    if len(root_hashes)!=1 or len(native_rows)!=4:raise AssertionError("Independent SDK native root mismatch")
    for condition,_ in FROZEN:
        pair=[z for z in native_rows if z["condition"]==condition]
        if len(pair)!=2 or {z["witness"] for z in pair}!={"A","B"}:
            raise AssertionError("Original SDK two entrance witnesses missing")
        for key in ("genuine_stage3_success","genuine_stage4_nonadvance","source_stage4_cups",
                    "same_original_sdk_level4_root","actual_original_final_level","actual_original_final_state"):
            if pair[0][key]!=pair[1][key]:raise AssertionError("Genuine SDK witness source disagreement "+condition+"."+key)
    report={
        "kind":"SP80_ORIGINAL_SDK_CONFIRMED_LEVEL3_SUCCESS_VS_LEVEL4_NONADVANCE",
        "original_native_resets":len(native_rows),
        "successful_stage3_to4_events":len(native_rows),
        "unsuccessful_stage4_to5_events":len(native_rows),
        "original_level4_source_root":next(iter(root_hashes)),
        "frozen_comparison_cases":FROZEN,
        "native_original_source_rows":native_rows,
        "boundary":"Only the level3->4 ACTION5 is an observed official success. Source animation resets/cup colors cannot themselves decode the level4 win condition.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("ARC4_SUCCESS_FAILURE_SUMMARY "+json.dumps({
       "original_native_resets":len(native_rows),
       "native_stage3_to4_successes":len(native_rows),
       "native_stage4_to5_advances":0,
       "original_level4_root":next(iter(root_hashes)),
       "cases":{n:{
           "stage3_success_last_two_palette13":next(z["genuine_stage3_success"]["last_two_palette13"] for z in native_rows if z["condition"]==n),
           "stage4_nonadvance_last_two_palette13":next(z["genuine_stage4_nonadvance"]["last_two_palette13"] for z in native_rows if z["condition"]==n),
           "stage3_success_terminal_pixel_hash":next(z["genuine_stage3_success"]["native_returned_final_hash"] for z in native_rows if z["condition"]==n),
           "stage4_nonadvance_terminal_pixel_hash":next(z["genuine_stage4_nonadvance"]["native_returned_final_hash"] for z in native_rows if z["condition"]==n),
           "stage4_cups":next(z["source_stage4_cups"] for z in native_rows if z["condition"]==n),
           "native_stage3_success_animation_frames":next(z["genuine_stage3_success"]["source_stack_frames"] for z in native_rows if z["condition"]==n),
           "native_stage4_nonadvance_animation_frames":next(z["genuine_stage4_nonadvance"]["source_stack_frames"] for z in native_rows if z["condition"]==n),
           } for n,_ in FROZEN}
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
