"""Prospective original SP80 stage1 non-restoring native action test.

All six native actions 1..6 are source advertised on the genuine stage1
root. Exact interior restoration from root for reciprocal pairs 12/21,
34/43,56/65 and balanced 1324 etc was SOURCE OBSERVED, not game solving:
level stayed at 1/6, and row63 advanced every action.

Freeze 12 intentionally non-restoring context words with distinct
persistent native action directions and mixed action classes, plus two
balanced timing-matched native negative controls. Every trial must
actually reach stage1 with the original 454545 prefix and check SDK
legal actions on EACH step. Use two independently reset original games
per word. Stop at first native WIN, GAME_OVER, or level change. Measure
levels_completed and true SDK state before interpreting pixel motion.

No automatic AI search, synthetic game, F3 mathematical A/B action map,
claimed solution or hidden state identity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_legal_pairs import one

CANDIDATES=(
    "1"*12, "2"*12, "3"*12, "4"*12,
    "5"*12, "6"*12,
    "13"*8, "31"*8, "15"*8, "35"*8,
    "136"*5, "246"*5,
)
TIMING_CONTROLS=("12"*6, "34"*6)
WORDS=CANDIDATES+TIMING_CONTROLS
RESETS=2
assert len(WORDS)==len(set(WORDS))==14
assert all(12<=len(w)<=16 and set(w)<={"1","2","3","4","5","6"}
           for w in WORDS)
assert len(CANDIDATES)==12 and len(TIMING_CONTROLS)==2


def summarize(trials):
    byword={}
    for word in WORDS:
        matches=[t for t in trials if t["word"]==word]
        byword[word]={
            "class":"NONRESTORING_CANDIDATE" if word in CANDIDATES else "BALANCED_TIMING_CONTROL",
            "genuine_resets":len(matches),
            "requested_context_actions":len(word),
            "source_actions_with_valid_frames":[
                t["actual_accepted_complete_native_action_frames"] for t in matches
            ],
            "native_disposition":[t["status"] for t in matches],
            "actual_levels_completed":[t["last_reported_native_level"] for t in matches],
            "native_SDK_state":[t["last_reported_native_state"] for t in matches],
            "native_level2_or_WIN":[t["progress_to_level2_or_native_WIN"] for t in matches],
            "native_interior_restored":[t["entire_original_interior_restored_to_stage1_root"] for t in matches],
            "native_interior_root_pixel_differences":[t["original_interior_pixels_different_from_root"] for t in matches],
            "native_boundary_root_pixel_differences":[t["original_boundary_y63_pixels_different_from_root"] for t in matches],
        }
    return byword


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    trials,frames={},{}
    rows=[]
    for word in WORDS:
        for reset in range(RESETS):
            trial,full_native_frames=one(word,reset)
            trial["prospectively_assigned_group"]=(
                "NONRESTORING_CANDIDATE" if word in CANDIDATES
                else "BALANCED_TIMING_CONTROL")
            rows.append(trial)
            frames[f"{word}_{reset}"]=full_native_frames
    counts=Counter(row["status"] for row in rows)
    wins=[{"word":t["word"],"replicate":t["replicate"],
           "state":t["last_reported_native_state"],
           "level":t["last_reported_native_level"],
           "after_actions":t["actual_accepted_complete_native_action_frames"]}
          for t in rows if t["last_reported_native_state"]=="WIN"]
    progress=[{"word":t["word"],"replicate":t["replicate"],
               "state":t["last_reported_native_state"],
               "level":t["last_reported_native_level"],
               "after_actions":t["actual_accepted_complete_native_action_frames"]}
              for t in rows if t["last_reported_native_level"]>=2]
    out={
        "kind":"SP80_ORIGINAL_PUBLIC_NATIVE_STAGE1_NONRESTORING_ACTION_HOLDOUT",
        "genuine_predeclared_native_stage1_prefix":"454545",
        "frozen_candidate_words":CANDIDATES,
        "balanced_timing_controls":TIMING_CONTROLS,
        "independent_original_game_resets_per_word":RESETS,
        "actual_original_native_resets":len(rows),
        "original_probe_actions_with_complete_frame":sum(
            t["actual_accepted_complete_native_action_frames"] for t in rows),
        "native_disposition_counts":dict(counts),
        "official_native_WIN_records":wins,
        "official_native_level2_or_later_progress":progress,
        "word_level_observations":summarize(rows),
        "full_source_trial_records":rows,
        "limits":"Only genuine SDK-advertised original native actions1..6 and real levels_completed/WIN. No autonomous policy, hidden-state identification, original mathematical 48-law mapping or inferred level2 from visible pixel movement; interrupted actions unknown.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("SP80_NONRESTORING_LEVEL2 "+json.dumps({
        k:v for k,v in out.items() if k!="full_source_trial_records"
    },sort_keys=True))
    if len(rows)!=len(WORDS)*RESETS:
        raise RuntimeError("Missing actual genuine game resets")


if __name__=="__main__":
    main()
