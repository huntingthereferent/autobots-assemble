"""Frame-by-frame native source timeline for the SP80 level-4 cup-fill boundary.

Narrow follow-up to cross-arrangement experiment: compare top_left1 vs
 top_left2 on both frozen lower arrangements, preserving all original SDK
 frames and official level/state. Cup pixels are observations, not a win rule.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT = "6@46,33 3"
PARENTS = (
    ("clean_D3L2_L3U2", "6@24,33 2 2 2 3 3", "6@34,42 3 3 3 1 1"),
    ("clean_D4L2_L4U2", "6@24,33 2 2 2 2 3 3", "6@34,42 3 3 3 3 1 1"),
)
CUP = {
    "left_lateral": (5,35,10,43),
    "top_left": (17,5,25,10),
    "top_middle": (35,5,43,10),
    "top_right": (47,5,55,10),
}
TOP = "6@34,21"
CONDITIONS = (("top_left1","3"), ("top_left2","3 3"))

def program(middle, lower_l, upper):
    return " ".join(x for x in (RIGHT,middle,lower_l,TOP,upper,"5") if x)

FROZEN = tuple(
    (f"{parent}_{name}", program(middle,lower_l,upper))
    for parent,middle,lower_l in PARENTS
    for name,upper in CONDITIONS
)
assert len(FROZEN) == 4
assert len(STAGE1_WITNESSES) == 2

def frame_profile(root, pre, frames):
    if root.shape != (64,64) or pre.shape != (64,64) or frames.ndim != 3 or frames.shape[1:] != (64,64):
        raise AssertionError("Expected actual original SDK 64x64 frames")
    profiles=[]
    previous=pre
    for t, frame in enumerate(frames):
        cups={}
        for name,(x0,y0,x1,y1) in CUP.items():
            original=(root[y0:y1+1,x0:x1+1] == 11)
            if int(original.sum()) != 45:
                raise AssertionError("Original source cup mask changed")
            cups[name]=int(np.count_nonzero(original & (frame[y0:y1+1,x0:x1+1] == 13)))
        changed=np.argwhere(frame != previous)
        profiles.append({
            "frame":t,
            "source_hash":hash_frame(frame),
            "changed_pixels_vs_previous_frame":int(len(changed)),
            "cup_fill_pixels_to13":cups,
            "cups_fully_filled":sum(v==45 for v in cups.values()),
            "four_cups_simultaneous":all(v==45 for v in cups.values()),
        })
        previous=frame
    return profiles

def selected(frame):
    return [{"bbox":c["bbox"],"pixels":c["pixels"]} for c in color_components(frame)
            if c["palette"]==9 and 19<=c["bbox"][1]<=53]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    records=[]; all_frames={}; roots=set()
    for case,word in FROZEN:
        parts=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(len(parts)-1)][-1]
            poured=raw["stage4_"+str(len(parts))]
            profile=frame_profile(root,pre,poured)
            row={
                "case":case,"witness":witness,"word":word,
                "official_level":sdk["true_original_sdk_final_level"],
                "official_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "prepour_hash":hash_frame(pre),
                "selected_objects_before_pour":selected(pre),
                "frame_profile":profile,
                "action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            records.append(row)
            for k,stack in raw.items():
                all_frames[f"{case}_{witness}_{k}"]=stack
            print("ORIGINAL_SP80_CUP_TRANSITION_CASE "+json.dumps({
                "case":case,"witness":witness,"official_level":row["official_level"],
                "official_state":row["official_state"],
                "first_four_cups_frame":next((p["frame"] for p in profile if p["four_cups_simultaneous"]),None),
                "timeline":profile,
            },sort_keys=True),flush=True)
    if len(records)!=8 or len(roots)!=1:
        raise AssertionError("Expected 8 independent native SDK runs from one level-4 root")
    for case,_ in FROZEN:
        pair=[r for r in records if r["case"]==case]
        if len(pair)!=2 or pair[0]["frame_profile"]!=pair[1]["frame_profile"]:
            raise AssertionError("A/B source timeline mismatch: "+case)
    summary={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_CUP_TRANSITION_TIMELINE",
        "source_experiment":"PR #398 cross-arrangement validation",
        "root_hash":next(iter(roots)),
        "fresh_original_sdk_resets":len(records),
        "condition_count":len(FROZEN),
        "official_level5_or_WIN_count":sum(r["official_level5_or_WIN"] for r in records),
        "official_level_histogram":dict(Counter(str(r["official_level"]) for r in records)),
        "official_state_histogram":dict(Counter(str(r["official_state"]) for r in records)),
        "records":records,
        "interpretation_boundary":"Timeline and cup fill are source observations only. Official SDK level/state is reported separately; no pixel threshold is treated as a win.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_frames)
    print("ORIGINAL_SP80_CUP_TRANSITION_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="records"
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
