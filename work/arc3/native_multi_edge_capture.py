"""Real native LS20 collector; never scores frozen geometry predictions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from .native_suffix_probe import take_word
from .native_multi_edge_composition import PROTOCOL

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.prediction.read_text())
    rows=frozen.get("native_holdout_trials",[])
    if (frozen.get("kind")!="AB_NATIVE_MULTI_UNKNOWN_EDGE_FROZEN_V1" or
        frozen.get("protocol")!=PROTOCOL or
        len(rows)!=64 or len({r["word"] for r in rows})!=64):
        raise ValueError("no complete frozen multi-edge source plan")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    sources=[]
    images={}
    roots=set()
    for index,trial in enumerate(rows):
        path,frames=take_word(arcade,"ls20",trial["word"])
        key=f"trial_{index:03d}"
        sources.append({"trial_key":key,"word":trial["word"],
                        "kind":trial["kind"],"native_path":path})
        images[key]=np.stack(frames)
        roots.add(path["states"][0]["observation"]["whole"])
    result={
        "kind":"AB_REAL_NATIVE_MULTI_NEW_EDGE_SOURCE_V1","protocol":PROTOCOL,
        "game":"ls20","native_trajectories":sources,
        "native_actions":sum(v["native_path"]["steps"] for v in sources),
        "all_roots":sorted(roots),
        "collector_does_not_score_predictions":True
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**images)
    print("AB_NATIVE_MULTI_EDGE_CAPTURE "+json.dumps({
        "trials":len(sources),"actions":result["native_actions"],
        "completed":sum(row["native_path"]["completed"] is True for row in sources),
        "same_root":len(roots)==1},sort_keys=True))

if __name__=="__main__":main()
