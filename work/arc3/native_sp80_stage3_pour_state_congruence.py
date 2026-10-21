"""Bounded original SDK SP80 stage3 pour-state observation/congruence trial.

Continues merged native trial PR #330, run #39545364349. Its actual source
frames show identical second ACTION5 result at original root/three-group
arrangements but *different* second final frame under a four-group setup.
Neither source pattern advanced official SDK level3. This trial asks if
visible pre-ACTION5 source state and the same action adequately describe
native returned outcomes across independently witnessed action histories.

No inferred hidden physics/goal, replacement SP80 engine or proxy victory.
Only genuine SDK levels_completed>=4 / WIN signifies level advancement.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

MIDDLE4 = "6@10,30 4 4 4 4"
MIDDLE3 = "6@10,30 4 4 4"
BOTTOM = "6@40,42 4"
FOUR = MIDDLE4 + " " + BOTTOM
THREE = MIDDLE3 + " " + BOTTOM
TOPRIGHT_THREE = "6@20,18 4 4 " + THREE
TOPLEFT_FOUR = "6@20,18 3 3 " + FOUR
POURS = "5 5 5 5 5 5"
THREE_POURS = "5 5 5"

# All pairs are predeclared before any new actual original SDK source calls.
# The same three initial pours permit comparison with the no-intervention
# continuation. '3 4' and '4 3' are *commands*, not assertions of restoration:
# compare actual pre/post SDK source frame hashes to establish restoration.
FROZEN = (
    ("root_six_pours", POURS),
    ("root_reselect_after_three", "5 5 5 6@20,18 " + THREE_POURS),
    ("three_six_pours", THREE + " " + POURS),
    ("four_six_pours", FOUR + " " + POURS),
    ("top_right_three_six_pours", TOPRIGHT_THREE + " " + POURS),
    ("top_left_four_six_pours", TOPLEFT_FOUR + " " + POURS),
    ("four_after_three_bottom_left_right", FOUR + " 5 5 5 6@44,42 3 4 " + THREE_POURS),
    ("four_after_three_bottom_right_left", FOUR + " 5 5 5 6@44,42 4 3 " + THREE_POURS),
    ("four_after_three_bottom_reselect", FOUR + " 5 5 5 6@44,42 " + THREE_POURS),
    ("four_after_three_middle_left_right", FOUR + " 5 5 5 6@34,30 3 4 " + THREE_POURS),
    ("four_after_three_upper_left_right", FOUR + " 5 5 5 6@20,18 3 4 " + THREE_POURS),
    ("four_after_three_upper_down_up", FOUR + " 5 5 5 6@40,18 2 1 " + THREE_POURS),
    ("three_after_three_bottom_left_right", THREE + " 5 5 5 6@44,42 3 4 " + THREE_POURS),
    ("three_after_three_bottom_reselect", THREE + " 5 5 5 6@44,42 " + THREE_POURS),
    ("root_pour_then_four_five_pours", "5 " + FOUR + " 5 5 5 5 5"),
    ("four_after_one_upper_right_return", FOUR + " 5 6@20,18 4 3 5 5 5 5 5"),
)
assert len(FROZEN) == len(set(name for name, _ in FROZEN)) == 16
assert len(STAGE1_WITNESSES) == 2
assert all(
    parse_plan(word)[-1][0] == 5
    and len(parse_plan(word)) <= 25
    and 1 <= sum(a == 5 for a, _ in parse_plan(word)) <= 6
    for _, word in FROZEN
)


def stack_digest(arr):
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def summarize_trial(case, witness, word, row, stacks):
    """Keep all original frame arrays in NPZ; report source-derived receipts."""
    events = row["original_stage3_intervention_events"]
    root = stacks["entry2_11"][-1]
    observations = []
    pours = []
    last_pour_index = 0
    prior_pour_terminal = None
    for index, record in enumerate(events, 1):
        stack = stacks.get("stage3_" + str(index))
        native_action = record.get("original_action")
        receipt = {
            "native_step": index,
            "original_action": native_action,
            "original_click_xy": record.get("original_click_xy"),
            "sdk_level_before": record.get("official_source_level_before"),
            "sdk_level_after": record.get("official_source_level_after"),
            "sdk_state_before": record.get("official_source_state_before"),
            "sdk_state_after": record.get("official_source_state_after"),
            "sdk_source_pre_sha256": record.get("actual_source_before_sha"),
            "sdk_source_post_sha256": record.get("actual_source_after_sha"),
            "original_legal_before": record.get("original_legal_before"),
            "source_admission": record.get("admission", "SDK_RETURNED"),
        }
        if stack is not None:
            frames = np.asarray(stack)
            before = root if index == 1 else stacks["stage3_" + str(index - 1)][-1]
            after = frames[-1]
            if receipt["sdk_source_pre_sha256"] != hash_frame(before):
                raise AssertionError("Original SDK pre-frame SHA disagreement")
            if receipt["sdk_source_post_sha256"] != hash_frame(after):
                raise AssertionError("Original SDK post-frame SHA disagreement")
            receipt.update({
                "original_sdk_animation_frame_count": len(frames),
                "full_sdk_animation_sha256": stack_digest(frames),
                "actual_prepost_changed_pixel_count": int(np.count_nonzero(before != after)),
                "original_sdk_returned_frame_sha256": [hash_frame(f) for f in frames],
            })
            if native_action == 5:
                pours.append({
                    "native_step": index,
                    "official_level_after": receipt["sdk_level_after"],
                    "original_pre_sha256": receipt["sdk_source_pre_sha256"],
                    "original_after_sha256": receipt["sdk_source_post_sha256"],
                    "identical_terminal_image_to_previous_pour": (
                        None if prior_pour_terminal is None
                        else prior_pour_terminal == receipt["sdk_source_post_sha256"]
                    ),
                    "actual_intervening_source_actions": [
                        r["original_action"]
                        for r in observations if last_pour_index < r["native_step"]
                    ],
                    "sdk_animation_frame_count": len(frames),
                    "sdk_animation_sha256": receipt["full_sdk_animation_sha256"],
                })
                prior_pour_terminal = receipt["sdk_source_post_sha256"]
                last_pour_index = index
        observations.append(receipt)

    return {
        "frozen_case": case,
        "independent_sdk_witness": witness,
        "exact_original_native_word": word,
        "verified_source_root_sha256": row["original_verified_stage3_root"]["original_source_sha256"],
        "original_sdk_official_level": row["official_original_final_level"],
        "original_sdk_official_state": row["official_original_final_state"],
        "original_sdk_advanced_to_4_or_WIN": row["official_original_level4_or_WIN"],
        "trial_disposition": row["trial_disposition"],
        "actual_original_sdk_actions": observations,
        "genuine_original_pour_sequence": pours,
    }


def observation_pairs(records):
    """Group only identical source before-frame, action, official level/state.

    An inconsistent next image is an observed-source congruence counterexample,
    NOT an explanation of the unobserved cause. An animation difference with
    same terminal image is separately reported, not called level progress.
    """
    indexed = defaultdict(list)
    for row in records:
        for event in row["actual_original_sdk_actions"]:
            if event.get("full_sdk_animation_sha256") is None:
                continue
            key = (
                event["sdk_source_pre_sha256"], event["original_action"],
                event["sdk_level_before"], event["sdk_state_before"],
            )
            indexed[key].append({
                "case": row["frozen_case"],
                "witness": row["independent_sdk_witness"],
                "native_step": event["native_step"],
                "source_post_sha256": event["sdk_source_post_sha256"],
                "official_sdk_level_after": event["sdk_level_after"],
                "official_sdk_state_after": event["sdk_state_after"],
                "sdk_animation_sha256": event["full_sdk_animation_sha256"],
            })
    comparable = []
    image_divergences = []
    animation_only = []
    for key, entries in sorted(indexed.items(), key=lambda item: str(item[0])):
        if len(entries) < 2:
            continue
        terminal = {(e["source_post_sha256"],
                     e["official_sdk_level_after"],
                     e["official_sdk_state_after"]) for e in entries}
        animations = {e["sdk_animation_sha256"] for e in entries}
        item = {
            "pre_source_sha256": key[0],
            "action": key[1],
            "source_level_before": key[2],
            "source_state_before": key[3],
            "cases": entries,
        }
        comparable.append(item)
        if len(terminal) > 1:
            image_divergences.append(item)
        elif len(animations) > 1:
            animation_only.append(item)
    return {
        "same_observed_prestate_and_action_comparison_classes": len(comparable),
        "different_original_terminal_or_official_outcomes": image_divergences,
        "different_original_returned_animation_only": animation_only,
    }


def self_test():
    """Synthetic controls verify that the comparator does not hide divergence."""
    def rec(name, after, anim):
        return {
            "frozen_case": name, "independent_sdk_witness": "TEST",
            "actual_original_sdk_actions": [{
                "sdk_source_pre_sha256": "shared", "original_action": 5,
                "sdk_level_before": 3, "sdk_state_before": "NOT_FINISHED",
                "sdk_source_post_sha256": after,
                "sdk_level_after": 3, "sdk_state_after": "NOT_FINISHED",
                "full_sdk_animation_sha256": anim, "native_step": 1,
            }],
        }
    equal = observation_pairs([rec("a", "same", "a"), rec("b", "same", "a")])
    changed = observation_pairs([rec("a", "same", "a"), rec("b", "changed", "b")])
    frames_only = observation_pairs([rec("a", "same", "a"), rec("b", "same", "b")])
    assert equal["same_observed_prestate_and_action_comparison_classes"] == 1
    assert not equal["different_original_terminal_or_official_outcomes"]
    assert len(changed["different_original_terminal_or_official_outcomes"]) == 1
    assert not frames_only["different_original_terminal_or_official_outcomes"]
    assert len(frames_only["different_original_returned_animation_only"]) == 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    self_test()
    records, original_arrays, roots = [], {}, set()
    for name, word in FROZEN:
        for witness, entry in STAGE1_WITNESSES:
            row, stacks = real_trial(witness, entry, name, word)
            record = summarize_trial(name, witness, word, row, stacks)
            records.append(record)
            roots.add(record["verified_source_root_sha256"])
            for phase, stack in stacks.items():
                original_arrays[f"{name}_{witness}_{phase}"] = stack
            print("ORIGINAL_SP80_POUR_STATE_CASE " + json.dumps({
                "case": name, "witness": witness,
                "official_level": record["original_sdk_official_level"],
                "sdk_state": record["original_sdk_official_state"],
                "source_pour_terminal_shas": [
                    x["original_after_sha256"] for x in record["genuine_original_pour_sequence"]
                ],
            }, sort_keys=True), flush=True)
    if len(records) != 32 or len(roots) != 1:
        raise AssertionError("Missing genuine independently reset source witnesses")
    source_comparison = observation_pairs(records)
    successes = [
        {"case": r["frozen_case"], "witness": r["independent_sdk_witness"],
         "word": r["exact_original_native_word"],
         "level": r["original_sdk_official_level"],
         "state": r["original_sdk_official_state"]}
        for r in records if r["original_sdk_advanced_to_4_or_WIN"]
    ]
    summary = {
        "kind": "ORIGINAL_SDK_SP80_STAGE3_SOURCE_POUR_STATE_CONGRUENCE",
        "source_antecedent_native_run": 39545364349,
        "original_source_reset_games": len(records),
        "frozen_native_plans": FROZEN,
        "original_source_stage3_root_sha256": next(iter(roots)),
        "original_sdk_final_level_histogram": dict(Counter(
            str(r["original_sdk_official_level"]) for r in records)),
        "genuine_original_source_level4_or_WIN_count": len(successes),
        "genuine_original_source_progress_witnesses": successes,
        "source_observation_sufficiency_test": source_comparison,
        "all_genuine_source_sdk_records": records,
        "limitations": (
            "Pixel SHA+native action congruence is an observational test only. "
            "A difference is not an inferred hidden mechanic, physical cause or "
            "independent proof of game semantics. SDK levels/states alone prove "
            "native progress. All original returned source frames retained in NPZ."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"), **original_arrays)
    print("ORIGINAL_SP80_POUR_STATE_SUMMARY " + json.dumps({
        k: v for k, v in summary.items()
        if k not in ("all_genuine_source_sdk_records", "frozen_native_plans")
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
