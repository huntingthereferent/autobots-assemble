"""Execute fixed native LS20 unknown-edge trials; collector never scores predictions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from .native_suffix_probe import take_word
from .native_geometry_unknown_edge import WORDS,PROTOCOL

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.frozen.read_text())
    if frozen.get("protocol")!=PROTOCOL or frozen.get("frozen_holdout_words")!=list(WORDS):
        raise ValueError("native execution not bound to frozen source-word set")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    paths=[]
    raw={}
    for word in WORDS:
        path,frames=take_word(arcade,"ls20",word)
        paths.append(path)
        raw[word]=np.stack(frames)
    receipt={"kind":"AB_LS20_UNKNOWN_GEOMETRY_RAW_FRAMES_V1",
        "protocol":PROTOCOL,"game":"ls20","words":list(WORDS),
        "trajectories":paths,"native_actions":sum(x["steps"] for x in paths),
        "collector_does_not_score_predictions":True}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**raw)
    print("AB_NATIVE_UNKNOWN_EDGES_CAPTURED "+json.dumps({
        "words":len(paths),"actions":receipt["native_actions"],
        "completed":sum(x["completed"] is True for x in paths)},sort_keys=True))

if __name__=="__main__":main()
