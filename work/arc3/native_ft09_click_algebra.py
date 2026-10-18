"""Native FT09 click idempotence/commutation compared with original F3 laws.

Coordinates are PREDECLARED FROM THE PREVIOUS EXPERIMENT'S real FT09 8-site
response witness, not a solution path or game source. Two DIFFERENT site pairs
are tested on fresh native resets, preserving entire 64x64 visible frames.

Strictly distinguish native-visible equality from hidden state equality.
F3 mathematical source remains unchanged; no arbitrary modulo mapping.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
import numpy as np

from work.arc_like_maze.math import inverse_candidates
from .native_ft09_f3_clicks import GAME,run_word,native_root
from .native_f3_other_games import digest


# Independent test pairs were observed to produce different nontrivial native
# effects during the prior 74-site spatial scan.
PAIR_COORDS=(
    ((36,36),(44,36)),
    ((36,44),(52,52)),
)
WORDS=("", "A","AA","AAA", "B","BB","BBB",
       "AB","BA","AAB","ABA","ABB","BAB","BBA")
COMPARISONS=(
    ("","A"),("","AAA"),("A","AA"),("AA","AAA"),
    ("","B"),("B","BB"),("BB","BBB"),
    ("AB","BA"),("AB","ABA"),("AB","AAB"),("AB","ABB"),("AB","BAB"),
)


def analyze_pair(arcade,root,locations,i):
    observed={}
    frames={}
    count=0
    for word in WORDS:
        record,raw=run_word(arcade,root,locations,word)
        observed[word]=record
        frames[f"pair_{i}_{word or 'EMPTY'}"]=raw
        count+=record["native_actions"]
    consistent=all(record["root_matches"] and record["status"]=="COMPLETE"
                   for record in observed.values())
    comparisons=[]
    worlds=inverse_candidates()
    for a,b in COMPARISONS:
        left,right=observed[a],observed[b]
        native_equal=(
            left["whole_frame"]==right["whole_frame"] if consistent else None)
        F3_equal=sum(w.apply(a)==w.apply(b) for w in worlds)
        comparisons.append({
            "words":[a,b],
            "actual_native_full_frame_equal":native_equal,
            "F3_worlds_equal":F3_equal,
            "F3_worlds_distinct":9-F3_equal,
        })
    def eq(a,b):
        return (observed[a]["whole_frame"]==observed[b]["whole_frame"]
                if consistent else None)
    return {
        "coordinates":[list(locations[0]),list(locations[1])],
        "complete_and_identical_native_roots":consistent,
        "native_actions":count,
        "native_words":observed,
        "mathematical_comparisons":comparisons,
        "native_A_changes_root":not eq("","A") if consistent else None,
        "native_A_visibly_idempotent_at_root":eq("A","AA"),
        "native_B_changes_root":not eq("","B") if consistent else None,
        "native_B_visibly_idempotent_at_root":eq("B","BB"),
        "native_AB_BA_visible_commutation":eq("AB","BA"),
        "native_root_three_A_return":eq("","AAA"),
    },frames


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/ft09-click-algebra.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env,obs,root=native_root(arcade,GAME)
    results=[]
    arrays={"root":root}
    for i,coords in enumerate(PAIR_COORDS):
        result,grids=analyze_pair(arcade,root,coords,i)
        results.append(result)
        arrays.update(grids)
    output={
        "kind":"FT09_NATIVE_CLICK_TRANSFORMATION_ALGEBRA_VS_ORIGINAL_F3",
        "game":GAME,
        "math_source":"work/arc_like_maze/math.py",
        "native_root_hash":digest(root),
        "coordinates_source":"prior independent native 74-site response scan",
        "predeclared_click_pairs":PAIR_COORDS,
        "predeclared_words":WORDS,
        "predeclared_word_comparisons":COMPARISONS,
        "results":results,
        "native_actions":sum(x["native_actions"] for x in results),
        "boundary":"Visible equalities are rooted frame measurements, NOT complete hidden-state or global operation equalities; selected click positions come from prior native observations; source F3 mathematics not edited; no ARC solve or modulo 3 pixel projection.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("FT09_NATIVE_CLICK_ALGEBRA "+json.dumps({
        "game":GAME,
        "actions":output["native_actions"],
        "cases":[{
            "pair":r["coordinates"],
            "complete":r["complete_and_identical_native_roots"],
            "native_A_changes_root":r["native_A_changes_root"],
            "native_A_idempotent_visible":r["native_A_visibly_idempotent_at_root"],
            "native_B_changes_root":r["native_B_changes_root"],
            "native_B_idempotent_visible":r["native_B_visibly_idempotent_at_root"],
            "native_AB_BA_commute_visible":r["native_AB_BA_visible_commutation"],
            "native_AAA_root_return":r["native_root_three_A_return"],
            "source_comp":[{"words":q["words"],
                            "native_eq":q["actual_native_full_frame_equal"],
                            "F3_equal_worlds":q["F3_worlds_equal"]}
                           for q in r["mathematical_comparisons"]],
        } for r in results],
        "json":str(args.out),"frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))
    if not all(r["complete_and_identical_native_roots"] for r in results):
        raise RuntimeError("FT09 native action observations interrupted; no completed algebraic comparison")


if __name__=="__main__":
    main()
