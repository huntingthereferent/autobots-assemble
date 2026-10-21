"""Native SP80 level3 source intervention: catch second observed early stream.

Run #39550721172 (original SDK NPZ independently inspected) retained four
cup-region source transitions under the 10-left lower-bar movement, and
changed the earliest bottom source-boundary transition from frame22 at
x17..19 incoming palette6 to frame26 at x35..37. These are actual source
pixel observations, not decoded engine mechanics.

Keep that original source correction fixed, vary the second bottom bar's
actual native position around the new observed x35..37 path, run exactly
one true ACTION5 per fresh original SP80 game. Only the original SDK
levels_completed>=4 or WIN proves advancement.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import Counter
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

MID4="6@10,30 4 4 4 4"
CORRECT_LEFT10="6@46,33 "+" ".join(["3"]*10)
CORRECT_DOWN1_LEFT10="6@46,33 2 "+" ".join(["3"]*10)

def bottom(direction,steps):
    if steps==0:return ""
    return "6@40,42 "+" ".join([str(direction)]*steps)

def plan(*blocks):
    return " ".join(x for x in (*blocks,"5") if x)

# Predeclared source x35..37 catcher comparisons. No feedback is used to
# change this roster during the original native SDK experiments.
FROZEN=(
    ("source_previous_bottom_right1",plan(MID4,CORRECT_LEFT10,bottom(4,1))),
    ("second_bar_held",plan(MID4,CORRECT_LEFT10)),
    ("second_bar_left1",plan(MID4,CORRECT_LEFT10,bottom(3,1))),
    ("second_bar_left2",plan(MID4,CORRECT_LEFT10,bottom(3,2))),
    ("second_bar_left3",plan(MID4,CORRECT_LEFT10,bottom(3,3))),
    ("second_bar_left4",plan(MID4,CORRECT_LEFT10,bottom(3,4))),
    ("second_bar_right2",plan(MID4,CORRECT_LEFT10,bottom(4,2))),
    ("second_bar_right3",plan(MID4,CORRECT_LEFT10,bottom(4,3))),
    ("top_left1_second_left2",plan("6@20,18 3",MID4,CORRECT_LEFT10,bottom(3,2))),
    ("top_left2_second_left2",plan("6@20,18 3 3",MID4,CORRECT_LEFT10,bottom(3,2))),
    ("top_right1_second_left2",plan("6@20,18 4",MID4,CORRECT_LEFT10,bottom(3,2))),
    ("top_left1_second_left3",plan("6@20,18 3",MID4,CORRECT_LEFT10,bottom(3,3))),
    ("top_right1_second_left3",plan("6@20,18 4",MID4,CORRECT_LEFT10,bottom(3,3))),
    ("down1_lower_left10_second_left2",plan(MID4,CORRECT_DOWN1_LEFT10,bottom(3,2))),
)
assert len(FROZEN)==14==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,_ in parse_plan(w))==1
           and len(parse_plan(w))<=27 for _,w in FROZEN)
CUPS=((8,16),(26,34),(38,46),(50,58))

def observe_source(before,animation):
    if before.shape!=(64,64):
        raise AssertionError("Not original 64x64 source frame")
    first_boundary=None;first_all4=None;best=0;first_boundary_x=[];percup=[None]*4
    for k,frame in enumerate(animation):
        if frame.shape!=before.shape:
            raise AssertionError("Not native original animation")
        cs=[
            int(np.count_nonzero(
                (before[53:59,lo:hi+1]==11)&(frame[53:59,lo:hi+1]==13)
            )) for lo,hi in CUPS
        ]
        for i,n in enumerate(cs):
            if n==45 and percup[i] is None:percup[i]=k
        score=sum(n==45 for n in cs)
        best=max(best,score)
        if score==4 and first_all4 is None:first_all4=k
        edge=(before[59:63,2:62]!=frame[59:63,2:62])
        if first_boundary is None and edge.any():
            first_boundary=k
            # Native source flow-colored positions at y58 when the first
            # original boundary pixel changes. Not inferred leak causes.
            first_boundary_x=[
                int(x) for x in np.where(
                    (before[58]!=6)&(frame[58]==6)
                )[0]
            ]
    shapes=[{"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
            for c in color_components(before)
            if c["palette"] in (8,9) and 29<=c["bbox"][1]<=44]
    return {
        "original_native_animation_frames":len(animation),
        "original_pre_source_blake2b16":hash_frame(before),
        "original_post_source_blake2b16":hash_frame(animation[-1]),
        "actual_original_lower_bar_pre_pour_bboxes":shapes,
        "first_actual_bottom_boundary_change_frame":first_boundary,
        "first_actual_bottom_boundary_flow_color6_x_at_y58":first_boundary_x,
        "first_simultaneous_four_original_cup_change_frame":first_all4,
        "source_max_simultaneous_cup_regions":best,
        "original_cup_first_full_change_frames":percup,
        "boundary":"All reported pixel changes are true SDK returns, not an objective predicate.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    records=[];arrays={};roots=set()
    for name,word in FROZEN:
        parts=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            row,frames=real_trial(witness,entry,name,word)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            after=frames.get("stage3_"+str(len(parts)))
            bef=frames.get("stage3_"+str(len(parts)-1),frames["entry2_11"])[-1]
            obs=observe_source(bef,after) if after is not None else None
            record={
                "source_plan":name,"genuine_independent_native_witness":witness,
                "true_original_action_word":word,
                "original_SDK_official_final_level":row["official_original_final_level"],
                "original_SDK_official_final_state":row["official_original_final_state"],
                "original_SDK_level4_or_WIN":row["official_original_level4_or_WIN"],
                "observed_native_source_single_pour":obs,
                "original_sdk_native_action_records":[
                    {k:v for k,v in ev.items() if k!="full_original_source_frame_ledger"}
                    for ev in row["full_original_sdk_action_events"]],
            }
            records.append(record)
            for phase,stack in frames.items():
                arrays[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_SECOND_STREAM_CASE "+json.dumps({
                "case":name,"witness":witness,
                "source_level":record["original_SDK_official_final_level"],
                "source_state":record["original_SDK_official_final_state"],
                "observed":obs,
            },sort_keys=True),flush=True)
    if len(records)!=28 or len(roots)!=1:
        raise AssertionError("Source SDK independent root disagreement")
    progresses=[{
        "case":r["source_plan"],"witness":r["genuine_independent_native_witness"],
        "word":r["true_original_action_word"],
        "official_original_SDK_level":r["original_SDK_official_final_level"],
        "official_original_SDK_state":r["original_SDK_official_final_state"]}
        for r in records if r["original_SDK_level4_or_WIN"]]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE3_SECOND_EARLY_STREAM_CATCH",
        "original_source_antecedents":[39549622886,39550721172],
        "genuine_original_sdk_reset_games":len(records),
        "prospectively_frozen_words":FROZEN,
        "real_level3_root_original_blake2b16":next(iter(roots)),
        "true_original_level4_or_WIN_count":len(progresses),
        "actual_source_sdk_successes":progresses,
        "official_source_end_levels":dict(Counter(str(r["original_SDK_official_final_level"]) for r in records)),
        "official_source_end_states":dict(Counter(r["original_SDK_official_final_state"] for r in records)),
        "original_sdk_full_records":records,
        "boundary":"Only native SDK level>=4 or WIN proves progress. No substitution of proxy flow, game physics, or invented material movements. Original SDK frame arrays preserved in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_SECOND_STREAM_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("original_sdk_full_records","prospectively_frozen_words")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
