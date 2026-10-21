"""Native original SP80 stage3: first-arrival contrast between 3 and 4 cups.

The five actual source selection classes and last-selection response
invariance were tested in runs #39560629170 and #39561674357. Further
late clicks will not alter the observed source pour for a fixed scene.

This finite original SDK experiment compares the *first* source
palette6 appearance in each pixel of full returned genuine ACTION5
animation, using pre-pour source frames as baselines. Crucially it
compares an original three-cup/no-bottom-change parent with its
four-cup/bottom-change sibling and two measured lower bar placements.
It reports earliest observed native differences, not inferred water
physics, causality or an engine clone. Only native level4/WIN counts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

SELECTED="6@20,18 4 4 2"
OTHER="6@40,18 2"
MIDDLE="6@10,30 4 4 4 4"
LOWER10="6@46,33 "+" ".join(["3"]*10)
LOWER9="6@46,33 "+" ".join(["3"]*9)
LOWER11="6@46,33 "+" ".join(["3"]*11)
LOWER_UP10="6@46,33 1 "+" ".join(["3"]*10)
BOTTOM1="6@40,42 4"
BOTTOM2="6@40,42 4 4"
CUPS=((8,16),(26,34),(38,46),(50,58))
ROWS=(7,16,19,26,29,35,41,47,52,56,58)

def plan(other,lower,bottom):
    return " ".join(v for v in (SELECTED,other,MIDDLE,lower,bottom,"5") if v)

FROZEN=(
    ("clean_three_cups",plan("",LOWER10,BOTTOM2)),
    ("four_cups_right_boundary",plan(OTHER,LOWER10,BOTTOM2)),
    ("four_cups_late_center_boundary",plan(OTHER,LOWER_UP10,BOTTOM1)),
    ("four_cups_early_left_boundary",plan(OTHER,LOWER9,BOTTOM2)),
    ("four_cups_early_farleft_boundary",plan(OTHER,LOWER11,BOTTOM2)),
    ("clean_three_cups_lower_up",plan("",LOWER_UP10,BOTTOM2)),
)
PAIRS=(
    ("clean_three_cups","four_cups_right_boundary"),
    ("four_cups_right_boundary","four_cups_late_center_boundary"),
    ("four_cups_right_boundary","four_cups_early_left_boundary"),
    ("four_cups_right_boundary","four_cups_early_farleft_boundary"),
    ("clean_three_cups","clean_three_cups_lower_up"),
)
assert len(FROZEN)==6==len(set(name for name,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(w)[-1][0]==5 and
    sum(a==5 for a,xy in parse_plan(w))==1 and
    len(parse_plan(w))<=36 for name,w in FROZEN
)

def intervals(xs):
    x=list(map(int,xs))
    if not x:return []
    output=[];lo=hi=x[0]
    for value in x[1:]:
        if value>hi+1:
            output.append([lo,hi]);lo=value
        hi=value
    output.append([lo,hi])
    return output

def original_first_arrivals(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Expected original SDK source frames")
    arrivals=np.full(pre.shape,-1,dtype=np.int16)
    four_frame=None;bottom_frame=None
    cup_first=[None]*4
    observed_row_arrivals={str(r):None for r in ROWS}
    bottom_episodes=[];prev_bottom=False
    for t,frame in enumerate(frames):
        native_new=(pre!=6)&(frame==6)
        first=native_new&(arrivals<0)
        arrivals[first]=t
        for r in ROWS:
            if observed_row_arrivals[str(r)] is None and native_new[r].any():
                observed_row_arrivals[str(r)]={
                    "frame":t,
                    "genuine_source_color6_new_x_intervals":intervals(np.flatnonzero(native_new[r])),
                }
        cup_counts=[
            int(np.count_nonzero(
                (pre[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUPS
        ]
        for j,v in enumerate(cup_counts):
            if v==45 and cup_first[j] is None:cup_first[j]=t
        if four_frame is None and all(v==45 for v in cup_counts):
            four_frame=t
        changed=(pre[59:63,2:62]!=frame[59:63,2:62]).any()
        if changed and bottom_frame is None:bottom_frame=t
        if changed and not prev_bottom:bottom_episodes.append(t)
        prev_bottom=bool(changed)
    return arrivals,{
        "original_prepour_blake2b16":hash_frame(pre),
        "original_final_after_pour_blake2b16":hash_frame(frames[-1]),
        "native_animation_frames":len(frames),
        "first_source_color6_at_rows":observed_row_arrivals,
        "source_cups_first_full_visual_frame":cup_first,
        "first_four_simultaneous_visual_cups":four_frame,
        "original_first_bottom_test_change":bottom_frame,
        "actual_bottom_test_change_episodes":bottom_episodes,
        "source_new_color6_ever_pixel_count":int(np.count_nonzero(arrivals>=0)),
    }

def compare(name_a,name_b,witnesses,arrays):
    results=[]
    for w in witnesses:
        a=arrays[(name_a,w)]
        b=arrays[(name_b,w)]
        only_b=(a<0)&(b>=0)
        only_a=(b<0)&(a>=0)
        common=(a>=0)&(b>=0)
        differences=common&(a!=b)
        b_arrivals=b[only_b]
        a_arrivals=a[only_a]
        # Native timeline differences are direct comparisons of observed
        # source palette6 appearance, NOT routes or causes.
        first_b=int(b_arrivals.min()) if b_arrivals.size else None
        first_a=int(a_arrivals.min()) if a_arrivals.size else None
        b_first_yx=[]
        if first_b is not None:
            ys,xs=np.nonzero(only_b&(b==first_b))
            b_first_yx=[[int(y),int(x)] for y,x in zip(ys,xs)][:100]
        timeline=[
            {"y":int(row),
             "source_A":intervals(np.flatnonzero(a[row]>=0)),
             "source_B":intervals(np.flatnonzero(b[row]>=0)),
             "source_only_B":intervals(np.flatnonzero(only_b[row])),
             "source_only_A":intervals(np.flatnonzero(only_a[row]))}
            for row in ROWS
        ]
        results.append({
            "original_independent_sdk_witness":w,
            "first_native_new_palette6_only_in_B_frame":first_b,
            "first_native_new_palette6_only_in_A_frame":first_a,
            "first_B_only_pixel_yx_samples":b_first_yx,
            "native_new_source_color6_only_B_pixel_count":int(only_b.sum()),
            "native_new_source_color6_only_A_pixel_count":int(only_a.sum()),
            "shared_source_color6_pixels_with_changed_arrival_time":int(differences.sum()),
            "actual_observed_row_occupancy_comparison":timeline,
        })
    if results[0]["first_native_new_palette6_only_in_B_frame"]!=results[1]["first_native_new_palette6_only_in_B_frame"]:
        raise AssertionError("Independent original native first differences mismatch")
    return {"original_source_A":name_a,"original_source_B":name_b,"independent_native_results":results}

def self_test():
    assert intervals([])==[]
    assert intervals([3,4,8,10,11])==[[3,4],[8,8],[10,11]]
    image=np.zeros((64,64),dtype=np.uint8)
    frames=np.stack((image.copy(),image.copy()))
    frames[1,19,10:13]=6
    a,b=original_first_arrivals(image,frames)
    assert a[19,10]==1 and a[18,10]==-1
    assert b["first_source_color6_at_rows"]["19"]["frame"]==1

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    self_test()
    original_raw={};arrivals={};rows=[];roots=set()
    for name,word in FROZEN:
        count=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=real_trial(witness,entry,name,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            animation=stacks.get("stage3_"+str(count))
            before=stacks.get("stage3_"+str(count-1),stacks["entry2_11"])[-1]
            arrival,metrics=original_first_arrivals(before,animation)
            arrivals[(name,witness)]=arrival
            row={
                "precommitted_original_source_case":name,
                "true_native_independent_witness":witness,
                "genuine_sdk_original_action_word":word,
                "official_original_final_level":sdk["official_original_final_level"],
                "official_original_final_state":sdk["official_original_final_state"],
                "native_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "actual_original_source_observations":metrics,
                "actual_original_sdk_receipts":[
                    {k:v for k,v in ev.items() if k!="full_original_source_frame_ledger"}
                    for ev in sdk["original_stage3_intervention_events"]],
            }
            rows.append(row)
            for phase,frame in stacks.items():
                original_raw[f"{name}_{witness}_{phase}"]=frame
            original_raw[f"{name}_{witness}_first_arrival"]=arrival
            print("ORIGINAL_SP80_FIRST_ARRIVAL_CASE "+json.dumps({
                "case":name,"witness":witness,
                "official_level":row["official_original_final_level"],
                "official_state":row["official_original_final_state"],
                "source":metrics,
            },sort_keys=True),flush=True)
    if len(rows)!=12 or len(roots)!=1:
        raise AssertionError("Missing independent genuine original SDK entries")
    comparisons=[
        compare(a,b,("A","B"),arrivals) for a,b in PAIRS
    ]
    progress=[{"case":r["precommitted_original_source_case"],
               "witness":r["true_native_independent_witness"]}
              for r in rows if r["native_level4_or_WIN"]]
    summary={
        "kind":"GENUINE_SP80_STAGE3_FIRST_SOURCE_ARRIVAL_CONTRAST",
        "original_antecedent_runs":[39560629170,39561674357],
        "authentic_native_sdk_independent_resets":len(rows),
        "fixed_original_source_words":FROZEN,
        "verified_original_sdk_stage3_root_blake2b16":next(iter(roots)),
        "native_official_level4_or_WIN_count":len(progress),
        "native_true_level4_witnesses":progress,
        "original_source_level_histogram":dict(Counter(str(r["official_original_final_level"]) for r in rows)),
        "original_source_state_histogram":dict(Counter(str(r["official_original_final_state"]) for r in rows)),
        "independently_reproduced_original_source_first_arrival_contrasts":comparisons,
        "native_source_full_receipts":rows,
        "limits":"A first color6 appearance records original source pixels, not a physical causal edge or independently verified leak cause. Only native SDK official level>=4/WIN proves game progression. Raw actual frame and pixel arrival arrays retained.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**original_raw)
    print("ORIGINAL_SP80_FIRST_ARRIVAL_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("fixed_original_source_words","native_source_full_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
