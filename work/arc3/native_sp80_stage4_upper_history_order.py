"""ARC4: genuine original SDK upper-bar action-order source contrast.

Derived from original SDK run #40123855347: all seven controls agree on
earliest row8/frame19 and row5/frame20 off-cup palette6 at x11..13, while
their native cup outcomes differ. This experiment asks whether reverse
order histories with the SAME observed final selected bbox differ in native
cup/border responses. It does not assume identical source state or hidden
physics from equal geometry. Original full SDK frames and A/B entries required.

The frozen parent, existing controls and two fresh original SDK entry
witnesses stay fixed. Only official SDK levels_completed>=5 or WIN counts
as level advancement. Not an ARC-like mathematical surrogate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage4_direct_upper_right1_contrast import (
    PARENT, source_report, comparison,
)

# Both original native witnesses receive the same predeclared seven histories.
CONTROLS = (
    ("reselect", ""),
    ("left1", "3"),
    ("right1", "4"),
    ("left_then_right", "3 4"),
    ("right_then_left", "4 3"),
    ("right_then_left2", "4 3 3"),
    ("left_then_right_then_left", "3 4 3"),
)
MATCHED_PAIRS = (
    ("reselect", "left_then_right"),
    ("reselect", "right_then_left"),
    ("left1", "right_then_left2"),
    ("left1", "left_then_right_then_left"),
    ("right_then_left2", "left_then_right_then_left"),
)
assert len(CONTROLS) == len({name for name, _ in CONTROLS}) == 7
assert len(STAGE1_WITNESSES) == 2
for name, suffix in CONTROLS:
    actions = parse_plan(" ".join(x for x in (PARENT, suffix, "5") if x))
    assert len(actions) <= 23
    assert actions[-1][0] == 5 and sum(a == 5 for a, xy in actions) == 1
    assert all(xy is not None for a, xy in actions if a == 6)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    entries = {}
    raw_source = {}
    roots = set()
    cases = []

    for name, suffix in CONTROLS:
        word = " ".join(x for x in (PARENT, suffix, "5") if x)
        parsed = parse_plan(word)
        for witness, entry in STAGE1_WITNESSES:
            sdk, raw = run_case(name, witness, entry, word)
            root = raw["entry3_34"][-1]
            before = raw["stage4_" + str(len(parsed) - 1)][-1]
            after = raw["stage4_" + str(len(parsed))]
            source = source_report(root, before, after)
            roots.add(source["root_hash"])
            row = {
                "case": name,
                "independent_original_sdk_witness": witness,
                "predeclared_word": word,
                "official_sdk_level": sdk["true_original_sdk_final_level"],
                "official_sdk_state": sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN": sdk["official_original_level5_or_WIN"],
                "native_source_observations": source,
                "original_sdk_action_receipts": sdk["genuine_original_stage4_action_ledger"],
            }
            cases.append(row)
            entries[(name, witness)] = (root.copy(), before.copy(), after.copy())
            for key, frames in raw.items():
                raw_source[name + "_" + witness + "_" + key] = frames
            print("ARC4_ORDER_NATIVE_CASE " + json.dumps({
                "name": name, "witness": witness,
                "sdk_level": row["official_sdk_level"],
                "sdk_state": row["official_sdk_state"],
                "source": source,
            }, sort_keys=True), flush=True)

    if len(roots) != 1 or len(cases) != len(CONTROLS) * 2:
        raise AssertionError("Independent original SDK source root/reset mismatch")
    for name, _ in CONTROLS:
        pair = [row for row in cases if row["case"] == name]
        if len(pair) != 2 or {x["independent_original_sdk_witness"] for x in pair} != {"A", "B"}:
            raise AssertionError("Missing A/B original source witness " + name)
        for field in ("official_sdk_level", "official_sdk_state", "official_level5_or_WIN",
                      "native_source_observations"):
            if pair[0][field] != pair[1][field]:
                raise AssertionError("Native witness disagreement: " + name + " " + field)

    contrasts = []
    for baseline, variant in MATCHED_PAIRS:
        witnesses = []
        for witness, _ in STAGE1_WITNESSES:
            root, base_pre, base_frames = entries[(baseline, witness)]
            other_root, other_pre, other_frames = entries[(variant, witness)]
            if not np.array_equal(root, other_root):
                raise AssertionError("Original SDK roots not identical")
            measured = comparison(base_pre, base_frames, other_pre, other_frames, root)
            left = next(x for x in cases if x["case"] == baseline and
                        x["independent_original_sdk_witness"] == witness)
            right = next(x for x in cases if x["case"] == variant and
                         x["independent_original_sdk_witness"] == witness)
            l_obs, r_obs = left["native_source_observations"], right["native_source_observations"]
            witnesses.append({
                "source_frame_difference": measured,
                "same_observed_selected_bbox": l_obs["selected_bbox"] == r_obs["selected_bbox"],
                "source_selected_bbox_pair": [l_obs["selected_bbox"], r_obs["selected_bbox"]],
                "same_four_cup_frame": l_obs["source_first_four_simultaneous"] ==
                                       r_obs["source_first_four_simultaneous"],
                "native_four_cup_frames": [l_obs["source_first_four_simultaneous"],
                                           r_obs["source_first_four_simultaneous"]],
                "same_original_status": (left["official_sdk_level"],left["official_sdk_state"]) ==
                                        (right["official_sdk_level"],right["official_sdk_state"]),
            })
        if witnesses[0] != witnesses[1]:
            raise AssertionError("Source A/B matched-history contrast mismatch")
        contrasts.append({
            "baseline": baseline,
            "variant": variant,
            "source_observed_comparison": witnesses[0],
            "boundary": "Identical final selected bbox alone does not prove identical source state.",
        })

    advanced = [row for row in cases if row["official_level5_or_WIN"]]
    report = {
        "kind": "ARC4_ORIGINAL_SDK_UPPER_HISTORY_ORDER_CONTRAST",
        "authentic_native_antecedent_run": 40123855347,
        "prospectively_frozen_controls": CONTROLS,
        "prospectively_frozen_pairs": MATCHED_PAIRS,
        "original_sdk_resets": len(cases),
        "original_root_hash": next(iter(roots)),
        "official_level5_or_WIN_count": len(advanced),
        "official_progress_cases": advanced,
        "official_native_level_histogram": dict(Counter(str(x["official_sdk_level"]) for x in cases)),
        "native_cases": cases,
        "native_history_comparisons": contrasts,
        "boundary": "All measurements are authentic original SDK frames/status. Visible selected bbox is not complete game state. Source pixel changes alone do not certify a WIN.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **raw_source)
    print("ARC4_ORDER_NATIVE_SUMMARY " + json.dumps({
        "resets": len(cases),
        "official_level5_or_WIN_count": len(advanced),
        "official_level_histogram": report["official_native_level_histogram"],
        "native_cases": [{
            "case": row["case"],
            "witness": row["independent_original_sdk_witness"],
            "selected_bbox": row["native_source_observations"]["selected_bbox"],
            "first_four": row["native_source_observations"]["source_first_four_simultaneous"],
            "first_offcup": row["native_source_observations"]["first_native_new6_outside_cups_by_row"],
        } for row in cases if row["independent_original_sdk_witness"] == "A"],
        "matched_history_pairs": [{
            "baseline": c["baseline"],
            "variant": c["variant"],
            "same_bbox": c["source_observed_comparison"]["same_observed_selected_bbox"],
            "four_cup_frames": c["source_observed_comparison"]["native_four_cup_frames"],
            "pre_pour_difference": c["source_observed_comparison"]["source_frame_difference"]["source_prepour_differing_pixel_count"],
        } for c in contrasts],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
