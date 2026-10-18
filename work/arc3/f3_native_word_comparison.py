"""Compare *observed native word equalities* to original F3 rooted predictions.

Uses existing work.arc_like_maze.math.World; does not identify ARC's controls
with mathematical A/B without witness. Does not treat equal visible frames as
proof of equal hidden states. No ARC actuator, simulated ARC, solver or bot.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from work.arc_like_maze.math import inverse_candidates


def compare_words(record: dict) -> list[dict]:
    lookup = record["traces"]
    worlds = inverse_candidates()
    out = []
    for row in record["word_comparisons"]:
        left, right = row["words"]
        assert len(left) == 2 and len(right) == 2
        f3_equal_count = sum(w.apply("AB") == w.apply("BA") for w in worlds)
        if f3_equal_count != 0:
            raise AssertionError("original F3 rooted noncommutation changed")
        observed_equal = bool(row["same_full_frame"])
        # F3 AB != BA is necessary; visible inequality agrees, but isn't a
        # complete native-F3 state correspondence. Visible equality may conceal
        # distinct hidden states and so is NOT a universal F3 refutation.
        interpretation = (
            "CONSISTENT_NECESSARY_NONCOMMUTATION_ONLY" if not observed_equal
            else "VISIBLE_COLLISION_HIDDEN_STATE_UNKNOWN"
        )
        out.append({
            "native_ordered_pair": [int(left[0]), int(left[1])],
            "native_word_pair": [left, right],
            "native_visible_frames_equal": observed_equal,
            "native_glyph_masks_equal": bool(row["same_glyph_mask"]),
            "native_trace_masks_equal": bool(row["same_trace_mask"]),
            "F3_rooted_AB_equals_BA_count": f3_equal_count,
            "F3_declared_candidate_count": len(worlds),
            "interpretation": interpretation,
            "direct_A_cube_constraint": (
                "already contradicted for each single ACTION1..4 in"
                " LS20 native generator probes"
            ),
        })
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    raw=json.loads(args.native.read_text())
    if raw.get("kind")!="NATIVE_ARC_MIXED_ACTION_RELATIONS_FROM_PREOBSERVED_COLOR_GROUPS":
        raise ValueError("not an accepted native mixed-word witness")
    rows=compare_words(raw)
    result={
        "kind":"F3_ORIGINAL_LAWS_VS_NATIVE_ROOTED_WORD_RELATIONS",
        "original_math":"work/arc_like_maze/math.py",
        "native_source_sha256":__import__("hashlib").sha256(args.native.read_bytes()).hexdigest(),
        "comparisons":rows,
        "boundary":(
            "Equal native visible frames are not hidden state equality; "
            "matching qualitative relations are necessary, not sufficient. "
            "No direct F3 realization or ARC game solve is established."
        )
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print("F3_VS_NATIVE_WORDS "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
