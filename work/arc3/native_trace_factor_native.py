"""Collect and preserve new LS20 native words without evaluating predictions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from .native_suffix_probe import take_word
from .native_trace_factor_prediction import NATIVE_WORDS, PROTOCOL

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    prereg=json.loads(a.prediction.read_text())
    if prereg.get("protocol")!=PROTOCOL or prereg.get("committed_holdout_words")!=list(NATIVE_WORDS):
        raise ValueError("native execution is not bound to the frozen word set")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    roots=set()
    records=[]
    arrays={}
    actions=0
    for word in NATIVE_WORDS:
        path,frames=take_word(arcade,"ls20",word)
        arrays[word]=np.stack(frames)
        roots.add(path["states"][0]["observation"]["whole"])
        actions+=path["steps"]
        records.append(path)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    record={
        "kind":"AB_LS20_REAL_NATIVE_HOLDOUT_RAW_FRAMES_V1",
        "protocol":PROTOCOL,
        "game":"ls20",
        "declared_words":list(NATIVE_WORDS),
        "independent_reset_count":len(records),
        "completed_trajectories":sum(r["completed"] is True for r in records),
        "native_actions":actions,
        "all_roots_identical":len(roots)==1,
        "root_hashes":sorted(roots),
        "native_paths":records,
        "results_not_predicted_by_collector":True,
        "no_implicit_F3_mapping":True,
    }
    a.out.write_text(json.dumps(record,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**arrays)
    print("AB_NATIVE_HOLDOUT_COLLECTED "+json.dumps({
        "words":len(records),"actions":actions,
        "completed":record["completed_trajectories"],
        "roots_identical":record["all_roots_identical"]},sort_keys=True))
if __name__=="__main__":
    main()
