"""Predeclared NEW native ARC LS20 suffix trial, using original SDK runtime."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from .native_suffix_probe import take_word, outcome
from .native_observation_bridge import PREFIXES, NEW_SUFFIXES

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--game",default="ls20")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    rows=[]
    raw={}
    roots=set()
    actions=0
    counts={}
    for leftword,rightword,expected in PREFIXES:
        for suffix in NEW_SUFFIXES:
            left,frames_left=take_word(arcade,a.game,leftword+suffix)
            right,frames_right=take_word(arcade,a.game,rightword+suffix)
            roots.update((left["states"][0]["observation"]["whole"],
                          right["states"][0]["observation"]["whole"]))
            name=leftword+"_"+rightword+"_suffix_"+suffix
            raw[name+"_a"]=np.stack(frames_left)
            raw[name+"_b"]=np.stack(frames_right)
            actions+=left["steps"]+right["steps"]
            comp=outcome(left,right,boundary=len(leftword),expected_prefix_equal=expected)
            status=comp.get("status",comp.get("classification"))
            counts[status]=counts.get(status,0)+1
            rows.append({"prefix_pair":[leftword,rightword],"suffix":suffix,
                         "previous_relation":"VISIBLE_EQUAL" if expected else "VISIBLE_UNEQUAL",
                         "comparison":comp,"native_left":left,"native_right":right})
    report={"kind":"ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION",
            "protocol":"AB_LS20_INDEPENDENT_SUFFIX_V2","game":a.game,
            "predeclared_prefixes":PREFIXES,"predeclared_suffixes":NEW_SUFFIXES,
            "all_runs_start_at_identical_root_frame":len(roots)==1,
            "distinct_native_root_hashes":sorted(roots),
            "native_actions_including_independent_repetitions":actions,
            "comparisons":rows,"classification_counts":counts,
            "native_only_no_F3_mapping":True,"no_game_solution_claim":True}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**raw)
    print("AB_NATIVE_OUT_OF_SAMPLE "+json.dumps({"comparisons":len(rows),
        "actions":actions,"roots_identical":len(roots)==1,"statuses":counts},sort_keys=True))
if __name__=="__main__":main()
