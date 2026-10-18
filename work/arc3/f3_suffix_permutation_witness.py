"""Compare extended *native* rooted word data with exact source F3 permutation laws.

The original depth-three A/B maps are bijective, so distinct mathematical
endpoints cannot be merged by the SAME right-hand action suffix. Native
visibly distinct->equal endpoints are an obstruction ONLY to a literal
injective visible-state realization, not a proof of hidden-state equality.
No alteration to F3 definitions and no ARC game controls here.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from work.arc_like_maze.math import inverse_candidates


def convert(word: str) -> str:
    if not set(word) <= {"1","2"}:
        raise ValueError("no mathematical generator map admitted for other ARC controls")
    return "".join("A" if c == "1" else "B" for c in word)


def exact_math_witness(left: str, right: str) -> dict:
    """Source-based, enumerated nine-law check, not a native solver."""
    worlds = inverse_candidates()
    f3l, f3r = convert(left), convert(right)
    endpoints = tuple((w.apply(f3l), w.apply(f3r)) for w in worlds)
    return {
        "math_left": f3l, "math_right": f3r,
        "nine_F3_worlds_with_equal_endpoints": sum(x == y for x,y in endpoints),
        "nine_F3_worlds_with_unequal_endpoints": sum(x != y for x,y in endpoints),
        "exact_F3_endpoints": [
            {"phi":list(w.phi),"left":list(e[0]),"right":list(e[1])}
            for w,e in zip(worlds,endpoints)
        ],
    }


def audit(native: dict) -> dict:
    if native.get("kind") != "ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION":
        raise ValueError("requires genuine native suffix result manifest")
    if native.get("all_runs_start_at_identical_root_frame") is not True:
        raise ValueError("native starting frames do not agree")
    out=[]
    for row in native["comparisons"]:
        left,right=row["prefix_pair"]
        suffix=row["suffix"]
        if not (set(left+right+suffix) <= {"1","2"}):
            continue  # actual native actions 3/4 are not named F3 generators
        comp=row["comparison"]
        if not comp.get("previously_observed_prefix_relation_reproduced"):
            raise ValueError("predeclared native prefix relation not reproduced")
        if comp.get("observed_equal_prefix_frames"):
            raise ValueError("native prefix did not exhibit required visible distinction")
        before=exact_math_witness(left,right)
        after=exact_math_witness(left+suffix,right+suffix)
        if before["nine_F3_worlds_with_unequal_endpoints"] != 9:
            raise AssertionError("original F3 AB/BA witness changed")
        if after["nine_F3_worlds_with_unequal_endpoints"] != 9:
            raise AssertionError("the source F3 A/B bijectivity claim failed")
        visible_convergence=bool(comp["observed_equal_suffix_frames"])
        out.append({
            "native_prefix_pair":[left,right],
            "native_common_suffix":suffix,
            "native_visible_prefix_distinct":True,
            "native_visible_suffix_equal":visible_convergence,
            "F3_source_math_before":before,
            "F3_source_math_after":after,
            "finding":("OBSTRUCTION_TO_DIRECT_INJECTIVE_VISIBLE_F3_REALIZATION"
                       if visible_convergence
                       else "NECESSARY_DISTINCTION_PRESERVED_ONLY"),
            "qualification": (
                "native equality is equality of complete 64x64 visible frames, not hidden-state "
                "equality; F3 endpoints are full mathematical states, so no hidden-state "
                "impossibility or F3 quotient inference follows"
            )
        })
    return {
        "kind":"F3_EXACT_PERMUTATION_WITNESS_VS_NATIVE_SUFFIX",
        "mathematical_source":"work/arc_like_maze/math.py:World.step",
        "native_manifest_sha256":sha256(json.dumps(native,sort_keys=True).encode()).hexdigest(),
        "tested_1_2_mapping":"provisional ACTION1=A, ACTION2=B ONLY",
        "comparable_suffixes":out,
        "direct_injective_visible_F3_obstructions":sum(
            x["native_visible_suffix_equal"] for x in out),
        "scope":"No other controls mapped; native hidden states not witnessed; no ARC solve claimed.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(args.native.read_text())
    report=audit(data)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print("F3_NATIVE_SUFFIX_PERMUTATION "+json.dumps({
        "mapping":report["tested_1_2_mapping"],
        "tested":len(report["comparable_suffixes"]),
        "direct_visible_F3_obstructions":report["direct_injective_visible_F3_obstructions"],
        "rows":[{
            "native_prefix":x["native_prefix_pair"],"suffix":x["native_common_suffix"],
            "native_visible_suffix_equal":x["native_visible_suffix_equal"],
            "F3_nine_worlds_distinct":x["F3_source_math_after"]["nine_F3_worlds_with_unequal_endpoints"],
            "finding":x["finding"]
        } for x in report["comparable_suffixes"]],
        "record":str(args.out),
    },sort_keys=True))


if __name__ == "__main__":
    main()
