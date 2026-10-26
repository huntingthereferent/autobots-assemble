"""Continue original SP80 mistake-led A/B from the *observed* selected-L UP failure.

The independently repeated true SDK workflow #40395216888 observed:
palette15 L selected and moved RIGHT => palette9 selected 27px L at
x20..25,y35..40. Direct UP moved this same selection to y32..37.
The lateral cup remains 0/45 and original source6 water first appears
at x11..13,y5. This file does not load any public action solution.

No replacement game, idealized board, claimed win, or F3-native equivalence.
Each candidate actually replays its rooted history under Arcade.NORMAL;
even worse failures are retained with their complete source SDK frames.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_ab_operating_loop import one, describe, select_branch
from .native_sp80_stage4_ab_selected_L_continuity import (
    TRUE_PREVIOUS_SELECTED_L, selected_display_coords,
)
from .native_sp80_multi_select import parse_plan

# Native action 1, actually selected by earlier A/B. No re-selection:
# palette15 -> palette9 is a display/state transition of the same piece.
OBSERVED_FAILED_PARENT = TRUE_PREVIOUS_SELECTED_L + " 1"
assert len(parse_plan(OBSERVED_FAILED_PARENT)) < 58


def actual_selected(trial):
    """Read selection from actual SDK last frame before ACTION5, not a model."""
    region = selected_display_coords(trial["pre"])
    return {"palette9_selected": region,
            "original_last_action_receipt": trial["ledger"][-2]
            if len(trial["ledger"]) >= 2 else None}


def contrast(parent, candidate):
    a, b = parent["measure"], candidate["measure"]
    summary = describe(parent, candidate)
    summary.update({
        "parent_actual_source6_first_at_floor":
            a.get("observed_first_source6_near_top_floor"),
        "candidate_actual_source6_first_at_floor":
            b.get("observed_first_source6_near_top_floor"),
        "parent_cup_counts": a.get("four_native_cup_peak_counts"),
        "candidate_cup_counts": b.get("four_native_cup_peak_counts"),
        "parent_top_warning": a.get("floor_lines", {}).get("top"),
        "candidate_top_warning": b.get("floor_lines", {}).get("top"),
        "candidate_selected_original_L": selected_display_coords(candidate["pre"]),
        "official_native_status": {
            "level": b["official_sdk_level"],
            "state": b["official_sdk_state"],
            "advanced": b["official_level5_or_WIN"],
        },
    })
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    witness, entry = STAGE1_WITNESSES[0]
    parent = one("observed_original_selected_L_UP_failure", witness, entry,
                 OBSERVED_FAILED_PARENT + " 5")
    before = selected_display_coords(parent["pre"])
    if not before or before["original_selected_source9_pixels"] != 27:
        raise RuntimeError(
            "Source selected-L referent changed; preserve actual SDK failure")
    if before["original_selected_min_y"] != 32 or before["original_selected_max_y"] != 37:
        raise RuntimeError("Source selected L is not the observed UP failure")
    # This is referent validation, not rejection of an unhelpful movement.
    if parent["measure"]["four_native_cup_peak_counts"]["lateral"] != 0:
        raise RuntimeError("Prior missing lateral-cup error no longer matches source")
    records = [parent]
    chain = []
    rooted = OBSERVED_FAILED_PARENT
    for i in range(2):
        # Round zero compares left/right from the genuine selected-L-UP
        # failure. Round one selects opposing directions from the NEW
        # observed error, after the chosen round-zero movement.
        err = parent["measure"]["observed_error"]
        if parent["measure"]["official_level5_or_WIN"]:
            break
        selection = selected_display_coords(parent["pre"])
        if not selection or selection["original_selected_source9_pixels"] != 27:
            chain.append({
                "round": i, "observed_source_boundary":
                "No selected 27-pixel original SDK L remains; stop native actions",
                "last_observed_error": err,
                "selected_palette9": selection,
            })
            break
        directions = (3, 4) if i == 0 else (
            (1, 2) if err.get("kind") == "observed_unfilled_cup" else (3, 4))
        pair = []
        for name, action in zip(("A", "B"), directions):
            trial = one(f"selected_L_follow_{i}_{name}", witness, entry,
                        rooted + f" {action} 5")
            records.append(trial)
            pair.append(trial)
        # Retain both original SDK failures. The movement's evidence,
        # not an assumed acceptable outcome, determines the next parent.
        chosen, reason = select_branch(parent, *pair)
        item = {
            "round": i,
            "actual_previous_mistake": err,
            "original_selected_source_object": selection,
            "opposite_legal_native_actions": list(directions),
            "actual_original_sdk_A_B": [
                {"case": t["case"], "word": t["word"],
                 "actual_source_difference": contrast(parent, t)}
                for t in pair
            ],
            "followed_real_movement": chosen["case"],
            "why": reason,
        }
        chain.append(item)
        print("SP80_SELECTED_L_NEXT_AB " + json.dumps({
            "round": i, "old_error": err,
            "actions": list(directions),
            "differences": [contrast(parent, t) for t in pair],
            "followed": chosen["case"], "reason": reason,
        }, sort_keys=True), flush=True)
        parent = chosen
        rooted = chosen["word"].rsplit(" 5", 1)[0]

    # An entirely independent original Stage0->Stage4 entrance is an
    # observation check, not a precondition for trying failed actions.
    second_witness, second_entry = STAGE1_WITNESSES[1]
    replicate = one("second_real_SDK_entry_of_chosen_correction",
                    second_witness, second_entry, parent["word"])
    records.append(replicate)
    equal = (
        replicate["measure"]["official_sdk_level"] ==
        parent["measure"]["official_sdk_level"] and
        replicate["measure"].get("source6_full_animation_digest") ==
        parent["measure"].get("source6_full_animation_digest")
    )
    native = {}
    receipts = []
    for t in records:
        for key, frames in t["source"].items():
            if key == "entry3_34" or key.startswith("stage4_"):
                native[f'{t["case"]}_{t["witness"]}_{key}'] = frames
        receipts.append({key: val for key, val in t.items()
                         if key not in ("source", "pre", "frames")})
    report = {
        "kind": "ORIGINAL_SP80_AB_SELECTED_L_UP_ERROR_FOLLOW",
        "source_prior_native_workflow": 40395216888,
        "rooted_owned_failed_parent": OBSERVED_FAILED_PARENT,
        "parent_selected_L": before,
        "parent_observed_failure": records[0]["measure"]["observed_error"],
        "genuine_sdk_game_count": len(records),
        "original_sdk_observed_movement_chain": chain,
        "replay_second_independent_source_agrees": equal,
        "native_original_game_level5_or_win_cases": [
            t["case"] for t in records if t["measure"]["official_level5_or_WIN"]],
        "complete_native_action_receipts": receipts,
        "original_sdk_stage4_roots": sorted({
            t.get("native_root") for t in records if t.get("native_root")}),
        "external_winning_action_program_used": False,
        "separate_F3_48_math_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **native)
    print("SP80_SELECTED_L_NEXT_AB_RESULT " + json.dumps({
        "source_workflow": 40395216888,
        "actual_native_games": len(records),
        "second_entrance_matches": equal,
        "official_progress_cases": report["native_original_game_level5_or_win_cases"],
        "last_observed_mistake": parent["measure"]["observed_error"],
        "followed_native_word": parent["word"],
    }, sort_keys=True), flush=True)
    if not equal:
        raise AssertionError(
            "Real original SDK independent entrances disagree; evidence saved")


if __name__ == "__main__":
    main()
