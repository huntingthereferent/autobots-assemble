"""Observe source-owned SP80 level-4 event ordering; no new movement hypothesis.

Frozen positives are from PR #398. Each is replayed against two original
SDK entrance witnesses. Native status, not pixels, determines progression.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

CUPS = {
    "lateral": (5, 35, 10, 43),
    "top_left": (17, 5, 25, 10),
    "top_middle": (35, 5, 43, 10),
    "top_right": (47, 5, 55, 10),
}
BORDERS = {
    "left": (slice(2, 62), slice(2, 5)),
    "right": (slice(2, 62), slice(59, 62)),
    "top": (slice(2, 5), slice(2, 62)),
    "bottom": (slice(59, 63), slice(2, 62)),
}
RIGHT = "6@46,33 3"
PARENTS = {
    "D3L2_L3U2": ("6@24,33 2 2 2 3 3", "6@34,42 3 3 3 1 1"),
    "D4L2_L4U2": ("6@24,33 2 2 2 2 3 3", "6@34,42 3 3 3 3 1 1"),
}
# Three native visual positives and two matched negative controls.
FROZEN = (
    ("D3L2_L3U2", "left1", "3"),
    ("D4L2_L4U2", "left1", "3"),
    ("D4L2_L4U2", "left2", "3 3"),
    ("D3L2_L3U2", "reselect", ""),
    ("D4L2_L4U2", "up1", "1"),
)

def word(parent: str, move: str) -> str:
    middle, lower = PARENTS[parent]
    return " ".join(v for v in (RIGHT, middle, lower, "6@34,21", move, "5") if v)

def observe(root: np.ndarray, pre: np.ndarray, frames: np.ndarray) -> dict:
    if root.shape != (64, 64) or pre.shape != (64, 64) or frames.ndim != 3 or frames.shape[1:] != (64, 64):
        raise ValueError("Original 64x64 native SDK frames required")
    origins = {}
    outside_cups = np.ones((64, 64), dtype=bool)
    for key, (x0, y0, x1, y1) in CUPS.items():
        mask = root[y0:y1+1, x0:x1+1] == 11
        if int(mask.sum()) != 45:
            raise AssertionError("Observed original cup mask differs from source anchor")
        origins[key] = mask
        outside_cups[y0:y1+1, x0:x1+1] = False
    first_full = {key: None for key in CUPS}
    maximum = {key: 0 for key in CUPS}
    first_four = None
    boundaries = {name: {"first_any": None, "first_1_to_14": None,
                         "first_changed_count": None, "episodes": []}
                  for name in BORDERS}
    border_prev = {name: False for name in BORDERS}
    outside = {"row5": None, "row8": None}
    ordered_events = []

    for t, frame in enumerate(frames):
        full = 0
        for key, (x0, y0, x1, y1) in CUPS.items():
            region = frame[y0:y1+1, x0:x1+1]
            filled = int(np.count_nonzero(origins[key] & (region == 13)))
            maximum[key] = max(maximum[key], filled)
            if filled == 45:
                full += 1
                if first_full[key] is None:
                    first_full[key] = int(t)
                    ordered_events.append({"frame": int(t), "kind": "cup_first_full", "source": key})
        if full == 4 and first_four is None:
            first_four = int(t)
            ordered_events.append({"frame": int(t), "kind": "four_simultaneous_cups"})

        new6 = (pre != 6) & (frame == 6) & outside_cups
        for name, y in (("row5", 5), ("row8", 8)):
            if outside[name] is None:
                xs = np.flatnonzero(new6[y, 8:59]) + 8
                if len(xs):
                    outside[name] = {"frame": int(t), "x": [int(v) for v in xs]}
                    ordered_events.append({"frame": int(t), "kind": "new_source6_outside_cups", "source": name})
        for name, region in BORDERS.items():
            prior, current = pre[region], frame[region]
            different = prior != current
            active = bool(np.any(different))
            info = boundaries[name]
            if active and info["first_any"] is None:
                info["first_any"] = int(t)
                info["first_changed_count"] = int(np.count_nonzero(different))
                ordered_events.append({"frame": int(t), "kind": "first_border_change", "source": name})
            if active and not border_prev[name]:
                info["episodes"].append(int(t))
            if info["first_1_to_14"] is None and bool(np.any((prior == 1) & (current == 14))):
                info["first_1_to_14"] = int(t)
            border_prev[name] = active
    ordered_events.sort(key=lambda e: (e["frame"], e["kind"], e.get("source", "")))
    return {
        "cup_first_full": first_full,
        "cup_maximum": maximum,
        "first_four_simultaneously_full": first_four,
        "native_boundary_events": boundaries,
        "first_new6_outside_cups": outside,
        "first_event_order": ordered_events,
        "source_prepour_hash": hash_frame(pre),
        "source_final_hash": hash_frame(frames[-1]),
        "original_sdk_animation_frames": int(len(frames)),
        "limit": "Frame observations are not the hidden engine rule or an official success predicate.",
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    records, original_frames = [], {}
    for parent, control, movement in FROZEN:
        case = parent + "_" + control
        actions = word(parent, movement)
        parts = parse_plan(actions)
        assert parts[-1][0] == 5 and sum(a == 5 for a, _ in parts) == 1
        for witness, entry in STAGE1_WITNESSES:
            native, raw = run_case(case, witness, entry, actions)
            root = raw["entry3_34"][-1]
            pre = raw["stage4_" + str(len(parts) - 1)][-1]
            frames = raw["stage4_" + str(len(parts))]
            observation = observe(root, pre, frames)
            records.append({
                "case": case, "native_witness": witness,
                "original_native_action_word": actions,
                "original_sdk_level": native["true_original_sdk_final_level"],
                "original_sdk_state": native["true_original_sdk_final_state"],
                "official_level5_or_WIN": native["official_original_level5_or_WIN"],
                "original_sdk_action_receipts": native["genuine_original_stage4_action_ledger"],
                "source_observations": observation,
            })
            for key, frameset in raw.items():
                original_frames[case + "_" + witness + "_" + key] = frameset
            print("ARC4_EVENT_AUDIT_CASE " + json.dumps({
                "case": case, "witness": witness,
                "level": records[-1]["original_sdk_level"],
                "state": records[-1]["original_sdk_state"],
                "observations": observation,
            }, sort_keys=True), flush=True)
    for parent, control, movement in FROZEN:
        case = parent + "_" + control
        pair = [v for v in records if v["case"] == case]
        if len(pair) != 2:
            raise AssertionError("Missing independent native witness")
        for key in ("original_sdk_level", "original_sdk_state", "source_observations"):
            if pair[0][key] != pair[1][key]:
                raise AssertionError("Independent native observations disagree: " + case + " " + key)
    report = {
        "kind": "ARC4_SOURCE_OWNED_EVENT_ORDER_AUDIT",
        "source_previous_pr": 398,
        "native_original_sdk_reset_count": len(records),
        "official_progress_count": sum(bool(v["official_level5_or_WIN"]) for v in records),
        "official_level_histogram": dict(Counter(str(v["original_sdk_level"]) for v in records)),
        "original_native_records": records,
        "scope": "Frozen native replay and first frame-event ordering; no private physics or inferred win rule.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **original_frames)
    print("ARC4_EVENT_AUDIT_SUMMARY " + json.dumps({
        "native_original_sdk_reset_count": report["native_original_sdk_reset_count"],
        "official_progress_count": report["official_progress_count"],
        "official_level_histogram": report["official_level_histogram"],
    }, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
