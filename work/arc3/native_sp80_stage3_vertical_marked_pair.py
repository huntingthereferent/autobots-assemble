"""Original SDK SP80 stage3: vertical transport of observed middle-spout pair.

Original native #39553891447 (76 genuine reset games) exhaustively tested
a bounded two-upper x three-mid-horizontal x three-lower x two-bottom
roster: no official level4. Horizontal changes shifted the earliest
boundary stream among source x5,17,23,35,59, without a four-cup &
no-bottom-change image. This trial tests a NEW movement dimension:
up/down and ordering of the native selected linked middle-spout pair.
The public game guide describes a spout on a movable bar (this is not a
private SDK engine, physics derivation, or predicted win predicate).
Native SDK only; one ACTION5 per independently reset original game.
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

UPPERS=(
    ("upper_selected_right2","6@20,18 4 4"),
    ("upper_other_left2","6@40,18 3 3"),
)
LOWER10="6@46,33 "+" ".join(["3"]*10)
BOTTOM2="6@40,42 4 4"
CUP_BINS=((8,16),(26,34),(38,46),(50,58))
DIRECTIONS=(
    ("up1",1,1),("up2",1,2),("up3",1,3),
    ("down1",2,1),("down2",2,2),("down3",2,3),
)

def middle(action,n,vertical_first):
    updown=" ".join([str(action)]*n)
    lateral="4 4 4 4"
    return "6@10,30 "+(" ".join([updown,lateral]) if vertical_first
                        else " ".join([lateral,updown]))

def word(upper,movement):
    return " ".join([upper,movement,LOWER10,BOTTOM2,"5"])

FROZEN=tuple(
    (f"{uname}_{dname}_{'verticalfirst' if first else 'horizontalfirst'}",
     word(uword,middle(direction,count,first)))
    for uname,uword in UPPERS
    for dname,direction,count in DIRECTIONS
    for first in (True,False)
)+(
    ("upper_selected_right2_horizontal_only",word(UPPERS[0][1],"6@10,30 4 4 4 4")),
    ("upper_other_left2_horizontal_only",word(UPPERS[1][1],"6@10,30 4 4 4 4")),
    ("no_upper_horizontal_only"," ".join(["6@10,30 4 4 4 4",LOWER10,BOTTOM2,"5"])),
)
assert len(FROZEN)==27==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(w)[-1][0]==5
    and sum(a==5 for a,_ in parse_plan(w))==1
    and len(parse_plan(w))<=32
    for _,w in FROZEN
)

def measure(pre,returned):
    if pre.shape!=(64,64):
        raise AssertionError("True original SDK pre-pour frame shape")
    fourth_frame=None;boundary_frame=None
    full_at=[None]*4;max_full=0
    for i,now in enumerate(returned):
        if now.shape!=pre.shape:
            raise AssertionError("Genuine original SDK return frame shape")
        per_cup=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&
                (now[53:59,lo:hi+1]==13)
            )) for lo,hi in CUP_BINS
        ]
        for j,v in enumerate(per_cup):
            if v==45 and full_at[j] is None:full_at[j]=i
        n=sum(v==45 for v in per_cup)
        max_full=max(max_full,n)
        if n==4 and fourth_frame is None:fourth_frame=i
        boundary=(pre[59:63,2:62]!=now[59:63,2:62])
        if boundary.any() and boundary_frame is None:
            boundary_frame={
                "source_animation_frame":i,
                "changed_source_bottom_test_pixels":int(boundary.sum()),
                "new_source_palette6_x_at_y58":[
                    int(x) for x in np.where(
                        (pre[58]!=6)&(now[58]==6)
                    )[0]
                ],
            }
    bands=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9)
        and 15<=c["bbox"][1]<=49
    ]
    return {
        "genuine_SDK_pre_pour_blake2b16":hash_frame(pre),
        "genuine_SDK_post_pour_blake2b16":hash_frame(returned[-1]),
        "all_original_source_4_8_9_pre_pour_components":bands,
        "original_SDK_animation_frame_count":len(returned),
        "first_source_simultaneous_four_cup_animation_frame":fourth_frame,
        "source_max_simultaneous_full_cups":max_full,
        "source_first_per_cup_full_frames":full_at,
        "observed_first_y59_62_bottom_change":boundary_frame,
        "no_observed_source_tested_bottom_change":boundary_frame is None,
        "limitation":"Source pixels and bboxes observed only, not decoded engine semantics or a success condition.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];raw_arrays={};roots=set()
    for name,program in FROZEN:
        length=len(parse_plan(program))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=real_trial(witness,entry,name,program)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            poured=stacks.get("stage3_"+str(length))
            before=stacks.get("stage3_"+str(length-1),stacks["entry2_11"])[-1]
            visual=measure(before,poured) if poured is not None else None
            record={
                "source_native_predeclared_trial":name,
                "source_independent_sdk_witness":witness,
                "authentic_original_sdk_word":program,
                "official_original_SDK_level":sdk["official_original_final_level"],
                "official_original_SDK_state":sdk["official_original_final_state"],
                "genuine_original_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "source_original_trial_disposition":sdk["trial_disposition"],
                "source_original_visual_measurements":visual,
                "actual_native_SDK_receipts":[
                    {k:v for k,v in ev.items() if k!="full_original_source_frame_ledger"}
                    for ev in sdk["full_original_sdk_action_events"]],
            }
            rows.append(record)
            for key,arr in stacks.items():
                raw_arrays[f"{name}_{witness}_{key}"]=arr
            print("ORIGINAL_SP80_VERTICAL_MID_SOURCE_CASE "+json.dumps({
                "case":name,"witness":witness,
                "level":record["official_original_SDK_level"],
                "state":record["official_original_SDK_state"],
                "visual":visual
            },sort_keys=True),flush=True)
    if len(rows)!=54 or len(roots)!=1:
        raise AssertionError("Independent original source SDK witnesses missing")
    gains=[
        {"case":r["source_native_predeclared_trial"],"witness":r["source_independent_sdk_witness"],
         "original_level":r["official_original_SDK_level"],"original_state":r["official_original_SDK_state"],
         "exact_original_native_word":r["authentic_original_sdk_word"]}
        for r in rows if r["genuine_original_level4_or_WIN"]
    ]
    visual_candidates=[
        {"case":r["source_native_predeclared_trial"],"witness":r["source_independent_sdk_witness"]}
        for r in rows if r["source_original_visual_measurements"] is not None
        and r["source_original_visual_measurements"]["source_max_simultaneous_full_cups"]==4
        and r["source_original_visual_measurements"]["no_observed_source_tested_bottom_change"]
    ]
    summary={
        "kind":"REAL_ORIGINAL_SP80_STAGE3_MARKED_SPOUT_VERTICAL_MOVEMENT_CONTRAST",
        "original_source_antecedent_native_runs":[39552468947,39553167522,39553891447],
        "independent_original_SDK_reset_games":len(rows),
        "prospectively_fixed_native_words":FROZEN,
        "verified_original_stage3_source_root_blake2b16":next(iter(roots)),
        "official_original_level4_or_WIN_count":len(gains),
        "genuine_source_level_advancement_witnesses":gains,
        "visual_only_four_full_no_test_bottom_change":visual_candidates,
        "official_original_level_histogram":dict(Counter(str(r["official_original_SDK_level"]) for r in rows)),
        "official_original_state_histogram":dict(Counter(r["official_original_SDK_state"] for r in rows)),
        "genuine_original_SDK_records":rows,
        "limits":"Only source SDK official levels>=4 / WIN proves advancement. Palette observations, two-spout labels and tested boundary pixels do not define a complete goal or external physical process. All source returned 64x64 NPZ frames retained, other lanes and rights unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_arrays)
    print("ORIGINAL_SP80_VERTICAL_MID_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_fixed_native_words","genuine_original_SDK_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
