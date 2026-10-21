"""One-pour source-native SP80 level3 intervention at observed early boundary path.

Original source NPZ from CI run #39549622886: in the four-cup case
'mid4_bottom_right1', the first bottom-boundary palette1->14 source change
is native animation frame 22, preceding the frame 27 simultaneous cup4
palette11->13 display. At first boundary, source liquid-colored pixels
occur around x17..19,y56..58. This is an OBSERVED target, not a decoded
causal leak law. Test longer movements of an EXISTING original lower bar
to intercept that region upstream, keeping other original pieces fixed.

No guessed objects, new engine, proxy success or hidden physics. The SDK's
levels_completed>=4 or WIN is the only accepted level advancement.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_stage2_source_map import color_components
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

MIDDLE4="6@10,30 4 4 4 4"
BOTTOM_RIGHT1="6@40,42 4"

def bar(down,left):
    return "6@46,33 " + " ".join(["2"]*down+["3"]*left)

def program(*args):
    return " ".join([*args,"5"])

# Frozen prospective source contrasts. Matching the target x17..19
# requires ~nine original source ACTION3 steps for the starting lower
# bar at x44..55; actual movement may be blocked, and is measured.
FROZEN=(
    ("unchanged_lower_bar",program(MIDDLE4,BOTTOM_RIGHT1)),
    ("lower_left6",program(MIDDLE4,bar(0,6),BOTTOM_RIGHT1)),
    ("lower_left8",program(MIDDLE4,bar(0,8),BOTTOM_RIGHT1)),
    ("lower_left9",program(MIDDLE4,bar(0,9),BOTTOM_RIGHT1)),
    ("lower_left10",program(MIDDLE4,bar(0,10),BOTTOM_RIGHT1)),
    ("lower_down1_left6",program(MIDDLE4,bar(1,6),BOTTOM_RIGHT1)),
    ("lower_down1_left8",program(MIDDLE4,bar(1,8),BOTTOM_RIGHT1)),
    ("lower_down1_left9",program(MIDDLE4,bar(1,9),BOTTOM_RIGHT1)),
    ("lower_down1_left10",program(MIDDLE4,bar(1,10),BOTTOM_RIGHT1)),
    ("lower_down2_left8",program(MIDDLE4,bar(2,8),BOTTOM_RIGHT1)),
    ("lower_down2_left9",program(MIDDLE4,bar(2,9),BOTTOM_RIGHT1)),
    ("lower_down2_left10",program(MIDDLE4,bar(2,10),BOTTOM_RIGHT1)),
    ("lower_down3_left8",program(MIDDLE4,bar(3,8),BOTTOM_RIGHT1)),
    ("lower_down3_left9",program(MIDDLE4,bar(3,9),BOTTOM_RIGHT1)),
    ("lower_down3_left10",program(MIDDLE4,bar(3,10),BOTTOM_RIGHT1)),
    ("upper_left1_lower_down1_left9",program("6@20,18 3",MIDDLE4,bar(1,9),BOTTOM_RIGHT1)),
    ("upper_left2_lower_down1_left9",program("6@20,18 3 3",MIDDLE4,bar(1,9),BOTTOM_RIGHT1)),
    ("upper_right1_lower_down1_left9",program("6@20,18 4",MIDDLE4,bar(1,9),BOTTOM_RIGHT1)),
)
assert len(FROZEN)==18==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(word))<=24
    and parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    for _,word in FROZEN
)
CUPS=((8,16),(26,34),(38,46),(50,58))

def source_frames(pre, frames):
    if pre.shape!=(64,64):
        raise AssertionError("Original SDK frame shape changed")
    first_border=None;first_all4=None;seen_cups=[None]*4
    first_border_colors=[]
    max_cups=0
    for t,f in enumerate(frames):
        if f.shape!=pre.shape:
            raise AssertionError("Original SDK returned frame shape changed")
        hits=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (f[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for j,v in enumerate(hits):
            if v==45 and seen_cups[j] is None:seen_cups[j]=t
        full=sum(v==45 for v in hits)
        max_cups=max(max_cups,full)
        if full==4 and first_all4 is None:first_all4=t
        orig=pre[59:63,2:62];now=f[59:63,2:62]
        changed=orig!=now
        if first_border is None and np.any(changed):
            first_border=t
            transitions=Counter(zip(orig[changed].tolist(),now[changed].tolist()))
            first_border_colors=[
                {"actual_source_before_palette":int(a),"actual_source_after_palette":int(b),
                 "pixel_count":count}
                for (a,b),count in sorted(transitions.items())
            ]
    pre_components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (8,9) and c["bbox"][1]>=20 and c["bbox"][1]<=44
    ]
    stream_at_first=None
    if first_border is not None:
        frame=frames[first_border]
        stream_at_first=int(np.count_nonzero(
            (pre[56:59,17:20]!=6)&(frame[56:59,17:20]==6)
        ))
    return {
        "actual_original_pre_pour_frame_blake2b16":hash_frame(pre),
        "actual_original_final_pour_frame_blake2b16":hash_frame(frames[-1]),
        "source_frame_count":len(frames),
        "original_source_pre_pour_selectable_region_boxes":pre_components,
        "observed_first_bottom_boundary_change_frame":first_border,
        "original_palette_changes_at_first_boundary":first_border_colors,
        "first_simultaneous_four_cup_palette_change_frame":first_all4,
        "first_change_frame_per_original_cup_region":seen_cups,
        "source_cup_regions_ever_simultaneously_changed":max_cups,
        "source_palette6_at_early_x17_19_bottom_when_boundary_first_changed":stream_at_first,
        "source_timing_only_not_goal_or_leak_ontology":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    records=[];original_arrays={};roots=set()
    for name,word in FROZEN:
        count=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            row,stacks=real_trial(witness,entry,name,word)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            result=stacks.get("stage3_"+str(count))
            last=stacks.get("stage3_"+str(count-1),stacks["entry2_11"])[-1]
            metrics=source_frames(last,result) if result is not None else None
            record={
                "original_frozen_control":name,
                "genuine_independent_native_witness":witness,
                "source_action_word":word,
                "real_original_sdk_level":row["official_original_final_level"],
                "real_original_sdk_state":row["official_original_final_state"],
                "real_original_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "real_original_sdk_trial_disposition":row["trial_disposition"],
                "original_sdk_source_timing_and_shapes":metrics,
                "original_sdk_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in row["full_original_sdk_action_events"]],
            }
            records.append(record)
            for phase,stack in stacks.items():
                original_arrays[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_EARLY_STREAM_INTERCEPT "+json.dumps({
                "case":name,"witness":witness,
                "sdk_level":record["real_original_sdk_level"],
                "sdk_state":record["real_original_sdk_state"],
                "source_metrics":metrics,
            },sort_keys=True),flush=True)
    if len(records)!=36 or len(roots)!=1:
        raise AssertionError("Missing genuine original native source witness")
    gains=[
        {"case":r["original_frozen_control"],"witness":r["genuine_independent_native_witness"],
        "word":r["source_action_word"],"level":r["real_original_sdk_level"]}
        for r in records if r["real_original_sdk_level4_or_WIN"]
    ]
    payload={
        "kind":"ACTUAL_ORIGINAL_SP80_STAGE3_EARLY_STREAM_INTERCEPTION",
        "source_antecedents":[39463571663,39549622886],
        "authentic_independently_reset_original_sdk_games":len(records),
        "frozen_native_words":FROZEN,
        "original_source_stage3_root_blake2b16":next(iter(roots)),
        "real_original_sdk_level4_or_WIN_count":len(gains),
        "actual_native_source_progresses":gains,
        "real_original_sdk_last_level_counts":dict(Counter(str(r["real_original_sdk_level"]) for r in records)),
        "real_original_sdk_last_state_counts":dict(Counter(r["real_original_sdk_state"] for r in records)),
        "all_real_original_sdk_source_records":records,
        "boundary":"Only actual native SDK level>=4 or WIN proves progress. Color6, cup-region color and bottom-line onset are observed source pixel transitions; no source-engine leak proof, substitute solver, or physical claim. Original 64x64 returned frames preserved in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**original_arrays)
    print("ORIGINAL_SP80_INTERCEPT_SUMMARY "+json.dumps({
        k:v for k,v in payload.items() if k not in ("frozen_native_words","all_real_original_sdk_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
