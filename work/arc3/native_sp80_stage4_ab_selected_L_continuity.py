"""Original SP80 A/B correction following actual selected L through palette change.

Authentic own original run #40394846609 revealed:
native L selection ACTION6 at (17,37), pre-click palette15,
then genuine RIGHT action4; the original selected object became
palette9 x20..25,y35..40. Previous runner stopped because it
searched ONLY for palette15, incorrectly treating selected-L display
change as disappearance. This experiment corrects THAT mistake:
do not reselect. Move the still-selected genuine object with
opposing native UP/DOWN and follow the returned source difference.

No published solution or F3-to-native mapping is used or asserted.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_ab_l15_error_follow import ROOTED_OWN_MISTAKE
from .native_sp80_stage4_ab_operating_loop import one,describe,select_branch
from .native_sp80_multi_select import parse_plan
import numpy as np

TRUE_PREVIOUS_SELECTED_L=ROOTED_OWN_MISTAKE+" 6@17,37 4"
assert len(parse_plan(TRUE_PREVIOUS_SELECTED_L))<60

def selected_display_coords(frame):
    coords=np.argwhere(frame==9)
    if not len(coords):return None
    yy,xx=coords[:,0],coords[:,1]
    return {"original_selected_source9_pixels":len(coords),
            "original_selected_min_x":int(xx.min()),
            "original_selected_max_x":int(xx.max()),
            "original_selected_min_y":int(yy.min()),
            "original_selected_max_y":int(yy.max())}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    witness,stage1=STAGE1_WITNESSES[0]
    parent=one("prior_authentic_selected_L",witness,stage1,TRUE_PREVIOUS_SELECTED_L+" 5")
    selected=selected_display_coords(parent["pre"])
    if selected is None or not (selected["original_selected_min_x"]<=20<=selected["original_selected_max_x"]):
        raise AssertionError("Original selected palette9 L object source referent changed")
    if parent["measure"]["four_native_cup_peak_counts"]["lateral"]!=0:
        raise AssertionError("True native lateral-cup mistake changed")
    trials=[parent];pairs=[]
    for side,move in (("A",1),("B",2)):
        trial=one("native_selected_L_"+side,witness,stage1,
                  TRUE_PREVIOUS_SELECTED_L+f" {move} 5")
        trials.append(trial)
        pairs.append({"side":side,"action":move,
                      "native_correction_difference":describe(parent,trial),
                      "official_sdk_level":trial["measure"]["official_sdk_level"],
                      "actual_error":trial["measure"]["observed_error"],
                      "selected_L_before":selected_display_coords(trial["pre"])})
    followed,reason=select_branch(parent,trials[1],trials[2])
    second_w,second_entry=STAGE1_WITNESSES[1]
    repeated=one("independently_verified_selected_L_continuation",
                 second_w,second_entry,followed["word"])
    trials.append(repeated)
    if (repeated["measure"]["official_sdk_level"]!=followed["measure"]["official_sdk_level"]
        or repeated["measure"]["source6_full_animation_digest"]!=
           followed["measure"]["source6_full_animation_digest"]):
        raise AssertionError("Genuine independent original SDK entries disagree")
    print("SP80_NATIVE_SELECTED_L_AB_MOVEMENT "+json.dumps({
        "L_source":selected,
        "opposing_native_actions":[1,2],
        "observed_native_A_B":pairs,
        "continued_true_source":followed["case"],
        "reason":reason
    },sort_keys=True),flush=True)
    arrays={};receipts=[]
    for trial in trials:
        for key,frame in trial["source"].items():
            if key=="entry3_34" or key.startswith("stage4_"):
                arrays[f"{trial['case']}_{trial['witness']}_{key}"]=frame
        receipts.append({k:v for k,v in trial.items() if k not in ("source","pre","frames")})
    report={
      "kind":"ORIGINAL_SDK_OWN_AB_CORRECTED_SELECTED_L_REPRESENTATION",
      "original_source_of_mistake":40394846609,
      "original_verified_pre_click_color":15,
      "original_true_selected_color_after_click_move":9,
      "same_actual_original_selected_object":selected,
      "opposing_original_SDK_action_A_B":pairs,
      "actual_sdk_games":len(trials),
      "next_followed_original_A_B_branch":followed["case"],
      "reason":reason,
      "official_progress_cases":[trial["case"] for trial in trials
                                  if trial["measure"]["official_level5_or_WIN"]],
      "complete_original_native_source_receipts":receipts,
      "public_external_solution_loaded":False,
      "scope":"A/B moves by mistakes, corrections follow original SDK. No external answer imported; separate F3-48 formal model untouched."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_NATIVE_SELECTED_L_AB_SUMMARY "+json.dumps({
       k:v for k,v in report.items()
       if k not in ("opposing_original_SDK_action_A_B","complete_original_native_source_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
