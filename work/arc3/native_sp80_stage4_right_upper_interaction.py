"""Original SDK SP80 level4: right bar x upper bar vertical interaction.

Frozen original source L/middle placement and exact two authentic entrance
witnesses. Right LEFT1/LEFT2 crossed with upper LEFT1, LEFT1-UP1,
LEFT1-DOWN1. No candidate is asserted to be a win. Only SDK levels
completed>=5 or WIN counts as progress, never four-cup pixels alone.
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

RIGHT_MOVES=(("right_LEFT1","3"),("right_LEFT2","3 3"))
UPPER_MOVES=(("upper_LEFT1","3"),("upper_LEFT1_UP1","3 1"),
             ("upper_LEFT1_DOWN1","3 2"))
MIDDLE="6@24,33 2 2 2 3 3"
LOWER="6@34,42 3 3 3 1 1"
FROZEN=tuple(
 (f"{right_name}__{upper_name}",
  " ".join(("6@46,33",right_word,MIDDLE,LOWER,
            "6@34,21",upper_word,"5")))
 for right_name,right_word in RIGHT_MOVES
 for upper_name,upper_word in UPPER_MOVES
)
CUP_MASKS=((5,35,10,43),(17,5,25,10),(35,5,43,10),(47,5,55,10))
CUP_NAMES=("lateral","top_left","top_middle","top_right")

def cup_timeline(root,frames):
 masks=[]
 for x0,y0,x1,y1 in CUP_MASKS:
  mask=np.zeros((64,64),bool)
  mask[y0:y1+1,x0:x1+1]=(root[y0:y1+1,x0:x1+1]==11)
  if int(mask.sum())!=45:raise AssertionError("Original 45-cell mask differs")
  masks.append(mask)
 all_cup=[]
 for f in frames:
  all_cup.append([int(np.count_nonzero((f==13)&m)) for m in masks])
 full=[int(i) for i,counts in enumerate(all_cup) if all(x==45 for x in counts)]
 return {
  "source_four_full_frame_indices":full,
  "source_first_full_by_cup":{
   k:next((i for i,rec in enumerate(all_cup) if rec[j]==45),None)
    for j,k in enumerate(CUP_NAMES)},
  "source_native_terminal_cup_values":all_cup[-1],
  "source_last_full_by_cup":{
   k:next((i for i in range(len(all_cup)-1,-1,-1) if all_cup[i][j]==45),None)
    for j,k in enumerate(CUP_NAMES)},
 }

def first_native_edge(pre,frames,area):
 reference=pre[area]
 return next((i for i,f in enumerate(frames) if np.any(f[area]!=reference)),None)

def selected_bbox(frame):
 y,x=np.nonzero(frame==9)
 return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,required=True)
 arg=p.parse_args()
 rows=[];saved={};root_hashes=set()
 for name,word in FROZEN:
  actions=parse_plan(word)
  if actions[-1][0]!=5 or sum(a==5 for a,_ in actions)!=1:
   raise AssertionError("Frozen trial must end with exactly one genuine ACTION5")
  for witness,entry in STAGE1_WITNESSES:
   native,raw=run_case(name,witness,entry,word)
   root=raw["entry3_34"][-1]
   before=raw["stage4_"+str(len(actions)-1)][-1]
   animation=raw["stage4_"+str(len(actions))]
   full=source_report(root,before,animation)
   cup=cup_timeline(root,animation)
   root_hashes.add(hash_frame(root))
   right_action_count=2 if name.startswith("right_LEFT1") else 3
   right_position=raw["stage4_"+str(right_action_count)][-1]
   right_bbox=selected_bbox(right_position)
   if right_bbox not in ([38,32,52,34],[35,32,49,34]):
    raise AssertionError("Real right-bar selected source position unknown "+str(right_bbox))
   row={
      "condition":name,"witness":witness,"original_sdk_action_word":word,
      "source_right_bar_selected_bbox":right_bbox,
      "source_upper_bar_selected_bbox":full["selected_bbox"],
      "original_sdk_level":native["true_original_sdk_final_level"],
      "original_sdk_state":native["true_original_sdk_final_state"],
      "official_level5_or_WIN":native["official_original_level5_or_WIN"],
      "original_native_sdk_stage4_receipts":native["genuine_original_stage4_action_ledger"],
      "source_observed_cup_timing":cup,
      "native_source_report":full,
      "original_sdk_first_left_measured_frame":first_native_edge(
       before,animation,(slice(2,62),slice(2,5))),
      "source_before_pour_hash":hash_frame(before),
      "source_final_returned_hash":hash_frame(animation[-1]),
   }
   rows.append(row)
   for key,frames in raw.items():saved[name+"_"+witness+"_"+key]=frames
   print("ARC4_RIGHT_UPPER_FACTOR "+json.dumps({
     "case":name,"native_witness":witness,
     "original_sdk_level":row["original_sdk_level"],
     "official_level5_or_WIN":row["official_level5_or_WIN"],
     "right_bbox":right_bbox,
     "upper_bbox":row["source_upper_bar_selected_bbox"],
     "cup_first_full":cup["source_first_full_by_cup"],
     "four_full_frames":cup["source_four_full_frame_indices"],
     "native_left_wall_frame":row["original_sdk_first_left_measured_frame"],
    },sort_keys=True),flush=True)
 if len(rows)!=12 or len(root_hashes)!=1:
  raise AssertionError("Original SDK source root mismatch or missing witnesses")
 for name,_ in FROZEN:
  pair=[r for r in rows if r["condition"]==name]
  if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"}:
   raise AssertionError("Missing original SDK independent entrances")
  for field in ("source_right_bar_selected_bbox","source_upper_bar_selected_bbox",
    "original_sdk_level","original_sdk_state","official_level5_or_WIN",
    "source_observed_cup_timing","native_source_report",
    "original_sdk_first_left_measured_frame",
    "source_before_pour_hash","source_final_returned_hash"):
   if pair[0][field]!=pair[1][field]:
    raise AssertionError("Authentic A/B SDK mismatch "+name+"."+field)
 results={
  "kind":"SP80_STAGE4_ORIGINAL_SDK_RIGHT_HORIZONTAL_BY_UPPER_VERTICAL_INTERACTION",
  "native_original_sdk_reset_count":len(rows),
  "official_level_counts":dict(Counter(str(x["original_sdk_level"]) for x in rows)),
  "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
  "frozen_factorial_native_cases":FROZEN,
  "original_sdk_witness_source_records":rows,
  "interpretation_boundary":"Two independent original SDK entrance histories per condition; cup observations and border regions are visual outputs, not a game model or official completion rule."}
 arg.out.parent.mkdir(parents=True,exist_ok=True)
 arg.out.write_text(json.dumps(results,indent=2)+"\n")
 np.savez_compressed(arg.out.with_suffix(".npz"),**saved)
 print("ARC4_RIGHT_UPPER_FACTOR_SUMMARY "+json.dumps({
  "genuine_sdk_resets":len(rows),
  "official_levels":results["official_level_counts"],
  "official_level5_or_WIN_count":results["official_level5_or_WIN_count"],
  "source_controls":{name:{
    "native_right_bbox":next(r["source_right_bar_selected_bbox"] for r in rows if r["condition"]==name),
    "native_upper_bbox":next(r["source_upper_bar_selected_bbox"] for r in rows if r["condition"]==name),
    "cup_first_full":next(r["source_observed_cup_timing"]["source_first_full_by_cup"] for r in rows if r["condition"]==name),
    "four_full_frames":next(r["source_observed_cup_timing"]["source_four_full_frame_indices"] for r in rows if r["condition"]==name),
    "native_left_frame":next(r["original_sdk_first_left_measured_frame"] for r in rows if r["condition"]==name)}
   for name,_ in FROZEN}
 },sort_keys=True),flush=True)

if __name__=="__main__":
 main()
