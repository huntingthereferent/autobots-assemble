"""Actual native LS20 time-shifted mixed-tile capture; no hypothesis scoring."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import arc_agi
from arc_agi import OperationMode
import numpy as np
from .native_suffix_probe import take_word
from .native_shifted_tile_entry import PROTOCOL
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.frozen.read_text())
    trials=frozen.get("frozen_trials")
    if (frozen.get("kind")!="AB_FROZEN_SHIFTED_NATIVE_TILE_ENTRY_V1" or
        frozen.get("protocol")!=PROTOCOL or
        not isinstance(trials,list) or len(trials)!=24):
        raise ValueError("source-frozen native experiment missing")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    raw={}
    roots=set()
    for i,t in enumerate(trials):
        path,frames=take_word(arcade,"ls20",t["word"])
        key=f"trial_{i:02d}"
        records.append({"key":key,"kind":t["kind"],"path":path})
        raw[key]=np.stack(frames)
        roots.add(path["states"][0]["observation"]["whole"])
    result={"kind":"AB_NATIVE_SHIFTED_TILE_ENTRY_RAW_V1","protocol":PROTOCOL,
            "game":"ls20","trials":records,
            "roots":sorted(roots),
            "native_actions":sum(t["path"]["steps"] for t in records),
            "collector_owns_no_predictions":True}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**raw)
    print("AB_NATIVE_SHIFTED_ENTRY_CAPTURE "+json.dumps({
      "trials":len(records),"actions":result["native_actions"],
      "completed":sum(r["path"]["completed"] is True for r in records),
      "same_root":len(roots)==1},sort_keys=True))
if __name__=="__main__":main()
