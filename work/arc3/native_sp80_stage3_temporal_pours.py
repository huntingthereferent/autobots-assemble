"""Original SDK SP80 level3 two-pour temporal contrasts.

Source: merged PR #287, native run #39475858637. Its 128 genuinely reset
games all remained at official level3, including screen-pour effects that
lit all four observed lower palette regions. These are not goal criteria.

This intervention tests ACTION5 timing and post-pour reconfiguration,
not another broad single-pour geometry sweep. Every case uses the original
Arcade.NORMAL SP80 environment and the two verified level3 entry witnesses.
Only official SDK levels_completed >= 4 or WIN counts as advancement.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_stage3_source_guided_search import feedback
from .native_sp80_legal_pairs import hash_frame

# These exact source-screen movements were observed in run #39475858637.
# "Four group" describes the transient color feedback, NOT an official goal.
MIDDLE4 = "6@10,30 4 4 4 4"
MIDDLE3 = "6@10,30 4 4 4"
BOTTOM1 = "6@40,42 4"
FOUR = MIDDLE4 + " " + BOTTOM1
THREE = MIDDLE3 + " " + BOTTOM1

FROZEN = (
    ("root_once", "5"),
    ("root_twice", "5 5"),
    ("root_three_times", "5 5 5"),
    ("four_group_single_pour", FOUR + " 5"),
    ("four_group_repeat_pour", FOUR + " 5 5"),
    ("four_group_root_pour_first", "5 " + FOUR + " 5"),
    ("four_group_mid_pour_first", MIDDLE4 + " 5 " + BOTTOM1 + " 5"),
    ("three_group_repeat_pour", THREE + " 5 5"),
    ("three_group_mid_pour_first", MIDDLE3 + " 5 " + BOTTOM1 + " 5"),
    # Following the initial native pour, make a second source movement and pour.
    # x44,y42 stays inside the actually shifted bottom band for both directions.
    ("four_group_bottom_left_after_pour", FOUR + " 5 6@44,42 3 5"),
    ("four_group_bottom_right_after_pour", FOUR + " 5 6@44,42 4 5"),
    ("four_group_middle_left_after_pour", FOUR + " 5 6@34,30 3 5"),
    ("four_group_middle_right_after_pour", FOUR + " 5 6@34,30 4 5"),
    ("four_group_lower_left_after_pour", FOUR + " 5 6@46,33 3 5"),
    ("four_group_upper_left_after_pour", FOUR + " 5 6@20,18 3 5"),
    ("four_group_upper_right_down_after_pour", FOUR + " 5 6@40,18 2 5"),
    ("four_group_bottom_up_after_pour", FOUR + " 5 6@44,42 1 5"),
    ("four_group_bottom_down_after_pour", FOUR + " 5 6@44,42 2 5"),
    ("top_right2_three_group_single_pour", "6@20,18 4 4 " + THREE + " 5"),
    ("top_right2_three_group_repeat_pour", "6@20,18 4 4 " + THREE + " 5 5"),
)

assert len(FROZEN) == len({name for name, _ in FROZEN}) == 20
assert len(STAGE1_WITNESSES) == 2
assert all(
    1 <= sum(int(a == 5) for a, _ in parse_plan(word)) <= 3
    and parse_plan(word)[-1][0] == 5
    and len(parse_plan(word)) <= 25
    for _, word in FROZEN
)


def compact_events(row):
    # Full SDK frame arrays retained separately in NPZ, not dropped.
    return [{key: value for key, value in event.items()
             if key != "full_original_source_frame_ledger"}
            for event in row["full_original_sdk_action_events"]]


def source_pours(root, stacks, program):
    """Check actual native animation after each ACTION5, not just final pour."""
    actions = parse_plan(program)
    results = []
    for index, (action, _) in enumerate(actions, 1):
        if action != 5:
            continue
        key = "stage3_" + str(index)
        if key not in stacks:
            # A witnessed level change/terminal may stop the native trial early.
            results.append({"action_index": index,
                            "status": "NOT_EXECUTED_SOURCE_STOPPED"})
            continue
        before = root if index == 1 else stacks["stage3_" + str(index - 1)][-1]
        returned = stacks[key]
        results.append({
            "action_index": index,
            "status": "ACTUAL_SOURCE_SDK_POUR",
            "source_frames": len(returned),
            "source_pre_pour_sha256": hash_frame(before),
            "source_post_pour_sha256": hash_frame(returned[-1]),
            "observed_only_relative_to_actual_pre_pour": feedback(before, returned),
            "observed_only_relative_to_stage3_root": feedback(root, returned),
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    records = []
    source_frames = {}
    roots = set()
    for name, word in FROZEN:
        for witness, entry in STAGE1_WITNESSES:
            row, stacks = real_trial(witness, entry, name, word)
            root = stacks["entry2_11"][-1]
            roots.add(row["original_verified_stage3_root"]["original_source_sha256"])
            report = {
                "frozen_case": name,
                "source_witness": witness,
                "original_native_stage3_word": word,
                "official_sdk_final_level": row["official_original_final_level"],
                "official_sdk_final_state": row["official_original_final_state"],
                "official_sdk_level4_or_WIN": row["official_original_level4_or_WIN"],
                "sdk_trial_disposition": row["trial_disposition"],
                "genuine_native_pours": source_pours(root, stacks, word),
                "all_original_sdk_action_receipts": compact_events(row),
            }
            records.append(report)
            for phase, returned in stacks.items():
                source_frames[f"{name}_{witness}_{phase}"] = returned
            print("ORIGINAL_SP80_TEMPORAL_SOURCE_CASE " + json.dumps({
                key: value for key, value in report.items()
                if key != "all_original_sdk_action_receipts"
            }, sort_keys=True), flush=True)

    if len(records) != 40 or len(roots) != 1:
        raise AssertionError("Original independent level3 source witnesses missing or different")
    outcomes = Counter(str(r["official_sdk_final_level"]) for r in records)
    successes = [
        {"case": r["frozen_case"], "witness": r["source_witness"],
         "level": r["official_sdk_final_level"], "state": r["official_sdk_final_state"],
         "native_word": r["original_native_stage3_word"]}
        for r in records if r["official_sdk_level4_or_WIN"]
    ]
    summary = {
        "kind": "ACTUAL_SP80_STAGE3_SOURCE_TWO_POUR_TEMPORAL_CONTRAST",
        "original_antecedent_trial": 39475858637,
        "native_verified_level3_entry_witnesses": [name for name, _ in STAGE1_WITNESSES],
        "prospectively_frozen_original_native_words": FROZEN,
        "genuine_independently_reset_original_sdk_games": len(records),
        "verified_original_stage3_root_sha256": next(iter(roots)),
        "source_native_official_level4_or_WIN_count": len(successes),
        "original_sdk_level_counts": dict(outcomes),
        "native_original_successes": successes,
        "genuine_native_source_records": records,
        "boundary": (
            "Each transient lower-band palette11->13 change is observed only. "
            "Temporal ACTION5 contrast does not decode the hidden goal. "
            "Only official original SDK level>=4 or WIN advances SP80. "
            "All SDK-returned raw frames are kept in NPZ. "
            "No new engine, fabricated impact, F3 mapping, other lane changes, "
            "or license changes."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"), **source_frames)
    print("ORIGINAL_SP80_TEMPORAL_SUMMARY " + json.dumps({
        key: value for key, value in summary.items()
        if key not in ("prospectively_frozen_original_native_words",
                       "genuine_native_source_records")
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
