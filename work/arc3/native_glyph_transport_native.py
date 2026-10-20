"""Collect fresh predeclared LS20 transport holdout with original public SDK."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from work.arc3.native_suffix_probe import take_word
from work.arc3.native_glyph_transport_prediction import WORDS,PROTOCOL

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    prediction=json.loads(a.prediction.read_text())
    if (prediction.get("protocol")!=PROTOCOL or
            prediction.get("new_words_committed_before_native_execution")!=list(WORDS) or
            [p.get("word") for p in prediction.get("predictions",[])]!=list(WORDS)):
        raise ValueError("not the preregistered native word set")
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    records=[]
    images={}
    initial_roots=set()
    for word in WORDS:
        row,frames=take_word(arcade,"ls20",word)
        records.append(row)
        images[word]=np.stack(frames)
        initial_roots.add(row["states"][0]["observation"]["whole"])
    report={"kind":"AB_LS20_GLYPH_TRANSPORT_NATIVE_CAPTURE_V1","protocol":PROTOCOL,
            "words":list(WORDS),"game":"ls20","native_paths":records,
            "all_roots_identical":len(initial_roots)==1,
            "root_hashes":sorted(initial_roots),
            "native_actions":sum(r["steps"] for r in records),
            "recorded_outcomes_not_scored_by_collector":True}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**images)
    print("AB_TRANSPORT_NATIVE_COLLECTED "+json.dumps({
        "words":len(records),"native_actions":report["native_actions"],
        "completed":sum(r["completed"] is True for r in records),
        "roots_equal":report["all_roots_identical"]},sort_keys=True))

if __name__=="__main__":
    main()
