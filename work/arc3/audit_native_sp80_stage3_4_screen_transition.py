"""Read official native SDK stage3-success and stage4-nonadvance border timelines.

Compute original pre-ACTION5-vs-returned-frame changes on fixed screen
subwindows without guessing boundary physics. Explicitly distinguish a
terminal screen transition from preceding animation-frame changes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

AREAS={
 "measured_left_x2_4_y2_61": (slice(2,62),slice(2,5)),
 "measured_right_x59_61_y2_61": (slice(2,62),slice(59,62)),
 "measured_top_y2_4_x2_61": (slice(2,5),slice(2,62)),
 "measured_bottom_y59_62_x2_61": (slice(59,63),slice(2,62)),
 "entire_left_six_x0_5":(slice(0,64),slice(0,6)),
 "entire_right_six_x58_63":(slice(0,64),slice(58,64)),
 "entire_top_six_y0_5":(slice(0,6),slice(0,64)),
 "entire_bottom_six_y58_63":(slice(58,64),slice(0,64)),
}

def screen_events(before,frames):
 if before.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
  raise AssertionError("Actual original native SDK frames required")
 out={}
 for name,area in AREAS.items():
  changed=[int(np.count_nonzero(frame[area]!=before[area])) for frame in frames]
  p14=[i for i,frame in enumerate(frames) if np.any((before[area]==1)&(frame[area]==14))]
  observed=[i for i,c in enumerate(changed) if c]
  out[name]={
    "first_change":observed[0] if observed else None,
    "last_change":observed[-1] if observed else None,
    "first_source_1_to_14":p14[0] if p14 else None,
    "max_changed_pixels":max(changed),
    "penultimate_changed_pixels":changed[-2],
    "returned_terminal_changed_pixels":changed[-1],
    "only_terminal_frame_changed":observed==[len(frames)-1],
  }
 return {
   "frame_count":int(len(frames)),
   "source_areas":out,
   "entire_final_vs_before_pixels":int(np.count_nonzero(before!=frames[-1])),
   "interior_y0_62_final_vs_before_pixels":int(np.count_nonzero(before[:63,:]!=frames[-1,:63,:])),
   "last_row_y63_final_vs_before_pixels":int(np.count_nonzero(before[63,:]!=frames[-1,63,:])),
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--json",type=Path,required=True)
 p.add_argument("--npz",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 opts=p.parse_args()
 original=json.loads(opts.json.read_text())
 if original.get("kind")!="SP80_ORIGINAL_SDK_CONFIRMED_LEVEL3_SUCCESS_VS_LEVEL4_NONADVANCE" or original.get("original_native_resets")!=4:
  raise AssertionError("Require the exact successful vs nonadvancing original SDK native run")
 records=[]
 with np.load(opts.npz,allow_pickle=False) as native:
  for row in original["native_original_source_rows"]:
   condition=row["condition"];witness=row["witness"]
   program=next(word for name,word in original["frozen_comparison_cases"] if name==condition)
   n=len(program.split())
   a=condition+"_"+witness+"_"
   before_success=native[a+"entry3_33"][-1]
   successful=native[a+"entry3_34"]
   before_fail=native[a+"stage4_"+str(n-1)][-1]
   failing=native[a+"stage4_"+str(n)]
   good_receipt=row["genuine_stage3_success"]["original_action_receipt"]
   bad_receipt=row["genuine_stage4_nonadvance"]["original_action_receipt"]
   if (good_receipt["sdk_level_before"],good_receipt["sdk_level_after"])!=(3,4):
    raise AssertionError("Actual SDK stage3 success missing")
   if (bad_receipt["sdk_level_before"],bad_receipt["sdk_level_after"])!=(4,4):
    raise AssertionError("Actual SDK stage4 nonadvance missing")
   records.append({"condition":condition,"witness":witness,
     "actual_stage3_success":screen_events(before_success,successful),
     "actual_stage4_nonadvance":screen_events(before_fail,failing),
     "official_sdk_receipts":{"advancing":good_receipt,"nonadvancing":bad_receipt}})
 if len(records)!=4:raise AssertionError("Original native records absent")
 for label in ("four_cup_transient","three_cup_negative"):
  two=[r for r in records if r["condition"]==label]
  if len(two)!=2 or {x["witness"] for x in two}!={"A","B"}:
   raise AssertionError("Original SDK native A/B witnesses missing")
  for name in ("actual_stage3_success","actual_stage4_nonadvance","official_sdk_receipts"):
   if two[0][name]!=two[1][name]:raise AssertionError("Native exact A/B source differs")
  observed=two[0]
  successful_area=observed["actual_stage3_success"]["source_areas"]["measured_left_x2_4_y2_61"]
  fail_area=observed["actual_stage4_nonadvance"]["source_areas"]["measured_left_x2_4_y2_61"]
  if successful_area["first_change"]!=29 or not successful_area["only_terminal_frame_changed"]:
   raise AssertionError("Original level3 successful left screen-redraw event differs")
  if fail_area["first_change"] is not None:
   raise AssertionError("Original level4 nonadvance unexpectedly changes measured left screen")
 summary={
  "kind":"ORIGINAL_SP80_STAGE3_SUCCESS_STAGE4_NONADVANCE_SCREEN_AREA_TIMELINE",
  "source_native_sdk_run":39762841397,
  "source_raw_sdk_artifact":12418353014,
  "original_sdk_independent_resets":len(records),
  "source_original_receipts_and_screen_areas":records,
  "interpretation_boundary":"Differences between successful and nonadvancing returned screens are observed consequences, not inferred causes or source game win predicates."
 }
 opts.out.parent.mkdir(parents=True,exist_ok=True)
 opts.out.write_text(json.dumps(summary,indent=2)+"\n")
 print("ARC4_SCREEN_AREA_TIMELINE "+json.dumps({
  "original_sdk_resets":len(records),"source_AGREES_A_B":True,
  "official_success":{"levels":"3->4",
    "first_left_wall_change":records[0]["actual_stage3_success"]["source_areas"]["measured_left_x2_4_y2_61"]["first_change"],
    "terminal_left_wall_different_pixels":records[0]["actual_stage3_success"]["source_areas"]["measured_left_x2_4_y2_61"]["returned_terminal_changed_pixels"],
    "final_total_screen_changed_pixels":records[0]["actual_stage3_success"]["entire_final_vs_before_pixels"]},
  "official_nonadvance":{"levels":"4->4",
    "first_left_wall_change":records[0]["actual_stage4_nonadvance"]["source_areas"]["measured_left_x2_4_y2_61"]["first_change"],
    "terminal_left_wall_different_pixels":records[0]["actual_stage4_nonadvance"]["source_areas"]["measured_left_x2_4_y2_61"]["returned_terminal_changed_pixels"],
    "final_total_screen_changed_pixels":records[0]["actual_stage4_nonadvance"]["entire_final_vs_before_pixels"]}
 },sort_keys=True))
if __name__=="__main__":
 main()
