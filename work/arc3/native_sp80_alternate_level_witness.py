"""Independent official native SP80 check of newly witnessed alternate level prefix.

The PR #122 follow-up long-history experiment found on two fresh resets:
  native 545454544 had first native level counter 0->1 at action 7,
  so its seven-letter prefix 5454545 is a NEW positive native hypothesis.

BEFORE this independent check, freeze negative and positive controls:
  545454  (six-action prefix, previously not a level win)
  5454545 (new positive seven-action candidate)
  454545  (previous independent six-action positive control)
  4545454 (positive control with one unnecessary trailing control)

Run three independent real public native resets per word. Stop at
native level transition, and retain true level counters, actual
native frame arrays and native GameState. This records one-level
progress only, not entire game WIN or mathematical Window48 F3.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode

from .native_sp80_level_recheck import replay, GAME


WORDS = ("545454", "5454545", "454545", "4545454")
FRESH_RESETS_PER_WORD = 3


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/sp80-alternate-level-witness.json"))
    args=parser.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    frames={}
    for word in WORDS:
        for reset in range(FRESH_RESETS_PER_WORD):
            row,raw=replay(arcade,word,reset)
            records.append(row)
            frames[f"{word}_reset{reset}"]=raw
    per_word={}
    for word in WORDS:
        subset=[x for x in records if x["word"]==word]
        per_word[word]={
            "independent_native_resets":len(subset),
            "actual_native_actions":sum(x["native_action_count"] for x in subset),
            "level_progress_replays":sum(x["actual_level_progression"] for x in subset),
            "first_level_change_action_numbers":[
                x["first_level_change_at_action"] for x in subset
            ],
            "level_counter_changes":[
                [x["root_levels_completed"],x["last_levels_completed"]]
                for x in subset],
            "native_terminal_states":[x["terminal_native_state"] for x in subset],
            "statuses":[x["status"] for x in subset],
            "root_frame_hashes":sorted({x["root_hash"] for x in subset}),
        }
    outcome={
        "kind":"INDEPENDENT_SP80_ALTERNATE_NATIVE_ONE_LEVEL_PROGRESS_WITNESS",
        "source":"official native arc-agi Arcade NORMAL public sp80",
        "prespecified_positive_and_negative_words":list(WORDS),
        "fresh_resets_per_word":FRESH_RESETS_PER_WORD,
        "actual_native_actions":sum(x["native_action_count"] for x in records),
        "native_reset_count":len(records),
        "per_word":per_word,
        "source_owned_per_native_action_records":records,
        "boundary":(
            "Independent predeclared native action word control, no saved "
            "winning route or native game source. Evidence is a single "
            "native level counter advancement 0->1 when observed; do NOT "
            "interpret as a full game WIN or a mathematical F3-48 law. "
            "Original 48 laws and agent remain unchanged."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("SP80_ALTERNATE_LEVEL_WITNESS "+json.dumps({
        "native_resets":outcome["native_reset_count"],
        "native_actions":outcome["actual_native_actions"],
        "per_word":per_word,
        "record":str(args.out),"frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))


if __name__=="__main__":
    main()
