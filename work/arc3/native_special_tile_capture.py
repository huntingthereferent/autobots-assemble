"""Actual public LS20 native captures after an identical visible special tile."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import arc_agi
from arc_agi import OperationMode
import numpy as np
from .native_suffix_probe import take_word
from .native_special_tile_successor import PROTOCOL,PREFIXES,ACTIONS

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.frozen.read_text())
    words=[p+action for p in PREFIXES for action in ACTIONS]
    if (frozen.get("kind")!="AB_SOURCE_FROZEN_SPECIAL_TILE_SUCCESSOR_V1" or
        frozen.get("protocol")!=PROTOCOL or
        [t.get("word") for t in frozen.get("frozen_trials",[])]!=words):
        raise ValueError("source-frozen native experiment not supplied")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    observed=[]
    arrays={}
    roots=set()
    for i,t in enumerate(frozen["frozen_trials"]):
        path,frames=take_word(arcade,"ls20",t["word"])
        key=f"trial_{i:02d}"
        arrays[key]=np.stack(frames)
        observed.append({"key":key,"trial_id":t["trial_id"],"path":path})
        roots.add(path["states"][0]["observation"]["whole"])
    report={"kind":"AB_OFFICIAL_NATIVE_SPECIAL_TILE_SUCCESSOR_CAPTURE_V1",
            "protocol":PROTOCOL,"game":"ls20",
            "trials":observed,
            "native_action_count":sum(row["path"]["steps"] for row in observed),
            "root_hashes":sorted(roots),
            "collector_has_not_scored_any_prediction":True}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**arrays)
    print("AB_NATIVE_SPECIAL_TILE_COLLECTED "+json.dumps({
      "separate_resets":len(observed),
      "actions":report["native_action_count"],
      "completed":sum(row["path"]["completed"] is True for row in observed),
      "roots_equal":len(roots)==1},sort_keys=True))
if __name__=="__main__":main()
