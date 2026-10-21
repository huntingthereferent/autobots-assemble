"""Original SP80 SDK: move catcher LEFT toward x35..37 third-cup spill contact.

Native source run #39599565368 (PR #361) identified two independent
original ways to restore the visually missing THIRD cup at the
no-observed-boundary catcher right1/up3 threshold:
* linked middle right3: four cups by returned frame27, but original
  tested bottom boundary begins frame10 (new palette6 x23..25/y58);
* linked middle right4/up1: four cups by frame27, but source bottom
  begins frame28 (new palette6 x35..37/y58).
Every tested other-upper/selected-upper variant left cup3 empty.

A NEW selectable-bar relationship is now targeted: previously tested
bottom catcher right1 (actual source bbox x41..52) does not cover the
observed x35..37 late spill window; genuine source ACTION3 LEFT1 moves
that catcher to x35..46. Freeze mid-right3 / mid-right4-up1 source
parents, bottom catcher offsets -2,-1,0,+1 at measured up2..4
heights, and minimal receiving-bar controls. Use only original
Arcade(OperationMode.NORMAL) SDK, not invented liquid physics.
Only official SDK level>=4 or WIN means stage progress.
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

UPPER="6@20,18 4 4 2 6@40,18 2"
MID_RIGHT3="6@10,30 4 4 4"
MID_UP1="6@10,30 4 4 4 4 1"
MID_PARENT="6@10,30 4 4 4 4"
LOWER10="6@46,33 1 "+" ".join(["3"]*10)
LOWER9="6@46,33 1 "+" ".join(["3"]*9)
LOWER11="6@46,33 1 "+" ".join(["3"]*11)
CUPS=((8,16),(26,34),(38,46),(50,58))
SOURCE_ROWS=(19,26,29,32,35,41,47,52,56,58)

def catcher(offset,up):
    assert -2<=offset<=1 and 2<=up<=4
    horizontal=([3]*(-offset) if offset<0 else [4]*offset)
    return " ".join(["6@40,42",*map(str,horizontal+[1]*up)])

def program(mid,offset,up,receiver=LOWER10):
    return " ".join((UPPER,mid,receiver,catcher(offset,up),"5"))

MIDS=(("middle_right3",MID_RIGHT3),("middle_up1",MID_UP1))
FROZEN=(
    *(
        (f"{mid_name}_catcher_{'left'+str(-offset) if offset<0 else 'held' if offset==0 else 'right'+str(offset)}_up{height}",
         program(mid_word,offset,height))
        for mid_name,mid_word in MIDS
        for offset in (-1,0,1)
        for height in (2,3,4)
    ),
    ("clean_missing_third_parent",program(MID_PARENT,1,3)),
    ("dirty_parent_original",program(MID_PARENT,1,2)),
    ("middle_right3_left2_up3",program(MID_RIGHT3,-2,3)),
    ("middle_up1_left2_up3",program(MID_UP1,-2,3)),
    ("middle_right3_left1_up3_receiver_left9",program(MID_RIGHT3,-1,3,LOWER9)),
    ("middle_right3_left1_up3_receiver_left11",program(MID_RIGHT3,-1,3,LOWER11)),
    ("middle_up1_left1_up3_receiver_left9",program(MID_UP1,-1,3,LOWER9)),
    ("middle_up1_left1_up3_receiver_left11",program(MID_UP1,-1,3,LOWER11)),
)
assert len(FROZEN)==26==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(action==5 for action,xy in parse_plan(word))==1
    and len(parse_plan(word))<=38
    and all(xy is not None for action,xy in parse_plan(word) if action==6)
    for _,word in FROZEN
)

def segments(xs):
    xs=list(map(int,xs))
    if not xs:return []
    out=[];lo=hi=xs[0]
    for x in xs[1:]:
        if x>hi+1:
            out.append([lo,hi]);lo=x
        hi=x
    out.append([lo,hi])
    return out

def observed_native_pixels(pre,animation):
    if pre.shape!=(64,64) or animation.ndim!=3 or animation.shape[1:]!=(64,64):
        raise AssertionError("Original 64x64 SDK source arrays absent")
    first_full=[None]*4;all_four=None;max_full=0
    third_max=0;third_max_frame=None
    first_bottom=None;episodes=[];was_changed=False
    right_rows={str(y):None for y in SOURCE_ROWS}
    for t,frame in enumerate(animation):
        extra=(pre!=6)&(frame==6)
        for y in SOURCE_ROWS:
            xs=np.flatnonzero(extra[y])
            if right_rows[str(y)] is None and xs.size:
                right_rows[str(y)]={"native_frame":t,"new_palette6_x_intervals":segments(xs)}
        per_cup=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (frame[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for i,v in enumerate(per_cup):
            if v==45 and first_full[i] is None:first_full[i]=t
        if per_cup[2]>third_max:
            third_max=per_cup[2];third_max_frame=t
        n=sum(v==45 for v in per_cup)
        max_full=max(max_full,n)
        if n==4 and all_four is None:all_four=t
        change=pre[59:63,2:62]!=frame[59:63,2:62]
        active=bool(change.any())
        if active and not was_changed:episodes.append(t)
        was_changed=active
        if active and first_bottom is None:
            first_bottom={
                "native_frame":t,
                "actual_changed_source_bottom_pixels":int(change.sum()),
                "new_palette6_y56_x_intervals":segments(np.flatnonzero(extra[56])),
                "new_palette6_y58_x_intervals":segments(np.flatnonzero(extra[58])),
            }
    comps=[
        {"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and 14<=c["bbox"][1]<=54
    ]
    return {
        "source_true_prepour_blake2b16":hash_frame(pre),
        "source_true_pour_final_blake2b16":hash_frame(animation[-1]),
        "native_sdk_source_frame_count":len(animation),
        "actual_prepour_source_components":comps,
        "original_source_each_cup_first_full_frame":first_full,
        "native_source_third_cup_max_palette13_changed_pixels":third_max,
        "native_source_third_cup_max_frame":third_max_frame,
        "max_simultaneous_observed_full_cups":max_full,
        "original_first_all_four_observed_cups":all_four,
        "first_original_test_bottom_change":first_bottom,
        "source_bottom_change_episodes":episodes,
        "first_new_source_color6_at_rows":right_rows,
        "qualification":"Only SDK official level>=4/WIN is progress; source palette6 and cup palette13 are partial visual observations, not validated flow rules.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    receipts=[];original_source_stacks={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,frames=real_trial(witness,entry,case,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            pour=frames.get("stage3_"+str(n))
            pre=frames.get("stage3_"+str(n-1),frames["entry2_11"])[-1]
            measured=observed_native_pixels(pre,pour) if pour is not None else None
            rec={
                "prospectively_frozen_source_case":case,
                "true_independent_original_sdk_witness":witness,
                "actual_original_sdk_word":word,
                "native_official_final_level":sdk["official_original_final_level"],
                "native_official_final_state":sdk["official_original_final_state"],
                "original_sdk_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "native_original_sdk_disposition":sdk["trial_disposition"],
                "genuine_native_source_measurements":measured,
                "original_source_step_receipts":[
                    {k:v for k,v in x.items() if k!="full_original_source_frame_ledger"}
                    for x in sdk["original_stage3_intervention_events"]],
            }
            receipts.append(rec)
            for phase,arr in frames.items():
                original_source_stacks[f"{case}_{witness}_{phase}"]=arr
            print("ORIGINAL_SP80_LEFT_SHIFT_CATCHER_CASE "+json.dumps({
                "case":case,"witness":witness,
                "native_level":rec["native_official_final_level"],
                "native_state":rec["native_official_final_state"],
                "source_observations":measured,
            },sort_keys=True),flush=True)
    if len(receipts)!=52 or len(roots)!=1:
        raise AssertionError("Missing real original SDK independent reset witness")
    for case,_ in FROZEN:
        matched=[x for x in receipts if x["prospectively_frozen_source_case"]==case]
        if len(matched)!=2 or (
            matched[0]["native_official_final_level"]!=matched[1]["native_official_final_level"]
            or matched[0]["native_official_final_state"]!=matched[1]["native_official_final_state"]
            or matched[0]["genuine_native_source_measurements"]!=matched[1]["genuine_native_source_measurements"]
        ):
            raise AssertionError("Original native A/B source mismatch: "+case)
    gains=[
        {"case":r["prospectively_frozen_source_case"],"witness":r["true_independent_original_sdk_witness"],
         "word":r["actual_original_sdk_word"],"official_level":r["native_official_final_level"],
         "official_state":r["native_official_final_state"]}
        for r in receipts if r["original_sdk_level4_or_WIN"]
    ]
    four_no_bottom=[
        {"case":r["prospectively_frozen_source_case"],"witness":r["true_independent_original_sdk_witness"]}
        for r in receipts if r["genuine_native_source_measurements"] is not None
        and r["genuine_native_source_measurements"]["original_first_all_four_observed_cups"] is not None
        and r["genuine_native_source_measurements"]["first_original_test_bottom_change"] is None
    ]
    result={
        "kind":"TRUE_ORIGINAL_SP80_STAGE3_LEFT_CATCHER_THIRD_CUP_BRANCH",
        "original_antecedent_SDK_run":39599565368,
        "actual_independently_reset_original_games":len(receipts),
        "precommitted_native_words":FROZEN,
        "true_stage3_source_entry_blake2b16":next(iter(roots)),
        "native_actual_official_level4_or_WIN_count":len(gains),
        "genuine_original_sdk_advancement_cases":gains,
        "visual_four_cup_no_tested_boundary":four_no_bottom,
        "real_original_sdk_level_counts":dict(Counter(str(r["native_official_final_level"]) for r in receipts)),
        "real_original_sdk_state_counts":dict(Counter(str(r["native_official_final_state"]) for r in receipts)),
        "source_original_action_receipts":receipts,
        "limits":"Actual SDK level>=4/WIN is decisive. Original source pixel colors describe tested frames, not independently verified physics, spill condition or level rule. Full actual source arrays retained NPZ; other lanes/rights unchanged.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(a.out.with_suffix(".npz"),**original_source_stacks)
    print("ORIGINAL_SP80_LEFT_SHIFT_CATCHER_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("precommitted_native_words","source_original_action_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
