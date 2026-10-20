"""Collect complete original native LS20 multi-action continuations without scoring."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import arc_agi
from arc_agi import OperationMode
import numpy as np
from .native_suffix_probe import take_word
from .native_special_tile_multistep import PROTOCOL,PREFIXES,SUFFIXES

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.frozen.read_text())
    expected=[prefix+suffix for suffix in SUFFIXES for prefix in PREFIXES]
    trials=frozen.get("registered_trials")
    if (frozen.get("kind")!="AB_SOURCE_FROZEN_SPECIAL_TILE_MULTI_SUFFIX_V1" or
        frozen.get("protocol")!=PROTOCOL or
        [x.get("word") for x in trials]!=expected):
        raise ValueError("original source hypothesis is incomplete or modified")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    arrays={}
    roots=set()
    for i,t in enumerate(trials):
        path,images=take_word(arcade,"ls20",t["word"])
        key=f"trial_{i:02d}"
        records.append({"key":key,"trial_id":t["id"],"native_path":path})
        arrays[key]=np.stack(images)
        roots.add(path["states"][0]["observation"]["whole"])
    result={
        "kind":"AB_REAL_NATIVE_SPECIAL_TILE_MULTISTEP_RAW_V1",
        "protocol":PROTOCOL,"game":"ls20",
        "native_paths":records,"native_actions":sum(r["native_path"]["steps"] for r in records),
        "native_visible_initial_root_hashes":sorted(roots),
        "collector_does_not_evaluate_predictions":True
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**arrays)
    print("AB_NATIVE_MULTISTEP_SPECIAL_TILE_COLLECTED "+json.dumps({
        "trajectories":len(records),"actions":result["native_actions"],
        "complete":sum(r["native_path"]["completed"] is True for r in records),
        "same_root":len(roots)==1},sort_keys=True))
if __name__=="__main__":
    main()
