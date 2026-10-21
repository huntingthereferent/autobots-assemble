"""Original SDK SP80 stage3: two observed palette4 sources and one-pour boundary.

Previous genuine runs proved real 0->1->2->3 source entries and observed
two separate palette4 marker regions on the genuine level3 frame
(#39463571663). The middle marker lies among linked selectable pieces.
The public SP80 level4 guide suggests a source on a movable bar, and both
cup completion AND avoiding spill matter. This is a proposed interpretation,
NOT verified engine physics; all evidence is measured original SDK frames.

New trial: move observed mid-marker-bearing pair and contrast actual upper,
lower and bottom piece placements. One original ACTION5 per fresh game.
Only official source SDK levels_completed>=4 or WIN counts as progress.
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

def move(click, direction, count):
    return ("6@%d,%d " % click + " ".join([str(direction)] * count)) if count else ""

def middle(n):
    return move((10, 30), 4, n)

def bottom(direction, count):
    return move((40, 42), direction, count)

def top_left(n):
    return move((20, 18), 3, n)

def top_right(n):
    return move((20, 18), 4, n)

def other_top(direction, count):
    return move((40, 18), direction, count)

def low_right(direction, count):
    return move((46, 33), direction, count)

def plan(*blocks):
    return " ".join(x for x in (*blocks, "5") if x)

# Prospective spatial contrast surrounding REAL source-screen four-group
# feedback configurations in original run #39475858637.
FROZEN = (
    ("mid3_bottom_right1", plan(middle(3), bottom(4,1))),
    ("mid4_bottom_right1", plan(middle(4), bottom(4,1))),
    ("mid5_bottom_right1", plan(middle(5), bottom(4,1))),
    ("mid4_bottom_held", plan(middle(4))),
    ("mid4_bottom_right2", plan(middle(4), bottom(4,2))),
    ("mid4_bottom_left1", plan(middle(4), bottom(3,1))),
    ("top_left1_mid4_bottom1", plan(top_left(1), middle(4), bottom(4,1))),
    ("top_left2_mid4_bottom1", plan(top_left(2), middle(4), bottom(4,1))),
    ("top_left3_mid4_bottom1", plan(top_left(3), middle(4), bottom(4,1))),
    ("top_right1_mid4_bottom1", plan(top_right(1), middle(4), bottom(4,1))),
    ("top_right2_mid4_bottom1", plan(top_right(2), middle(4), bottom(4,1))),
    ("top_right2_mid3_bottom1", plan(top_right(2), middle(3), bottom(4,1))),
    ("top_right1_mid3_bottom1", plan(top_right(1), middle(3), bottom(4,1))),
    ("other_top_left1_mid4_bottom1", plan(other_top(3,1), middle(4), bottom(4,1))),
    ("other_top_up1_mid4_bottom1", plan(other_top(1,1), middle(4), bottom(4,1))),
    ("other_top_down1_mid4_bottom1", plan(other_top(2,1), middle(4), bottom(4,1))),
    ("low_right_left1_mid4_bottom1", plan(low_right(3,1), middle(4), bottom(4,1))),
    ("low_right_right1_mid4_bottom1", plan(low_right(4,1), middle(4), bottom(4,1))),
    ("low_right_up1_mid4_bottom1", plan(low_right(1,1), middle(4), bottom(4,1))),
    ("low_right_down1_mid4_bottom1", plan(low_right(2,1), middle(4), bottom(4,1))),
)
assert len(FROZEN) == 20 == len(set(name for name, _ in FROZEN))
assert len(STAGE1_WITNESSES) == 2
assert all(
    len(parse_plan(word)) <= 20
    and sum(a==5 for a, _ in parse_plan(word)) == 1
    and parse_plan(word)[-1][0] == 5
    for _,word in FROZEN
)
CUP_BOUNDS=((8,16),(26,34),(38,46),(50,58))

def scan_original(pre, returned):
    """Return actual animation facts, without labeling game failure cause."""
    yy, xx = pre.shape
    if (yy,xx)!=(64,64): raise AssertionError("unexpected original SDK shape")
    measurements=[]
    active_boundary=set()
    touched_outside=set()
    for i,frame in enumerate(returned):
        if frame.shape != pre.shape: raise AssertionError("source frame shape changed")
        hits=[]
        for lo,hi in CUP_BOUNDS:
            cup=pre[53:59,lo:hi+1]
            now=frame[53:59,lo:hi+1]
            hits.append(int(np.count_nonzero((cup==11)&(now==13))))
        edge=pre[59:63,2:62] != frame[59:63,2:62]
        ys,xs=np.nonzero(edge)
        for y,x in zip(ys,xs):active_boundary.add((int(y)+59,int(x)+2))
        # Bottom source pixels outside original cup boxes. This raw pixel
        # trajectory is NOT a decoded leak oracle.
        out=np.zeros((6,60),dtype=bool)
        for j in range(60):
            x=j+2
            if not any(lo<=x<=hi for lo,hi in CUP_BOUNDS):
                out[:,j]=pre[53:59,x]!=frame[53:59,x]
        ys2,xs2=np.nonzero(out)
        for y,x in zip(ys2,xs2):touched_outside.add((int(y)+53,int(x)+2))
        measurements.append({
            "animation_frame_index":i,
            "observed_cup11_to13_counts":hits,
            "simultaneous_full_observed_cup_regions":sum(n==45 for n in hits),
            "original_bottom_boundary_changed_pixels":int(np.count_nonzero(edge)),
        })
    comps=[{"bbox":c["bbox"],"pixels":c["pixels"]}
           for c in color_components(pre) if c["palette"]==4]
    return {
        "true_sdk_animation_frame_count":len(returned),
        "original_pre_pour_source_frame_blake2b16":hash_frame(pre),
        "original_after_pour_source_frame_blake2b16":hash_frame(returned[-1]),
        "measured_source_palette4_markers_before_pour":comps,
        "all_actual_returned_animation_frame_metrics":measurements,
        "max_simultaneous_fully_changed_cup_regions":max(
            (m["simultaneous_full_observed_cup_regions"] for m in measurements),default=0),
        "maximum_bottom_boundary_pixel_changes_in_one_frame":max(
            (m["original_bottom_boundary_changed_pixels"] for m in measurements),default=0),
        "number_distinct_changed_original_bottom_boundary_pixels":len(active_boundary),
        "number_distinct_changed_source_bottom_gap_pixels":len(touched_outside),
        "note":"Source color transitions and bottom pixel changes only; no guessed physics or proven leak label.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    all_records=[];raw_arrays={};roots=set()
    for name,word in FROZEN:
        parsed=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            row,frames=real_trial(witness,entry,name,word)
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            last_key="stage3_"+str(len(parsed))
            last=frames.get(last_key)
            before_key="stage3_"+str(len(parsed)-1)
            before=frames[before_key][-1] if before_key in frames else frames["entry2_11"][-1]
            observed=scan_original(before,last) if last is not None else None
            receipt={
                "prospectively_frozen_case":name,
                "genuine_sdk_witness":witness,
                "actual_original_source_native_word":word,
                "official_original_sdk_level":row["official_original_final_level"],
                "official_original_sdk_state":row["official_original_final_state"],
                "actual_original_sdk_level4_or_WIN":row["official_original_level4_or_WIN"],
                "original_sdk_trial_disposition":row["trial_disposition"],
                "native_single_pour_frame_diagnostics":observed,
                "true_original_sdk_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in row["full_original_sdk_action_events"]],
            }
            all_records.append(receipt)
            for phase,arr in frames.items():
                raw_arrays[f"{name}_{witness}_{phase}"]=arr
            print("ORIGINAL_SP80_TWO_SOURCE_SINGLE_POUR "+json.dumps({
                "case":name,"witness":witness,
                "level":receipt["official_original_sdk_level"],
                "state":receipt["official_original_sdk_state"],
                "diag":({k:v for k,v in observed.items()
                         if k not in ("all_actual_returned_animation_frame_metrics","note")}
                        if observed else None),
            },sort_keys=True),flush=True)
    if len(all_records)!=40 or len(roots)!=1:
        raise AssertionError("Missing original SDK source entries or mismatched roots")
    progresses=[{
        "case":r["prospectively_frozen_case"],"witness":r["genuine_sdk_witness"],
        "word":r["actual_original_source_native_word"],
        "official_level":r["official_original_sdk_level"],
        "official_state":r["official_original_sdk_state"]}
        for r in all_records if r["actual_original_sdk_level4_or_WIN"]]
    summary={
        "kind":"GENUINE_ORIGINAL_SP80_STAGE3_TWO_SOURCE_SINGLE_POUR_BOUNDARY",
        "source_antecedents":[39463571663,39475858637,39548593826],
        "original_sdk_reset_games":len(all_records),
        "prospective_native_words":FROZEN,
        "verified_original_stage3_root_source_blake2b16":next(iter(roots)),
        "official_original_final_levels":dict(Counter(str(r["official_original_sdk_level"]) for r in all_records)),
        "official_original_final_states":dict(Counter(r["official_original_sdk_state"] for r in all_records)),
        "original_native_level4_or_WIN_count":len(progresses),
        "actual_sdk_progress_witnesses":progresses,
        "original_sdk_source_records":all_records,
        "limitations":"Only the original SDK reveals level changes. Source palette4 marks, simultaneous palette11->13 cup-region changes and bottom boundary changes are observation, not proven success conditions or private engine physics. All raw SDK returned frames preserved.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_arrays)
    print("ORIGINAL_SP80_TWO_SOURCE_SINGLE_POUR_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospective_native_words","original_sdk_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
