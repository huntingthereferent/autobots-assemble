"""Held-out original SP80 stage0 ACTION4-count hypothesis, full SDK frames."""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage0_progress_animation import stage0_original_trial

WORDS=(
 ("p1","54445",True),
 ("p2","554445",True),
 ("p3","455445",True),
 ("p4","44545",True),
 ("p5","445545",True),
 ("p6","4555445",True),
 ("p7","5544545",True),
 ("p8","5554445",True),
 ("p9","544455",True),
 ("n1","45545",False),
 ("n2","55445",False),
 ("n3","44555",False),
 ("n4","54455",False),
 ("n5","44445",False),
 ("n6","454445",False),
 ("n7","445445",False),
 ("n8","544445",False),
 ("n9","5544445",False),
)
RESETS=2
assert len(WORDS)==18 and RESETS==2
assert all(
    any(c=="5" and w[:i].count("4")==3 for i,c in enumerate(w))==v
    for _,w,v in WORDS
)

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    records,arrays=[],{}
    for name,word,predicted in WORDS:
        for replicate in range(RESETS):
            result,stacks=stage0_original_trial(name,word,replicate)
            source_events=result["genuine_source_action_records"]
            native_success=next((e["original_word_step"] for e in source_events
               if e.get("native_SDK_level_increase") or e.get("native_SDK_WIN")),None)
            frozen_step=next((i+1 for i,c in enumerate(word)
                if c=="5" and word[:i].count("4")==3),None)
            result["prediction"]={
                "frozen_should_advance":predicted,
                "observed_original_SDK_advanced":bool(native_success is not None),
                "frozen_step":frozen_step,
                "source_actual_advance_step":native_success,
                "matched":native_success==frozen_step,
            }
            records.append(result)
            for phase,arr in stacks.items():
                arrays[f"{name}_reset{replicate}_{phase}"]=arr
    grouped=Counter()
    total_frames=0
    for r in records:
      for e in r["genuine_source_action_records"]:
        stack=e.get("actual_SDK_frame_sequence")
        if not stack:continue
        total_frames+=stack["true_original_returned_frames"]
        if e["native_action"]!=5:continue
        k=(r["frozen_original_word"][:e["original_word_step"]-1].count("4"),
           bool(e["native_SDK_level_increase"]),
           stack["true_original_returned_frames"])
        grouped[k]+=1
    out={
      "kind":"original_sp80_stage0_source_count_heldout",
      "prospectively_frozen_words":WORDS,
      "original_native_resets":len(records),
      "source_SDK_actions":sum(r["actual_SDK_action_count"] for r in records),
      "actual_all_returned_frames":total_frames,
      "exact_source_prediction_matches":sum(r["prediction"]["matched"] for r in records),
      "source_prediction_trials":len(records),
      "source_sdk_level1_advances":sum(r["genuine_level0_to_level1_or_higher"] for r in records),
      "observed_original_A5_by_A4_count_progress_frame_length":[
        {"prior_A4":k[0],"advanced":k[1],"frames":k[2],"observations":v}
        for k,v in sorted(grouped.items())],
      "counterexamples":[{"word":r["frozen_original_word"],"rep":r["replicate"],
          **r["prediction"]} for r in records if not r["prediction"]["matched"]],
      "original_source_native_records":records,
      "limits":"Stage0 only. SDK levels and terminal states are authoritative; complete genuine frame stacks saved. No stage1->2 claim.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**arrays)
    print("SP80_STAGE0_COUNT_HOLDOUT "+json.dumps({
      k:v for k,v in out.items() if k!="original_source_native_records"},sort_keys=True))
if __name__=="__main__":main()
