"""Fail-closed ARC4 drift preflight / native artifact audit.

Preserves the explicit ARC source referent, frozen intervention, source status,
witnesses and exact unknown boundary. Does not play the game or infer physics.
Called before and after the existing ORIGINAL SDK run; no synthetic fallback.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

MANIFEST = Path("work/arc3/arc4_current_run.json")
DEFAULT_RESULT = Path("runtime/data/arc4/arc4-direct-upper-right1-contrast.json")


def require(condition, message):
    if not condition:
        raise RuntimeError("ARC4_DRIFT_WALL: " + message)


def context():
    contract = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(contract["schema_version"] == 1, "unrecognized run contract")
    require(contract["source_code"] ==
            "work/arc3/native_sp80_stage4_direct_upper_right1_contrast.py",
            "source implementation changed")
    from work.arc3.native_sp80_stage4_direct_upper_right1_contrast import (
        PARENT, CONTROLS, STAGE1_WITNESSES, parse_plan,
    )
    expected = [tuple(row) for row in contract["frozen_controls"]]
    require(PARENT == contract["frozen_parent"], "native parent drift")
    require(tuple(CONTROLS) == tuple(expected), "frozen control drift")
    require(len(CONTROLS) == 7 and len({n for n, _ in CONTROLS}) == 7,
            "lost or duplicated controls")
    require(dict(CONTROLS)["right1"] == "4" and
            dict(CONTROLS)["left_then_right"] == "3 4",
            "direct RIGHT1 and LEFT1->RIGHT1 conflated")
    require(tuple(name for name, _ in STAGE1_WITNESSES) == ("A", "B"),
            "independent original source entry pair drift")
    require(contract["resets_per_control"] == 2 and
            contract["expected_native_reset_count"] == len(CONTROLS) * 2,
            "unfrozen native reset budget")
    for name, controls in CONTROLS:
        word = " ".join(x for x in (PARENT, controls, "5") if x)
        actions = parse_plan(word)
        require(actions[-1][0] == 5 and
                sum(action == 5 for action, _ in actions) == 1,
                "missing original native commit in " + name)
        require(all(xy is not None for action, xy in actions if action == 6),
                "missing original native click coordinates in " + name)
    require(any("levels_completed >=5" in wall for wall in contract["walls"]),
            "official native level witness boundary missing")
    return contract


def verify_result(contract, result_path):
    import numpy as np
    require(result_path.is_file(), "native JSON missing")
    archive = result_path.with_suffix(".npz")
    require(archive.is_file(), "original full-returned-frame NPZ missing")
    data = json.loads(result_path.read_text(encoding="utf-8"))
    require(data.get("kind") == "ARC4_ORIGINAL_SDK_TOP_LEFT_SOURCE_FIRST_CONTRAST",
            "native result kind changed")
    expected = contract["frozen_controls"]
    require(data.get("predeclared_controls") == expected,
            "native result reports changed frozen controls")
    trials = data.get("native_cases")
    require(isinstance(trials, list) and
            len(trials) == contract["expected_native_reset_count"] and
            data.get("original_sdk_resets") == len(trials),
            "native reset ledger incomplete")
    successful = 0
    offcup_receipts = {}
    for name, word_tail in expected:
        rows = [row for row in trials if row.get("control") == name]
        require(len(rows) == 2 and
                {row.get("native_witness") for row in rows} == {"A", "B"},
                "independent source pair missing: " + name)
        word = " ".join(x for x in (contract["frozen_parent"],word_tail,"5") if x)
        for row in rows:
            require(row.get("source_action_word") == word, "native word drift")
            require(isinstance(row.get("sdk_level"), int) and
                    isinstance(row.get("sdk_state"), str),
                    "official SDK status missing")
            require(isinstance(row.get("genuine_stage4_action_receipts"), list)
                    and row["genuine_stage4_action_receipts"],
                    "actual original action receipts missing")
            require(isinstance(row.get("source_observation"), dict) and
                    row["source_observation"].get("source_frame_count", 0) > 0,
                    "actual source frame observation missing")
            obs = row["source_observation"]
            # A previous run accidentally shadowed the per-cup first-fill
            # dictionary with a later off-cup local. Reject this malformed
            # output rather than silently reporting invalid cup timing.
            cup_first = obs.get("source_first_full_cups")
            cup_max = obs.get("source_max_filled_cups")
            expected_cups = {"lateral", "top_left", "top_middle", "top_right"}
            require(isinstance(cup_first, dict) and set(cup_first) == expected_cups,
                    "first-full-cup map corrupted or missing")
            require(isinstance(cup_max, dict) and set(cup_max) == expected_cups,
                    "original cup maxima missing")
            for cup in expected_cups:
                frame = cup_first[cup]
                require((frame is None or (type(frame) is int and
                        0 <= frame < obs["source_frame_count"])) and
                        type(cup_max[cup]) is int and 0 <= cup_max[cup] <= 45,
                        "invalid original native first-full-cup receipt")
                require((frame is None) == (cup_max[cup] < 45),
                        "full-cup event contradicts original source maxima")
            first = obs.get("first_native_new6_outside_cups_by_row")
            require(isinstance(first, dict) and set(first) == {"5", "8"},
                    "frozen row-5/row-8 off-cup witness missing")
            for native_row in (5, 8):
                item = first[str(native_row)]
                if item is None:
                    continue  # Explicit absence in this bounded returned stack.
                require(isinstance(item, dict) and
                        isinstance(item.get("frame"), int) and
                        0 <= item["frame"] < obs["source_frame_count"] and
                        isinstance(item.get("source_x"), list) and
                        bool(item["source_x"]) and
                        item.get("source_pixel_count") == len(item["source_x"]),
                        "invalid first off-cup source event")
                for x in item["source_x"]:
                    require(type(x) is int and 0 <= x < 64 and
                            not any(y0 <= native_row <= y1 and x0 <= x <= x1
                                    for x0, y0, x1, y1 in
                                    ((5,35,10,43), (17,5,25,10),
                                     (35,5,43,10), (47,5,55,10))),
                            "off-cup event contains original cup pixel")
            if name in offcup_receipts:
                require(offcup_receipts[name] == first,
                        "A/B source off-cup event divergence for " + name)
            else:
                offcup_receipts[name] = first
            # Existing original SDK runner owns the native win classification.
            require(type(row.get("official_level5_or_WIN")) is bool,
                    "native progress flag missing or non-boolean")
            successful += int(row["official_level5_or_WIN"])
    require(data.get("official_level5_or_WIN_count") == successful,
            "source status contradicted by aggregate progress claim")
    with np.load(archive, allow_pickle=False) as saved:
        require(len(saved.files) >= len(trials), "raw source stacks missing")
        for key in saved.files:
            frames = saved[key]
            require(frames.ndim in (2, 3) and frames.shape[-2:] == (64, 64),
                    "non-native frame shape in archived source: " + key)
    return {
        "kind": "ARC4_DRIFT_RETURN",
        "referent": contract["referent"],
        "run_contract": contract["id"],
        "checkout_sha": os.getenv("GITHUB_SHA", "local-unpinned"),
        "state": "MOVE_PENDING_INDEPENDENT_VERIFICATION" if successful else "PARTIAL",
        "official_sdk_progress_cases": successful,
        "native_resets_with_receipts": len(trials),
        "observed_first_new6_outside_cups_by_row": offcup_receipts,
        "original_frame_archive": str(archive),
        "unresolved_walls": contract["walls"],
        "next_movement": (contract["next_if_progress"] if successful
                          else contract["next_if_no_progress"]),
        "scope": "Original native source only; no automatic F3 or solved-game inference",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("pre", "post"))
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    contract = context()
    if args.phase == "pre":
        print("ARC4_DRIFT_PREFLIGHT " + json.dumps({
            "contract": contract["id"],
            "source": contract["source_code"],
            "frozen_conditions": len(contract["frozen_controls"]),
            "expected_native_resets": contract["expected_native_reset_count"],
            "referent": contract["referent"],
            "last_supported": contract["prior_state"],
        }, sort_keys=True))
    else:
        receipt = verify_result(contract, args.result)
        path = args.result.with_suffix(".protocol.json")
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print("ARC4_DRIFT_RETURN " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
