"""Original native SP80 stage1 mixed-four action and paired-control study.

The original game advertised six legal native actions. Bounded source
tests of two-action words showed interior restoration from the genuine
stage1 root under 12/21,34/43,56/65, but not entire state restoration.
This trial predeclares six mixed four-action words and freezes those
six previous pair controls, on TWO fresh original resets per word.
No presumed global inverse, hidden-state equality or F3-48 mapping.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_legal_pairs import one

MIXED_FOUR=("1324","3142","1423","2314","1234","4321")
CONTROLS=("12","21","34","43","56","65")
WORDS=MIXED_FOUR+CONTROLS
RESETS=2
assert len(set(WORDS))==12
assert all(len(w)==4 and set(w)<={"1","2","3","4","5","6"}
           for w in MIXED_FOUR)
assert all(len(w)==2 for w in CONTROLS)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    trials,arrays=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            observation,frames=one(word,replicate)
            observation["predeclared_group"]=(
                "MIXED_FOUR_DISCOVERY" if word in MIXED_FOUR
                else "PRIOR_PAIRED_CONTROL")
            trials.append(observation)
            arrays[f"word_{word}_reset{replicate}"]=frames
    results={}
    for word in WORDS:
        rows=[t for t in trials if t["word"]==word]
        results[word]={
            "group":"MIXED_FOUR_DISCOVERY" if word in MIXED_FOUR
                    else "PRIOR_PAIRED_CONTROL",
            "native_state_after_word":[x["last_reported_native_state"] for x in rows],
            "actual_level_after_word":[x["last_reported_native_level"] for x in rows],
            "native_level2_or_WIN":[x["progress_to_level2_or_native_WIN"] for x in rows],
            "status":[x["status"] for x in rows],
            "original_stage1_interior_restored":[x["entire_original_interior_restored_to_stage1_root"] for x in rows],
            "original_stage1_interior_different_pixels":[x["original_interior_pixels_different_from_root"] for x in rows],
            "native_boundary_changed_pixels":[x["original_boundary_y63_pixels_different_from_root"] for x in rows],
            "actual_original_probe_steps":[x["actual_accepted_complete_native_action_frames"] for x in rows],
        }
    summary={
        "kind":"ORIGINAL_SP80_STAGE1_MIXED_FOUR_CONTROL_COMPOSITIONS",
        "predeclared_new_four_action_words":MIXED_FOUR,
        "frozen_two_action_controls":CONTROLS,
        "two_independently_reset_native_stage1_runs_per_word":RESETS,
        "actual_native_resets":len(trials),
        "observed_level2_or_WIN_count":sum(int(t["progress_to_level2_or_native_WIN"]) for t in trials),
        "native_run_status_counts":dict(Counter(t["status"] for t in trials)),
        "word_comparison":results,
        "native_source_records":trials,
        "limits":"Original game API evidence, not global inverse law, source F3 mathematical mapping, game-winning policy or solver. Stage1 root genuine 454545, controls only when native advertised; full NPZ frames retained.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_NATIVE_MIXED_FOUR "+json.dumps({
        k:v for k,v in summary.items() if k!="native_source_records"
    },sort_keys=True))
    if not trials:raise RuntimeError("No original native observations")


if __name__=="__main__":
    main()
