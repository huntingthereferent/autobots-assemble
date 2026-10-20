"""Independent native LS20 full-frontier capture; does not score predictions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import arc_agi
from arc_agi import OperationMode
import numpy as np
from .native_suffix_probe import take_word
from .native_geometry_frontier import PROTOCOL

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frozen", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    frozen = json.loads(a.frozen.read_text())
    if (frozen.get("kind") != "AB_NATIVE_SOURCE_FROZEN_COMPLETE_FRONTIER_V1" or
        frozen.get("protocol") != PROTOCOL or
        frozen.get("unique_unmeasured_edges") != 39 or
        len(frozen.get("source_frozen_trials", [])) != 78):
        raise ValueError("no valid preregistered native frontier")
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    rows = []
    frames = {}
    roots = set()
    for index, trial in enumerate(frozen["source_frozen_trials"]):
        word = trial["word"]
        capture, actual = take_word(arcade, "ls20", word)
        key = f"trial_{index:03d}"
        rows.append({"trial_key":key, "edge_id":trial["edge_id"],
                     "history":trial["history"], "native_path":capture})
        frames[key] = np.stack(actual)
        roots.add(capture["states"][0]["observation"]["whole"])
    result = {
        "kind":"AB_REAL_NATIVE_COMPLETE_FRONTIER_RAW_V1",
        "protocol": PROTOCOL, "game":"ls20",
        "native_trials": rows, "native_actions": sum(r["native_path"]["steps"] for r in rows),
        "actual_initial_native_root_hashes": sorted(roots),
        "collector_never_scores_predictions": True
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**frames)
    print("AB_NATIVE_COMPLETE_FRONTIER_COLLECTED " + json.dumps({
        "trials": len(rows), "actions": result["native_actions"],
        "same_root": len(roots)==1,
        "completed": sum(r["native_path"]["completed"] is True for r in rows)
    },sort_keys=True))

if __name__ == "__main__":
    main()
