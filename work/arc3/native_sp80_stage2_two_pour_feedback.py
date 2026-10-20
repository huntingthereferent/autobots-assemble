"""Source-native SP80 stage2 paired-pour feedback experiment.

Unlike the earlier single-ACTION5 four-bar sweeps this fixes a source
geometry, makes an ORIGINAL SDK pour, then changes exactly one bar and
pours again in the SAME original game. Both original pours and every
returned frame are retained, even if there is no advancement.
The public sp80 mechanics guide is external motivation only, NOT a
source-native observation and not evidence of winning.

This does not edit the F3 mathematics, ARC agent or game engine.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as source_trial
from .native_sp80_multi_select import parse_plan

BARS = ("U", "M", "L", "B")
POINTS = {"U": (12, 21), "M": (44, 29), "L": (12, 33), "B": (40, 41)}
# A fixed prospective set. A delta is an actual native 4-pixel horizontal
# action step. The paired pours differ by just one subsequent intervention.
CASES = (
    ("root_upper_right", (0, 0, 0, 0), "U", 1),
    ("root_upper_left", (0, 0, 0, 0), "U", -1),
    ("root_middle_left", (0, 0, 0, 0), "M", -1),
    ("root_middle_right", (0, 0, 0, 0), "M", 1),
    ("root_lower_right", (0, 0, 0, 0), "L", 1),
    ("root_lower_left", (0, 0, 0, 0), "L", -1),
    ("root_bottom_left", (0, 0, 0, 0), "B", -1),
    ("root_bottom_right", (0, 0, 0, 0), "B", 1),
    ("inward_one_upper", (1, -1, 1, -1), "U", 1),
    ("inward_one_middle", (1, -1, 1, -1), "M", -1),
    ("inward_one_lower", (1, -1, 1, -1), "L", 1),
    ("inward_one_bottom", (1, -1, 1, -1), "B", -1),
    ("inward_two_upper_reverse", (2, -2, 2, -2), "U", -1),
    ("inward_two_middle_reverse", (2, -2, 2, -2), "M", 1),
    ("inward_two_lower_reverse", (2, -2, 2, -2), "L", -1),
    ("inward_two_bottom_reverse", (2, -2, 2, -2), "B", 1),
)

def action_point(bar, dx=0):
    x, y = POINTS[bar]
    return "6@%d,%d" % (x + dx * 4, y)

def move(dx):
    return ["3"] * (-dx) if dx < 0 else ["4"] * dx

def plan(offsets, changed, delta):
    parts = []
    for bar, dx in zip(BARS, offsets):
        parts.append(action_point(bar))
        parts += move(dx)
    parts.append("5")
    # Native failed pour retains the object placements (not an engine
    # assumption here: source pixel and selection are reobserved below).
    # Click the translated expected original bar pixel to test precisely
    # one additional object shift before the next original source pour.
    parts.append(action_point(changed, offsets[BARS.index(changed)]))
    parts += move(delta)
    parts.append("5")
    return " ".join(parts)

PROGRAMS = tuple((name, offsets, changed, delta,
                  plan(offsets, changed, delta))
                 for name, offsets, changed, delta in CASES)
assert len(PROGRAMS) == 16 and len({p[0] for p in PROGRAMS}) == 16
assert len(STAGE1_WITNESSES) == 2
for name, offsets, changed, delta, word in PROGRAMS:
    parsed = parse_plan(word)
    assert changed in BARS and delta in (-1, 1)
    assert [a for a, _ in parsed].count(5) == 2
    assert [a for a, _ in parsed].count(6) == 5
    assert all(a != 6 or coords is not None for a, coords in parsed)

def actual_pours(row, raw):
    observations = []
    for event in row["stage2_native_observations"]:
        if event["native_action"] != 5:
            continue
        key = "stage2_" + str(event["phase_step"])
        frames = raw.get(key)
        if frames is None:
            observations.append({
                "source_phase_step": event["phase_step"],
                "disposition": "UNKNOWN_SOURCE_FRAME_STACK",
                "original_source_level_after": event["source_SDK_level_after"],
                "original_sdk_state_after": event["source_SDK_state_after"],
            })
            continue
        # Source-owned pixel readings; DO NOT equate any palette or region
        # with a decoded cup, spill, success, or hidden source predicate.
        frames = np.asarray(frames)
        if frames.ndim != 3 or frames.shape[1:] != (64, 64):
            observations.append({
                "source_phase_step": event["phase_step"],
                "disposition": "UNKNOWN_NATIVE_FRAME_SHAPE",
            })
            continue
        observations.append({
            "source_phase_step": event["phase_step"],
            "original_returned_sdk_frame_count": int(len(frames)),
            "real_original_sdk_level_before": event["source_SDK_level_before"],
            "real_original_sdk_level_after": event["source_SDK_level_after"],
            "real_original_sdk_state_after": event["source_SDK_state_after"],
            "sdk_original_frame_ledger": event["full_original_SDK_frame_ledger"],
            "actual_native_top_region_color_occupancy": [
                {str(c): int(np.count_nonzero(frame[:13] == c))
                 for c in (6, 8, 9, 11, 13, 14)} for frame in frames
            ],
            "actual_native_bottom_region_color_occupancy": [
                {str(c): int(np.count_nonzero(frame[48:] == c))
                 for c in (6, 8, 9, 11, 13, 14)} for frame in frames
            ],
        })
    return observations

def run(out: Path):
    rows, source_arrays = [], {}
    for name, offsets, changed, delta, word in PROGRAMS:
        for witness, source_word in STAGE1_WITNESSES:
            row, raw = source_trial(witness, source_word, name, word, 0)
            if row["source_genuine_level2_entry"]["source_original_level"] != 2:
                raise RuntimeError("Did not enter genuine source-native level2")
            row["frozen_original_first_geometry_offsets"] = dict(zip(BARS, offsets))
            row["frozen_second_original_bar_movement"] = {"bar": changed, "horizontal_steps": delta}
            row["source_two_separate_pour_reactions"] = actual_pours(row, raw)
            row["source_second_bar_selection_reading"] = [
                {"native_click_xy": e.get("native_click_xy"),
                 "native_preclick_color": e.get("original_native_preclick_color")}
                for e in row["stage2_native_observations"]
                if e["native_action"] == 6
            ][-1:]
            rows.append(row)
            for key, frames in raw.items():
                source_arrays["%s_%s_%s" % (name, witness, key)] = frames
    if len(rows) != 2 * len(PROGRAMS):
        raise RuntimeError("Missing genuine independent original source games")
    result = {
        "kind": "GENUINE_ORIGINAL_SP80_STAGE2_SAME_GAME_PAIRED_POUR_REACTIONS",
        "motivation": "External public game guide suggested study of pour feedback; guide is NOT original SDK evidence.",
        "prospectively_frozen_two_pour_programs": PROGRAMS,
        "original_stage1_to2_verified_native_words": STAGE1_WITNESSES,
        "original_source_independent_game_resets": len(rows),
        "true_original_stage2_pour_action5_observations": sum(len(r["source_two_separate_pour_reactions"]) for r in rows),
        "actual_official_original_level3_or_WIN": sum(int(r["source_level3_or_WIN"]) for r in rows),
        "original_SDK_dispositions": dict(Counter(r["source_stage2_control_disposition"] for r in rows)),
        "source_successes": [{"name": r["frozen_level2_control"], "witness": r["witness"],
                              "level": r["original_source_final_level"], "state": r["original_source_final_state"]}
                             for r in rows if r["source_level3_or_WIN"]],
        "all_original_source_native_trial_records": rows,
        "limitations": "Same authentic original SDK, two distinct ACTION5 pours within each original stage2 session. All raw native returned frames recorded. Official SDK level>=3 or WIN alone proves level advance; source colors and external guide cannot. No physical/hidden mechanic claim, F3 law mapping or complete SP80 win implied.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    np.savez_compressed(out.with_suffix(".npz"), **source_arrays)
    print("SP80_PAIRED_POURS " + json.dumps({
        k: v for k, v in result.items()
        if k not in ("all_original_source_native_trial_records", "prospectively_frozen_two_pour_programs")
    }, sort_keys=True))
    if any(not r["source_genuine_level2_entry"]["source_original_level"] == 2 for r in rows):
        raise RuntimeError("Unverified original SDK source entry")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    run(args.out)

if __name__ == "__main__":
    main()
