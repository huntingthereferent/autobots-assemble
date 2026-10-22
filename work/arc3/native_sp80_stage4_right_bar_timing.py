"""Original SDK SP80 stage4: one-factor horizontal right-source-bar controls.

Only the first authentic selected right bar's movement changes. Fixed D3L2
middle placement, L3U2 lower placement and final upper LEFT1 + ACTION5.
Both independent original stage4 entrances replay every frozen word. Native
SDK level5/WIN is the only positive outcome, not simulated cup flow.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_top_left_source_contrast import source_report
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

FROZEN=(
    ("right_reselect_only","6@46,33"),
    ("right_left1","6@46,33 3"),
    ("right_left2","6@46,33 3 3"),
    ("right_right1","6@46,33 4"),
)
MIDDLE="6@24,33 2 2 2 3 3"
LOWER="6@34,42 3 3 3 1 1"
UPPER="6@34,21 3 5"

def bbox_selected(frame):
    ys,xs=np.nonzero(frame==9)
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None

def first_touch(root,pre,frames):
    # Only source-native observation; do not claim a physical fluid or clock.
    masks=[]
    for x0,y0,x1,y1 in ((5,35,10,43),(17,5,25,10),(35,5,43,10),(47,5,55,10)):
        mask=np.zeros((64,64),bool)
        mask[y0:y1+1,x0:x1+1]=(root[y0:y1+1,x0:x1+1]==11)
        if int(mask.sum())!=45:raise AssertionError("Native source cup geometry changed")
        masks.append(mask)
    totals=[]
    all_full=[]
    for i,frame in enumerate(frames):
        counts=[int(np.count_nonzero((frame==13)&mask)) for mask in masks]
        totals.append(counts)
        if all(x==45 for x in counts):all_full.append(i)
    first_13={}
    for i,name in enumerate(("lateral","top_left","top_middle","top_right")):
        frames_nonzero=[n for n,row in enumerate(totals) if row[i]>0]
        first_13[name]=frames_nonzero[0] if frames_nonzero else None
    return {"first_source_cup_palette13":first_13,
            "all_full_frames":all_full,
            "source_total_cup_filled_penultimate":[int(x) for x in totals[-2]],
            "source_total_cup_filled_terminal":[int(x) for x in totals[-1]],
            "source_animation_count":len(frames),
            "native_last_frame_hash":hash_frame(frames[-1])}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    opts=a.parse_args()
    records=[];arrays={};source_roots=set()
    for name,right_word in FROZEN:
        n_right=len(parse_plan(right_word))
        action_word=" ".join((right_word,MIDDLE,LOWER,UPPER))
        commands=parse_plan(action_word)
        assert commands[-1][0]==5 and sum(x==5 for x,xy in commands)==1
        for witness,entry in STAGE1_WITNESSES:
            native,source=run_case(name,witness,entry,action_word)
            root=source["entry3_34"][-1]
            source_roots.add(hash_frame(root))
            right_selection=source["stage4_1"][-1]
            right_after=source["stage4_"+str(n_right)][-1]
            pre=source["stage4_"+str(len(commands)-1)][-1]
            frames=source["stage4_"+str(len(commands))]
            if bbox_selected(right_selection)!=[41,32,55,34]:
                raise AssertionError("Actual right bar source selection differed from verified root")
            measurements=source_report(root,pre,frames)
            cup_events=first_touch(root,pre,frames)
            row={"condition":name,"witness":witness,
               "original_sdk_action_word":action_word,
               "original_selected_right_before":bbox_selected(right_selection),
               "original_selected_right_after":bbox_selected(right_after),
               "right_source_pre":hash_frame(right_selection),
               "right_source_after":hash_frame(right_after),
               "official_original_level":native["true_original_sdk_final_level"],
               "official_original_state":native["true_original_sdk_final_state"],
               "official_level5_or_WIN":native["official_original_level5_or_WIN"],
               "source_cup_events":measurements,
               "source_cup_frame_timeline":cup_events,
               "original_stage4_sdk_receipts":native["genuine_original_stage4_action_ledger"]}
            records.append(row)
            for k,frameset in source.items():arrays[name+"_"+witness+"_"+k]=frameset
            print("ARC4_RIGHT_BAR_NATIVE_CASE "+json.dumps({
              "name":name,"witness":witness,
              "selected_before":row["original_selected_right_before"],
              "selected_after":row["original_selected_right_after"],
              "cup_first_full":measurements["source_first_full_cups"],
              "all_full":cup_events["all_full_frames"],
              "sdk_level":row["official_original_level"],
              "sdk_state":row["official_original_state"]},sort_keys=True),flush=True)
    if len(records)!=8 or len(source_roots)!=1:raise AssertionError("Native source entrances differ")
    for name,_ in FROZEN:
        rows=[x for x in records if x["condition"]==name]
        if len(rows)!=2 or {x["witness"] for x in rows}!={"A","B"}:
            raise AssertionError("Missing independent source entrance "+name)
        for key in ("original_selected_right_before","original_selected_right_after",
                    "official_original_level","official_original_state",
                    "source_cup_events","source_cup_frame_timeline"):
            if rows[0][key]!=rows[1][key]:
                raise AssertionError("Original SDK A/B disagreement "+name+"."+key)
    output={"kind":"SP80_NATIVE_STAGE4_RIGHT_BAR_HORIZONTAL_ONE_FACTOR",
       "original_sdk_resets":len(records),
       "native_original_level_histogram":dict(Counter(str(x["official_original_level"]) for x in records)),
       "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in records),
       "source_frozen_conditions":FROZEN,
       "original_native_rows":records,
       "boundary":"No offscreen rule inferred. Cup timing and visible shifts are source outputs, SDK level/state establish progress."}
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(opts.out.with_suffix(".npz"),**arrays)
    print("ARC4_RIGHT_BAR_SOURCE_SUMMARY "+json.dumps({
       "original_sdk_resets":len(records),
       "official_levels":output["native_original_level_histogram"],
       "level5_or_WIN":output["official_level5_or_WIN_count"],
       "source_controls":{name:{
          "native_selected_right_bbox":next(z["original_selected_right_after"] for z in records if z["condition"]==name),
          "native_first_full_cups":next(z["source_cup_events"]["source_first_full_cups"] for z in records if z["condition"]==name),
          "source_first_palette13_cup":next(z["source_cup_frame_timeline"]["first_source_cup_palette13"] for z in records if z["condition"]==name),
          "all_simultaneous_full_frames":next(z["source_cup_frame_timeline"]["all_full_frames"] for z in records if z["condition"]==name)}
          for name,_ in FROZEN}},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
