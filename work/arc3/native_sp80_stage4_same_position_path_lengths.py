"""Authentic SP80 level4: same selected upper-bar location across path lengths.

This prospective finite source audit varies only the native upper-bar movement
history before the same ACTION5. It reads SDK state, pixels, and action receipts,
without assigning semantics to the bottommost screen row.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_top_left_source_contrast import PARENT, source_report
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

# All paths have net LEFT1 in the source-observed movement alphabet.
FROZEN = (
    ("one_left", "3"),
    ("three_horizontal", "3 4 3"),
    ("three_vertical", "3 1 2"),
    ("five_horizontal", "3 4 3 4 3"),
    ("five_vertical", "3 1 2 1 2"),
    ("seven_horizontal", "3 4 3 4 3 4 3"),
    ("seven_vertical", "3 1 2 1 2 1 2"),
)
BBOX=(26,20,37,22)

def row_digest(frame):
    values=frame[63,:]
    return {"source_pixels":[int(x) for x in values.tolist()],
            "palette_histogram":dict(Counter(str(int(c)) for c in values)),
            "source_hash":hash_frame(frame)}

def compare(base,other):
    base_pre,base_frames=base
    pre,frames=other
    differences=np.argwhere(pre!=base_pre)
    if frames.shape!=base_frames.shape:raise AssertionError("Unequal original SDK animation frames")
    changed=frames!=base_frames
    outside=changed[:,:63,:]
    per_frame=[int(np.count_nonzero(z)) for z in changed]
    inside=[int(np.count_nonzero(z)) for z in outside]
    return {
        "native_prepour_different_pixels":int(len(differences)),
        "native_prepour_coordinates":[[int(x),int(y),int(base_pre[y,x]),int(pre[y,x])] for y,x in differences],
        "native_different_pixel_frames_total":int(np.count_nonzero(changed)),
        "native_different_pixel_frames_y0_62":int(np.count_nonzero(outside)),
        "native_different_pixel_frames_y63":int(np.count_nonzero(changed[:,63,:])),
        "first_nonidentical_animation_frame":next((int(i) for i,n in enumerate(per_frame) if n),None),
        "per_frame_native_different_pixel_counts":per_frame,
        "per_frame_native_interior_different_pixel_counts":inside,
        "native_final_frame_different_pixels":[[int(x),int(y),int(base_frames[-1,y,x]),int(frames[-1,y,x])]
           for y,x in np.argwhere(base_frames[-1]!=frames[-1])],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];arrays={};cases={};roots=set()
    for name,moves in FROZEN:
        word=" ".join([PARENT,moves,"5"])
        program=parse_plan(word)
        if program[-1][0]!=5 or sum(a==5 for a,xy in program)!=1:
            raise AssertionError("Exactly one terminal original native ACTION5")
        for witness,entry in STAGE1_WITNESSES:
            native,raw=run_case(name,witness,entry,word)
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(len(program)-1)][-1]
            frames=raw["stage4_"+str(len(program))]
            source=source_report(root,pre,frames)
            roots.add(source["root_hash"])
            source_bbox=source["selected_bbox"]
            if source_bbox!=list(BBOX):
                raise AssertionError("Same-position original source condition failed "+name+" "+str(source_bbox))
            line={
                "case":name, "witness":witness,"upper_source_action_count":len(parse_plan(moves)),
                "real_native_program":word,
                "official_native_level":native["true_original_sdk_final_level"],
                "official_native_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "native_action_receipts":native["genuine_original_stage4_action_ledger"],
                "actual_source":source,
                "native_prepour_row63":row_digest(pre),
                "native_last_pour_row63":row_digest(frames[-1])
            }
            records.append(line)
            cases[(name,witness)]=(pre.copy(),frames.copy())
            for key,array in raw.items():arrays[name+"_"+witness+"_"+key]=array
            print("ARC4_LENGTH_CASE "+json.dumps({
                "case":name,"witness":witness,"movement_actions":line["upper_source_action_count"],
                "native_level":line["official_native_level"],"state":line["official_native_state"],
                "source_selected_bbox":source_bbox,"source_cup_first_full":source["source_first_full_cups"],
                "source_bottom_row_before":line["native_prepour_row63"]["source_pixels"],
                "source_bottom_row_after":line["native_last_pour_row63"]["source_pixels"],
            },sort_keys=True),flush=True)
    if len(roots)!=1:raise AssertionError("Original native source entrance roots differed")
    differences={}
    for name,moves in FROZEN:
        group=[r for r in records if r["case"]==name]
        if len(group)!=2 or {g["witness"] for g in group}!={"A","B"}:
            raise AssertionError("Missing independent original SDK A/B case")
        for key in ("official_native_level","official_native_state","actual_source","native_prepour_row63","native_last_pour_row63"):
            if group[0][key]!=group[1][key]:
                raise AssertionError("Original SDK source A/B observation mismatch "+name+" "+key)
        if name=="one_left":continue
        by_witness=[compare(cases[("one_left",w)],cases[(name,w)]) for w in ("A","B")]
        if by_witness[0]!=by_witness[1]:
            raise AssertionError("Original SDK pixel comparison A/B mismatch "+name)
        differences[name]=by_witness[0]
    outcome={
        "kind":"ORIGINAL_SP80_STAGE4_SAME_SELECTED_POSITION_LENGTH_CONTROLS",
        "original_sdk_independent_resets":len(records),
        "source_frozen_upper_histories":FROZEN,
        "official_level_counts":dict(Counter(str(r["official_native_level"]) for r in records)),
        "official_level5_or_WIN_count":sum(int(r["official_level5_or_WIN"]) for r in records),
        "same_selected_native_bbox":list(BBOX),
        "original_sdk_records":records,
        "source_exact_frame_comparisons_to_one_left":differences,
        "boundary":"All 64x64 original SDK pixels and action receipts retained; any bottom-row meaning is UNKNOWN; frame-index equality is not hidden-state equivalence."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ARC4_LENGTH_SUMMARY "+json.dumps({
       "independent_original_sdk_resets":len(records),
       "official_level5_or_WIN_count":outcome["official_level5_or_WIN_count"],
       "official_level_counts":outcome["official_level_counts"],
       "history_source_results":[{"name":n,"move_count":next(r["upper_source_action_count"] for r in records if r["case"]==n),
          "pre_row63":next(r["native_prepour_row63"]["source_pixels"] for r in records if r["case"]==n),
          "final_row63":next(r["native_last_pour_row63"]["source_pixels"] for r in records if r["case"]==n),
          "cup_full":next(r["actual_source"]["source_first_full_cups"] for r in records if r["case"]==n)}
          for n,_ in FROZEN],
       "different_frame_pixels":{k:{"pre":v["native_prepour_different_pixels"],
          "interior":v["native_different_pixel_frames_y0_62"],
          "bottom":v["native_different_pixel_frames_y63"],
          "final":v["native_final_frame_different_pixels"]} for k,v in differences.items()}
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
