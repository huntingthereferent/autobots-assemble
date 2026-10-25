"""Original SP80 SDK level4: target the observed lower-left upstream branch.

Two preserved clean lateral configurations have a source-observed
three-pixel progression from x20..22 to x17..19 to x14..16 at y44..46
in A; B has an analogous trace one three-pixel cell lower. Those
arrivals are measurements, NOT a fluid-engine rule.

Hold both clean configurations fixed. After positioning the two native
selected objects, reselect the relocated left-middle piece itself at
(18,42) in A or (18,45) in B and apply bounded local movements.
This differs from sweeping the top bar or altering the original root.
Log full original SDK frames and exact before/after selected geometry.
Only official original SDK level>=5/WIN is game progression.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT = "6@46,33 3"
PARENTS = (
    ("clean_D3L2_L3U2", "6@24,33 2 2 2 3 3", "6@34,42 3 3 3 1 1", (18, 42), 44),
    ("clean_D4L2_L4U2", "6@24,33 2 2 2 2 3 3", "6@34,42 3 3 3 3 1 1", (18, 45), 47),
)
MOVES = (
    ("reclick_only", ""),
    ("up1", "1"),
    ("down1", "2"),
    ("left1", "3"),
    ("right1", "4"),
    ("up2", "1 1"),
    ("down2", "2 2"),
    ("up1_left1", "1 3"),
    ("up1_right1", "1 4"),
    ("down1_left1", "2 3"),
    ("down1_right1", "2 4"),
)

def build(parent, mid, lower_l, click, move):
    base = " ".join((RIGHT, mid, lower_l))
    if click is None:
        return base + " 5"
    reselect = f"6@{click[0]},{click[1]}"
    return " ".join(p for p in (base, reselect, move, "5") if p)

FROZEN = tuple(
    [(name + "_control", build(name, mid, lower_l, None, ""))
     for name, mid, lower_l, click, row in PARENTS]
    + [(name + "_" + move_name, build(name, mid, lower_l, click, word))
       for name, mid, lower_l, click, row in PARENTS
       for move_name, word in MOVES]
)
assert len(FROZEN) == 24 == len({n for n, _ in FROZEN})
assert len(STAGE1_WITNESSES) == 2
assert all(
    parse_plan(word)[-1][0] == 5
    and sum(a == 5 for a, xy in parse_plan(word)) == 1
    and len(parse_plan(word)) <= 24
    and all(xy is not None for a, xy in parse_plan(word) if a == 6)
    for _, word in FROZEN
)

CUPS = {
    "left_lateral": (5, 35, 10, 43),
    "top_left": (17, 5, 25, 10),
    "top_middle": (35, 5, 43, 10),
    "top_right": (47, 5, 55, 10),
}
BRANCH_X = ((20, 22), (17, 19), (14, 16))
BORDER_Y = slice(2, 62)
BORDER_X = slice(2, 5)

def selected(frame):
    return [
        {"palette": c["palette"], "bbox": c["bbox"], "pixels": c["pixels"]}
        for c in color_components(frame)
        if c["palette"] in (9, 15) and 18 <= c["bbox"][1] <= 53
    ]

def inspect(root, pre, frames, branch_y):
    if root.shape != (64, 64) or pre.shape != (64, 64):
        raise AssertionError("Expected original SDK 64x64 frames")
    if frames.ndim != 3 or frames.shape[1:] != (64, 64):
        raise AssertionError("Expected complete original SDK frame stack")
    arrivals = {f"x{a}-{b}": None for a, b in BRANCH_X}
    per_frame_counts = []
    first_cup_full = {name: None for name in CUPS}
    max_cup = {name: 0 for name in CUPS}
    first_border = None
    border_episodes = []
    border_previous = False
    for t, frame in enumerate(frames):
        new6 = (pre != 6) & (frame == 6)
        cell_counts = {}
        for a, b in BRANCH_X:
            key = f"x{a}-{b}"
            count = int(np.count_nonzero(new6[branch_y:branch_y + 3, a:b + 1]))
            cell_counts[key] = count
            if count and arrivals[key] is None:
                yy, xx = np.nonzero(new6[branch_y:branch_y + 3, a:b + 1])
                arrivals[key] = {
                    "frame": t,
                    "original_native_yx": [[int(y + branch_y), int(x + a)]
                                           for y, x in zip(yy, xx)],
                }
        per_frame_counts.append({"frame": t, "new_color6_cells": cell_counts})
        for name, (x0, y0, x1, y1) in CUPS.items():
            source = root[y0:y1 + 1, x0:x1 + 1] == 11
            if int(source.sum()) != 45:
                raise AssertionError("Original SDK root cup geometry changed")
            count = int(np.count_nonzero(source & (frame[y0:y1 + 1, x0:x1 + 1] == 13)))
            max_cup[name] = max(max_cup[name], count)
            if count == 45 and first_cup_full[name] is None:
                first_cup_full[name] = t
        border = pre[BORDER_Y, BORDER_X] != frame[BORDER_Y, BORDER_X]
        active = bool(np.any(border))
        if active and not border_previous:
            border_episodes.append(t)
        border_previous = active
        if active and first_border is None:
            first_border = {"frame": t, "native_changed_pixel_count": int(border.sum())}
    times = [arrivals[f"x{a}-{b}"]["frame"] if arrivals[f"x{a}-{b}"] else None
             for a, b in BRANCH_X]
    return {
        "original_prepour_blake2b16": hash_frame(pre),
        "original_final_blake2b16": hash_frame(frames[-1]),
        "original_returned_frame_count": len(frames),
        "branch_original_y": [branch_y, branch_y + 2],
        "three_cell_first_arrivals": arrivals,
        "measured_ordered_source_arrival": all(t is not None for t in times)
                                           and times[0] < times[1] < times[2],
        "full_branch_frame_counts": per_frame_counts,
        "original_cup_first_full_frames": first_cup_full,
        "original_cup_max_source_color13_pixels": max_cup,
        "native_first_left_border_change": first_border,
        "original_left_border_episode_frames": border_episodes,
        "original_prepour_selected_objects": selected(pre),
        "scope": "Original source observations only; no hidden physics or image-based WIN.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records, all_stacks, roots = [], {}, set()
    for case, word in FROZEN:
        parent = next(p for p in PARENTS if case.startswith(p[0] + "_"))
        _, mid, lower_l, click, branch_y = parent
        n = len(parse_plan(word))
        for witness, stage1_word in STAGE1_WITNESSES:
            sdk, stacks = run_case(case, witness, stage1_word, word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root = stacks["entry3_34"][-1]
            pre = stacks["stage4_" + str(n - 1)][-1]
            poured = stacks["stage4_" + str(n)]
            actual = inspect(root, pre, poured, branch_y)
            ledger = sdk["genuine_original_stage4_action_ledger"]
            movements = [
                {
                    "native_action_index": event["index"],
                    "original_action": event["genuine_original_action"],
                    "actual_native_click_xy": event["real_native_click_xy"],
                    "source_pixel_before_click": event["original_source_pixel_before_click"],
                    "selected_source_after": selected(stacks["stage4_" + str(event["index"])][-1]),
                    "source_frame_after_blake2b16": event["source_frame_after_blake2b16"],
                }
                for event in ledger if event["genuine_original_action"] in (1, 2, 3, 4, 6)
            ]
            if not case.endswith("_control"):
                if not any(m["actual_native_click_xy"] == list(click) for m in movements):
                    raise AssertionError("Intended relocated source middle piece was not clicked")
            row = {
                "predeclared_case": case,
                "independent_sdk_entry_witness": witness,
                "true_original_level4_word": word,
                "original_native_final_level": sdk["true_original_sdk_final_level"],
                "original_native_final_state": sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN": sdk["official_original_level5_or_WIN"],
                "observed_source_frames": actual,
                "original_native_selection_receipts": movements,
                "complete_original_sdk_action_receipts": ledger,
            }
            records.append(row)
            for phase, frames in stacks.items():
                all_stacks[f"{case}_{witness}_{phase}"] = frames
            print("SP80_LEVEL4_UPSTREAM_JUNCTION_CASE " + json.dumps({
                "case": case, "witness": witness,
                "level": row["original_native_final_level"],
                "state": row["original_native_final_state"],
                "arrival": actual["three_cell_first_arrivals"],
                "cup": actual["original_cup_max_source_color13_pixels"],
                "border": actual["native_first_left_border_change"],
            }, sort_keys=True), flush=True)
    if len(records) != 48 or len(roots) != 1:
        raise AssertionError("Missing independent original SDK clean Level4 entries")
    for case, _ in FROZEN:
        pair = [r for r in records if r["predeclared_case"] == case]
        if len(pair) != 2 or any(
            pair[0][key] != pair[1][key]
            for key in ("original_native_final_level", "original_native_final_state",
                        "observed_source_frames", "original_native_selection_receipts")
        ):
            raise AssertionError("Original SDK witness mismatch: " + case)
    advances = [r["predeclared_case"] + "/" + str(r["independent_sdk_entry_witness"])
                for r in records if r["official_level5_or_WIN"]]
    output = {
        "kind": "ORIGINAL_SP80_LEVEL4_LOWER_UPSTREAM_BRANCH_POST_PARENT_PROBE",
        "original_sdk_games": len(records),
        "prospectively_frozen_true_sdk_words": FROZEN,
        "original_level4_root_blake2b16": next(iter(roots)),
        "true_sdk_final_level_counts": dict(Counter(str(r["original_native_final_level"]) for r in records)),
        "official_level5_or_WIN_cases": advances,
        "complete_original_native_receipts": records,
        "limit": "Original SDK level >=5/WIN alone proves progress; pixel traces do not reveal engine physics.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **all_stacks)
    print("SP80_LEVEL4_UPSTREAM_JUNCTION_SUMMARY " + json.dumps({
        k: v for k, v in output.items()
        if k not in ("prospectively_frozen_true_sdk_words", "complete_original_native_receipts")
    }, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
