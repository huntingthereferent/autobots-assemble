"""Genuine SP80 level1 ACTION4-count transfer test, properly selected bars.

A separate original SDK stage0 holdout observed native progression after
exactly three ACTION4 uses followed by ACTION5. That is stage0 evidence,
NOT an assumed stage1 rule. Prospectively test native stage1 ACTION4
counts 0..6 for each of three correctly clicked source objects and a
no-click control. Two genuine independent reset SP80 games per cell.
Preserve every returned source SDK image, legal action, click pixel,
official levels_completed and WIN/GAME_OVER, including counterexamples.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from .native_sp80_action5_frame_stacks import one

TARGETS=(
  ("none",""),
  ("first_selected","6@24,37"),
  ("lower_color8","6@32,25"),
  ("upper_color8","6@12,17"),
)
COUNTS=tuple(range(7))
TRIALS=tuple(
  (target,k," ".join([click]+["4"]*k+["5"]).strip())
  for target,click in TARGETS for k in COUNTS
)
RESETS=2
assert len(TRIALS)==28 and RESETS==2

def analyze_trial(target,k,record,raw):
    action5=[e for e in record["real_sdk_observation_ledger"]
             if e["phase"]=="context" and e["native_action_id"]==5]
    last=action5[-1] if action5 else None
    result={
       "native_bar_target":target,
       "source_number_ACTION4":k,
       "replicate":record["replicate"],
       "sdk_actual_level2_or_win":record["native_level2_or_win"],
       "sdk_actual_level":record["original_last_source_level"],
       "sdk_actual_state":record["original_last_source_state"],
       "native_disposition":record["actual_source_disposition"],
       "native_sdk_actions":record["actual_native_calls"],
       "native_ACTION5_called":bool(last),
       "native_ACTION5_original_sdk_returned_frames":(
           last.get("source_animation",{}).get("true_original_returned_frames")
           if last else None),
       "native_ACTION5_sdk_level_after":last.get("original_source_level_after") if last else None,
       "native_ACTION5_preimage_color9_bbox":None,
       "native_ACTION5_postimage_color9_bbox":None,
       "native_ACTION5_preimage_color8_count":None,
       "real_native_clicks":[{
           "xy":e["native_click_xy"],
           "pre_click_actual_color":e["actual_native_pre_click_pixel"]
       } for e in record["real_sdk_observation_ledger"]
         if e["phase"]=="context" and e["native_action_id"]==6],
    }
    if last is not None and "source_animation" in last:
        idx=last["phase_action_number"]
        before=raw["entry_6"][-1] if idx==1 else raw["context_"+str(idx-1)][-1]
        after=raw["context_"+str(idx)][-1]
        for prefix,arr in (("preimage",before),("postimage",after)):
            y,x=np.nonzero(arr==9)
            result["native_ACTION5_"+prefix+"_color9_bbox"]=(
               [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
               if len(x) else None)
        result["native_ACTION5_preimage_color8_count"]=int(np.count_nonzero(before==8))
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    allrows,frames,summary=[],{},defaultdict(list)
    for target,k,word in TRIALS:
      for rep in range(RESETS):
        trial,raw=one(target+"_k"+str(k),word,rep)
        entry=analyze_trial(target,k,trial,raw)
        trial["original_source_ordinal_transfer_observation"]=entry
        allrows.append(trial)
        summary[(target,k)].append(entry)
        for phase,stack in raw.items():
            frames[f"{target}_k{k}_reset{rep}_{phase}"]=stack
    bytarget={}
    for target,_ in TARGETS:
      bytarget[target]={
         str(k):{
            "actual_sdk_levels":[r["sdk_actual_level"] for r in summary[(target,k)]],
            "actual_sdk_states":[r["sdk_actual_state"] for r in summary[(target,k)]],
            "native_level2_or_WIN":[r["sdk_actual_level2_or_win"] for r in summary[(target,k)]],
            "SDK_ACTION5_returned_frame_counts":[r["native_ACTION5_original_sdk_returned_frames"] for r in summary[(target,k)]],
            "source_original_preimage_color9_bboxes":[r["native_ACTION5_preimage_color9_bbox"] for r in summary[(target,k)]],
            "source_original_postimage_color9_bboxes":[r["native_ACTION5_postimage_color9_bbox"] for r in summary[(target,k)]],
            "source_dispositions":[r["native_disposition"] for r in summary[(target,k)]],
         } for k in COUNTS
      }
    payload={
        "kind":"GENUINE_SP80_STAGE1_A4_ORDINAL_TRANSFER_WITH_COORDINATE_SELECTION",
        "predeclared_source_coordinate_targets":TARGETS,
        "predeclared_ACTION4_counts":COUNTS,
        "independent_games_per_cell":RESETS,
        "genuine_source_native_games":len(allrows),
        "original_SDK_action_calls":sum(t["actual_native_calls"] for t in allrows),
        "original_SDK_level2_or_WIN_count":sum(t["native_level2_or_win"] for t in allrows),
        "source_dispositions":dict(Counter(t["actual_source_disposition"] for t in allrows)),
        "native_original_source_scorecard_by_selected_target_and_A4_count":bytarget,
        "full_original_SDK_native_source_trials":allrows,
        "limitations":"Stage0 ACTION4 ordinal result does not transfer by assumption. This is original SP80 level1 native SDK action observation only. Each ACTION6 uses explicit real x/y and pixel at click is retained. Full ordered SDK returned frames saved. Only official level2/WIN establishes game progress.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("SP80_STAGE1_A4_TRANSFER "+json.dumps({
      k:v for k,v in payload.items() if k!="full_original_SDK_native_source_trials"
    },sort_keys=True))
    if len(allrows)!=len(TRIALS)*RESETS:
      raise RuntimeError("Native SDK reset count does not match frozen test")

if __name__=="__main__":main()
