"""Reproduce exact ARC4 same-position frame differences from original SDK JSON/NPZ.

Checks every returned frame, not only hashes or cup summaries. Does not
infer what row63 means in the original game.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from .native_sp80_multi_select import parse_plan

HISTORIES=("left_right_left","left_up_down","left_down_up","left_left_right")
WITNESSES=("A","B")

def changes(before,after):
    ys,xs=np.nonzero(before!=after)
    return [{"x":int(x),"y":int(y),
             "source_before":int(before[y,x]),
             "source_after":int(after[y,x])}
            for y,x in zip(ys,xs)]

def inspect(source,stack,witness,history):
    rows={(v["history"],v["witness"]):v for v in source["native_rows"]}
    base=rows[("direct_left1",witness)]
    other=rows[(history,witness)]
    def images(rec):
        n=len(parse_plan(rec["actual_native_sdk_word"]))
        root=rec["history"]+"_"+witness+"_stage4_"
        return stack[root+str(n-1)][-1],stack[root+str(n)]
    base_pre,base_frames=images(base)
    other_pre,other_frames=images(other)
    if base_frames.shape!=other_frames.shape:
        raise AssertionError("Original SDK animation stacks have different lengths")
    pixel_compare=(base_frames!=other_frames)
    frame_counts=[int(x) for x in pixel_compare.sum(axis=(1,2))]
    inner_counts=[int(x) for x in pixel_compare[:,:63,:].sum(axis=(1,2))]
    return {
        "witness":witness,"history":history,
        "original_sdk_levels":[base["actual_level"],other["actual_level"]],
        "original_sdk_states":[base["actual_state"],other["actual_state"]],
        "native_animation_frames":len(base_frames),
        "source_prepour_pixel_changes":changes(base_pre,other_pre),
        "source_final_pixel_changes":changes(base_frames[-1],other_frames[-1]),
        "total_pixel_frame_differences":sum(frame_counts),
        "interior_rows0_62_pixel_frame_differences":sum(inner_counts),
        "bottom_row63_pixel_frame_differences":sum(frame_counts)-sum(inner_counts),
        "source_pour_animation_difference_counts":frame_counts,
        "recorded_cup_outcome_equal":(
            base["source"]["source_first_full_cups"]==other["source"]["source_first_full_cups"]
        ),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--npz",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    source=json.loads(a.json.read_text())
    if source.get("kind")!="ARC4_SAME_POSITION_DIFFERENT_HISTORY_GENUINE_NATIVE":
        raise ValueError("Expected a genuine original SDK history trial")
    with np.load(a.npz,allow_pickle=False) as data:
        rows=[inspect(source,data,w,h) for h in HISTORIES for w in WITNESSES]
    pairs={}
    for history in HISTORIES:
        group=[row for row in rows if row["history"]==history]
        if len(group)!=2:raise AssertionError("Missing original native A/B witness")
        keys=("source_prepour_pixel_changes","source_final_pixel_changes",
              "total_pixel_frame_differences","interior_rows0_62_pixel_frame_differences")
        for key in keys:
            if group[0][key]!=group[1][key]:
                raise AssertionError("Independent native A/B source disagreement "+history+" "+key)
        pairs[history]={"native_witnesses":2,
                        "native_frames_each":group[0]["native_animation_frames"],
                        "pre_pour_differences":group[0]["source_prepour_pixel_changes"],
                        "post_pour_differences":group[0]["source_final_pixel_changes"],
                        "interior_rows0_62_pixel_frame_differences":group[0]["interior_rows0_62_pixel_frame_differences"],
                        "bottom_row63_pixel_frame_differences":group[0]["bottom_row63_pixel_frame_differences"]}
    report={"kind":"ARC4_GENUINE_SDK_SAME_POSITION_PIXEL_DIFF_AUDIT",
            "native_comparison_rows":rows,
            "independent_history_pairs":pairs,
            "limit":"Row63 pixels are part of native source frames; their game semantics are unknown. Pixel equality does not prove hidden-state equivalence."}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("ARC4_HISTORY_PIXEL_AUDIT "+json.dumps(pairs,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
