"""Original SP80 stage3: source x59..61 late-boundary catcher trial.

Genuine native original SDK source run #39552468947 (raw NPZ artifact
#12323963933 independently inspected): two distinct four-cup screen
configurations produce four simultaneous observed palette11->13 cup
region changes at animation frame29. Then on frame30 native palette6
appears at x59..61,y58 and all 180 bottom y59..62 test pixels change
from source palette1 to14. All original SDK outcomes still level3.
This is source timing/position, NOT a decoded fluid rule or leak cause.

Move only preexisting original bottom bar at original click (40,42) to
test interception near that genuine later x59..61 stream. One native
ACTION5 per newly reset genuine Arcade.NORMAL SP80 game.
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

UPPER_SELECTED_RIGHT2="6@20,18 4 4"
UPPER_OTHER_LEFT2="6@40,18 3 3"
MID4="6@10,30 4 4 4 4"
LOWER10="6@46,33 "+" ".join(["3"]*10)
CUP_RANGES=((8,16),(26,34),(38,46),(50,58))

def bottom(right,down,vertical_first=False):
    if not (2<=right<=5 and 0<=down<=5):
        raise AssertionError("Non-frozen right-edge candidate")
    steps=([2]*down+[4]*right) if vertical_first else ([4]*right+[2]*down)
    return "6@40,42 "+" ".join(map(str,steps))

def source_word(upper,right,down=0,vertical_first=False):
    return " ".join([upper,MID4,LOWER10,bottom(right,down,vertical_first),"5"])

# Prospectively defined from the independent original source x59..61
# observation; stage3 goal is NOT hardcoded or assumed.
FROZEN=tuple(
    [(f"selected_right2_bottom_r{r}",source_word(UPPER_SELECTED_RIGHT2,r)) for r in (2,3,4,5)]
    +[(f"other_left2_bottom_r{r}",source_word(UPPER_OTHER_LEFT2,r)) for r in (2,3,4,5)]
    +[(f"selected_bottom_r4_d{d}",source_word(UPPER_SELECTED_RIGHT2,4,d)) for d in (1,2,3,4,5)]
    +[(f"selected_bottom_r5_d{d}",source_word(UPPER_SELECTED_RIGHT2,5,d)) for d in (1,2,3,4)]
    +[(f"selected_bottom_r3_d{d}",source_word(UPPER_SELECTED_RIGHT2,3,d)) for d in (2,4)]
    +[(f"other_bottom_r4_d{d}",source_word(UPPER_OTHER_LEFT2,4,d)) for d in (1,2,3,4)]
    +[(f"other_bottom_r5_d{d}",source_word(UPPER_OTHER_LEFT2,5,d)) for d in (2,4)]
    +[(f"selected_downfirst_d{d}_r4",source_word(UPPER_SELECTED_RIGHT2,4,d,True)) for d in (2,4)]
    +[("other_downfirst_d3_r4",source_word(UPPER_OTHER_LEFT2,4,3,True))]
)
assert len(FROZEN)==28==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=38
    for _,word in FROZEN
)

def native_pixels(pre,stack):
    if pre.shape!=(64,64):
        raise AssertionError("Source pre-pour frame shape")
    edge_first=None;four_first=None
    each_cup=[None]*4;max_four=0
    for t,f in enumerate(stack):
        if f.shape!=pre.shape:
            raise AssertionError("Original SDK return frame shape")
        counts=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (f[53:59,lo:hi+1]==13)))
            for lo,hi in CUP_RANGES
        ]
        for i,v in enumerate(counts):
            if v==45 and each_cup[i] is None:each_cup[i]=t
        four=sum(v==45 for v in counts)
        max_four=max(max_four,four)
        if four==4 and four_first is None:four_first=t
        before=pre[59:63,2:62];after=f[59:63,2:62]
        change=before!=after
        if edge_first is None and np.any(change):
            values,qty=np.unique(np.stack([before[change],after[change]],axis=1),axis=0,return_counts=True)
            edge_first={
                "original_animation_frame":t,
                "original_bottom_test_pixel_change_count":int(change.sum()),
                "source_palette_transitions":[
                    {"before_palette":int(p[0]),"after_palette":int(p[1]),
                     "count":int(n)} for p,n in zip(values,qty)
                ],
                "new_original_palette6_x_at_y58":[
                    int(i) for i in np.where((pre[58]!=6)&(f[58]==6))[0]
                ],
            }
    regions=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (8,9) and c["bbox"][1]>=15 and c["bbox"][1]<=55
    ]
    return {
        "pre_native_sdk_frame_blake2b16":hash_frame(pre),
        "post_native_sdk_frame_blake2b16":hash_frame(stack[-1]),
        "original_sdk_animation_frame_count":len(stack),
        "native_original_pre_pour_selected_region_bboxes":regions,
        "original_source_first_bottom_boundary_change":edge_first,
        "observed_bottom_boundary_unchanged_through_all_returned_frames":edge_first is None,
        "first_simultaneous_four_cup_region_frame":four_first,
        "first_full_change_frames_for_four_original_cups":each_cup,
        "maximum_simultaneously_changed_source_cup_regions":max_four,
        "bounds":"Source returned pixel metrics ONLY; neither a leak detector nor objective rule.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    receipts=[];arrays={};roots=set()
    for name,word in FROZEN:
        n=len(parse_plan(word))
        for witness,stage1_word in STAGE1_WITNESSES:
            row,stacks=real_trial(witness,stage1_word,name,word)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            last=stacks.get("stage3_"+str(n))
            prior=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            reading=native_pixels(prior,last) if last is not None else None
            record={
                "frozen_original_native_candidate":name,
                "original_independent_game_witness":witness,
                "true_original_sdk_stage3_word":word,
                "real_sdk_final_level":row["official_original_final_level"],
                "real_sdk_final_state":row["official_original_final_state"],
                "real_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "source_trial_disposition":row["trial_disposition"],
                "true_original_native_source_observations":reading,
                "genuine_original_sdk_action_events":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in row["full_original_sdk_action_events"]
                ],
            }
            receipts.append(record)
            for k,a in stacks.items():arrays[f"{name}_{witness}_{k}"]=a
            print("ORIGINAL_SP80_RIGHT_EDGE_CASE "+json.dumps({
                "case":name,"witness":witness,
                "official_level":record["real_sdk_final_level"],
                "official_state":record["real_sdk_final_state"],
                "source_reading":reading,
            },sort_keys=True),flush=True)
    if len(receipts)!=56 or len(roots)!=1:
        raise AssertionError("Original SDK independent witnesses or source root differ")
    successes=[{
        "case":r["frozen_original_native_candidate"],
        "witness":r["original_independent_game_witness"],
        "original_level":r["real_sdk_final_level"],
        "original_state":r["real_sdk_final_state"],
        "word":r["true_original_sdk_stage3_word"]
        } for r in receipts if r["real_sdk_level4_or_WIN"]
    ]
    observed_no_edge_and_four=[
        {"case":r["frozen_original_native_candidate"],"witness":r["original_independent_game_witness"]}
        for r in receipts if r["true_original_native_source_observations"] is not None
        and r["true_original_native_source_observations"]["observed_bottom_boundary_unchanged_through_all_returned_frames"]
        and r["true_original_native_source_observations"]["maximum_simultaneously_changed_source_cup_regions"]==4
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_RIGHT_EDGE_SOURCE_CATCH",
        "antecedent_actual_native_run":39552468947,
        "antecedent_original_raw_artifact":12323963933,
        "original_sdk_independent_reset_games":len(receipts),
        "prospective_original_sdk_native_words":FROZEN,
        "original_source_stage3_root_blake2b16":next(iter(roots)),
        "official_native_level4_or_WIN_count":len(successes),
        "official_actual_native_advances":successes,
        "source_observed_four_cup_no_bottom_boundary_cases":observed_no_edge_and_four,
        "official_native_level_histogram":dict(Counter(str(r["real_sdk_final_level"]) for r in receipts)),
        "official_native_state_histogram":dict(Counter(r["real_sdk_final_state"] for r in receipts)),
        "true_original_sdk_source_records":receipts,
        "boundary":"Only official original SDK levels>=4 or WIN prove progression. A visually clean bottom y59-62 interval does not prove no spill; four changed cups do not prove a win. No new engine or private source imitation; other lanes and rights untouched.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_RIGHT_EDGE_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospective_original_sdk_native_words","true_original_sdk_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
