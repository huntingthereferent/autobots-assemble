"""Fail-closed source-first pre/post contract for native ARC4 history ordering."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path

MANIFEST = Path("work/arc3/arc4_order_run.json")
OUTPUT = Path("runtime/data/arc4/arc4-upper-history-order.json")
KIND = "ARC4_ORIGINAL_SDK_UPPER_HISTORY_ORDER_CONTRAST"


def require(value, message):
    if not value:
        raise RuntimeError("ARC4_ORDER_DRIFT_WALL: " + message)


def context():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(m["schema_version"] == 1, "invalid manifest")
    require(m["source_code"] == "work/arc3/native_sp80_stage4_upper_history_order.py",
            "source file drift")
    from work.arc3.native_sp80_stage4_upper_history_order import (
        PARENT, CONTROLS, MATCHED_PAIRS, STAGE1_WITNESSES, parse_plan,
    )
    require(PARENT == m["frozen_parent"], "source parent drift")
    require([list(row) for row in CONTROLS] == m["frozen_controls"], "original action controls drift")
    require([list(pair) for pair in MATCHED_PAIRS] == m["frozen_pairs"], "pair contract drift")
    require(tuple(name for name, _ in STAGE1_WITNESSES) == ("A", "B"),
            "original native witness changes")
    require(m["expected_native_reset_count"] == 14
            and m["expected_native_reset_count"] ==
            m["resets_per_condition"] * len(CONTROLS),
            "unadmitted reset budget")
    require(dict(CONTROLS)["right_then_left"] == "4 3"
            and dict(CONTROLS)["left_then_right"] == "3 4",
            "reverse history orders merged")
    for name, word_tail in CONTROLS:
        word = " ".join(x for x in (PARENT, word_tail, "5") if x)
        plan = parse_plan(word)
        require(plan[-1][0] == 5 and sum(a == 5 for a, xy in plan) == 1,
                "missing authentic original SDK pour in " + name)
        require(all(xy is not None for a, xy in plan if a == 6),
                "missing original source click in " + name)
    require(any("levels_completed >=5" in wall for wall in m["walls"]),
            "official progress criterion missing")
    return m


def verify_result(contract, path: Path):
    import numpy as np
    require(path.is_file(), "genuine native JSON missing")
    archive = path.with_suffix(".npz")
    require(archive.is_file(), "full original SDK frame NPZ missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("kind") == KIND, "non-native or wrong result kind")
    require(data.get("prospectively_frozen_controls") == contract["frozen_controls"],
            "source changed native frozen controls")
    require(data.get("prospectively_frozen_pairs") == contract["frozen_pairs"],
            "native paired hypotheses drift")
    require(data.get("original_sdk_resets") == contract["expected_native_reset_count"],
            "native reset count incomplete")
    rows = data.get("native_cases")
    require(isinstance(rows, list) and len(rows) == contract["expected_native_reset_count"],
            "native A/B case receipts missing")
    totals = 0
    status_counts = Counter()
    for name, suffix in contract["frozen_controls"]:
        matched = [row for row in rows if row.get("case") == name]
        require(len(matched) == 2 and
                {row.get("independent_original_sdk_witness") for row in matched} == {"A", "B"},
                "original independent witness identity missing")
        word = " ".join(x for x in (contract["frozen_parent"], suffix, "5") if x)
        for row in matched:
            require(row.get("predeclared_word") == word, "source action word mismatch")
            require(type(row.get("official_sdk_level")) is int and
                    isinstance(row.get("official_sdk_state"), str),
                    "original official status missing")
            require(type(row.get("official_level5_or_WIN")) is bool,
                    "native WIN criterion absent")
            require(isinstance(row.get("original_sdk_action_receipts"), list)
                    and bool(row["original_sdk_action_receipts"]),
                    "original source action/selection receipts absent")
            obs = row.get("native_source_observations")
            require(isinstance(obs, dict) and obs.get("source_frame_count", 0) > 0,
                    "actual native source frames missing")
            require(isinstance(obs.get("root_hash"), str), "original root hash absent")
            require(isinstance(obs.get("first_native_new6_outside_cups_by_row"), dict),
                    "native color arrival observation missing")
            totals += int(row["official_level5_or_WIN"])
            status_counts[str(row["official_sdk_level"])] += 1
        for field in ("official_sdk_level", "official_sdk_state", "official_level5_or_WIN",
                      "native_source_observations"):
            require(matched[0][field] == matched[1][field],
                    "independent original A/B disagreement: " + name)
    require(totals == data.get("official_level5_or_WIN_count"),
            "claimed native progression contradicts actual source receipts")
    require(dict(status_counts) == data.get("official_native_level_histogram"),
            "official original SDK level histogram mismatch")
    pairs = data.get("native_history_comparisons")
    require(isinstance(pairs, list) and len(pairs) == len(contract["frozen_pairs"]),
            "missing predeclared native comparisons")
    matched_bbox = []
    differing_cups = []
    for pair, expected in zip(pairs, contract["frozen_pairs"]):
        require([pair.get("baseline"), pair.get("variant")] == expected,
                "original pair identity drift")
        obs = pair.get("source_observed_comparison")
        require(isinstance(obs, dict) and type(obs.get("same_observed_selected_bbox")) is bool,
                "original observed selected bbox comparison missing")
        require(isinstance(obs.get("source_frame_difference"), dict),
                "actual matched native source differences missing")
        require(obs["source_frame_difference"].get("source_prepour_differing_pixel_count") is not None,
                "exact pre-pour source pixel measurement missing")
        if obs["same_observed_selected_bbox"]:
            matched_bbox.append(expected)
            if not obs["same_four_cup_frame"]:
                differing_cups.append(expected)
    with np.load(archive, allow_pickle=False) as arrays:
        require(len(arrays.files) >= len(rows), "raw original SDK reset frames incomplete")
        for key in arrays.files:
            frames = arrays[key]
            require(frames.ndim in (2, 3) and frames.shape[-2:] == (64, 64),
                    "original 64x64 SDK frame archive invalid: " + key)
    return {
        "kind": "ARC4_ORDER_DRIFT_RETURN",
        "state": "PARTIAL" if not totals else "PROGRESS_REQUIRES_INDEPENDENT_NATIVE_RECHECK",
        "referent": contract["referent"],
        "checkout": os.getenv("GITHUB_SHA", "local-unpinned"),
        "contract": contract["id"],
        "official_sdk_progress_cases": totals,
        "native_resets_with_receipts": len(rows),
        "same_observed_selected_bbox_pairs": matched_bbox,
        "same_bbox_different_cup_timing_pairs": differing_cups,
        "unresolved_walls": contract["walls"],
        "next_movement": contract["next_if_progress"] if totals else contract["next_if_no_progress"],
        "source_archive": str(archive),
        "limit": "Genuine original SDK receipts and bounded source comparisons, no inferred hidden game physics or private win target.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("pre", "post"))
    p.add_argument("--result", type=Path, default=OUTPUT)
    args = p.parse_args()
    m = context()
    if args.phase == "pre":
        print("ARC4_ORDER_DRIFT_PREFLIGHT " + json.dumps({
            "referent": m["referent"], "source_code": m["source_code"],
            "frozen_cases": len(m["frozen_controls"]),
            "native_resets": m["expected_native_reset_count"],
            "frozen_pairs": m["frozen_pairs"],
        }, sort_keys=True), flush=True)
    else:
        receipt = verify_result(m, args.result)
        args.result.with_suffix(".protocol.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print("ARC4_ORDER_DRIFT_RETURN " + json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
