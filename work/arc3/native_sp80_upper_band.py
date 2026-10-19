"""Prospective genuine stage1 second color8 band / ACTION5 vs ACTION6.

Original real SP80 stage1 source frames show color8 native pixels near
x8..19,y16..19 and x28..39,y24..27. Previous prospectively tested
color9 contact at lower band (111 then ACTION5) converted 32 native
pixels 9->8 but DID NOT advance level2. The upper band is a
different real visible region. No assumption either region is a goal.

Predeclare genuine ACTION1(up) five times and ACTION3(left) three
times in both orders, plus ACTION5/ACTION6 after movement. Include
two-left partial contact, early no-overlap controls, geometry-only
controls and one follow-up ACTION4. Two independent ORIGINAL Arcade
stage1 native resets per word; stop on native WIN/GAME_OVER or level
change. Outcomes are the SDK LEVEL, STATE and real original frames.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_overlap_intervention import native_trial

WORDS=(
    "11111333","33311111",
    "111113335","111113336",
    "333111115","333111116",
    "11111335","11111336",
    "111113334","1111133354",
    "111115","111116",
    "333115","333116",
)
RESETS=2
assert len(WORDS)==len(set(WORDS))==14
assert all(6<=len(w)<=10 and set(w)<={"1","3","4","5","6"}
           for w in WORDS)
assert RESETS==2


def summarize(rows):
    byword={}
    for word in WORDS:
        trials=[r for r in rows if r["word"]==word]
        byword[word]={
            "native_resets":len(trials),
            "native_actions_with_original_frames":[t["actual_accepted_complete_native_action_frames"] for t in trials],
            "native_SDK_state":[t["last_reported_native_state"] for t in trials],
            "actual_native_levels":[t["last_reported_native_level"] for t in trials],
            "native_level2_or_WIN":[t["progress_to_level2_or_native_WIN"] for t in trials],
            "first_original_color8_decrease_step":[t["first_native_original_color8_count_decrease_step"] for t in trials],
            "final_source_color8_count":[t["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["actual_native_color8_pixels"] for t in trials],
            "final_color9_xy":[t["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["native_color9_xy_bounds"] for t in trials],
            "final_bottom_y63_cleared":[t["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["bottom_row63_cleared_cells"] for t in trials],
            "native_disposition":[t["status"] for t in trials],
        }
    return byword


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    trials,arrays=[],{}
    for word in WORDS:
        for reset in range(RESETS):
            observation,frames=native_trial(word,reset)
            trials.append(observation)
            arrays[f"{word}_{reset}"]=frames
    out={
        "kind":"ORIGINAL_SP80_STAGE1_SECOND_COLOR8_BAND_SOURCE_INTERVENTION",
        "frozen_original_native_words":WORDS,
        "native_resets_per_word":RESETS,
        "authentic_native_reset_count":len(trials),
        "valid_original_action_frames":sum(t["actual_accepted_complete_native_action_frames"] for t in trials),
        "true_native_stage2_or_WIN":sum(int(t["progress_to_level2_or_native_WIN"]) for t in trials),
        "native_source_dispositions":dict(Counter(t["status"] for t in trials)),
        "per_source_word":summarize(trials),
        "original_native_trial_records":trials,
        "limitations":"Original Arcade.NORMAL stage1, native legal ACTION1/3/4/5/6 only; color8/9 band intersection is a screen observation with unknown goal meaning. SDK reported levels and WIN/GAME_OVER are required for progress; no virtual game, solver or F3 generator mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_SECOND_BAND "+json.dumps({
        k:v for k,v in out.items() if k!="original_native_trial_records"
    },sort_keys=True))
    if len(trials)!=len(WORDS)*RESETS:raise RuntimeError("Missing native original games")


if __name__=="__main__":
    main()
