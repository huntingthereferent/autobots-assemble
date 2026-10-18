"""Test native mixed-action relations against separately observed moving glyph/trace.

Native full-state equality, color-group equality, and trace evidence remain
separate. This is a 2-step relation probe, not an F3 mapping or solver.
"""
from __future__ import annotations

import argparse
from hashlib import blake2b
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_relation_scan import grid, rigid_color_motion, compact_delta


# Color group was independently discovered in the native constant-action scan:
# exact, co-transported colored pixels 9 (15 cells) and 12 (10 cells).
GLYPH_COLORS = (9, 12)
# Color 11 independently loses 2 cells per native step in the same experiment.
TRACE_COLOR = 11
SEQUENCES = ((3, 4), (4, 3), (2, 1), (1, 2), (2, 3), (3, 2))


def snapshot(g):
    return {
        "whole": blake2b(g.tobytes(),digest_size=16).hexdigest(),
        "glyph": blake2b(np.isin(g, GLYPH_COLORS).astype(np.uint8).tobytes(),digest_size=16).hexdigest(),
        "trace": blake2b((g == TRACE_COLOR).astype(np.uint8).tobytes(),digest_size=16).hexdigest(),
        "glyph_by_color": {
            str(c): blake2b((g == c).astype(np.uint8).tobytes(),digest_size=16).hexdigest()
            for c in GLYPH_COLORS
        },
        "trace_cells": int(np.count_nonzero(g == TRACE_COLOR)),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--game", default="ls20")
    p.add_argument("--out",type=Path,default=Path("runtime/data/arc3/f3-native-mixed-words.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    observations={}
    full_grids={}
    for sequence in SEQUENCES:
        env=arcade.make(args.game)
        if env is None:
            raise RuntimeError("official ARC game missing")
        obs=env.reset()
        root=grid(obs).copy()
        frames=[root]
        deltas=[]
        before=root
        interrupted=False
        level=int(getattr(obs,"levels_completed",0))
        legal={int(getattr(a,"value",a)) for a in (getattr(obs,"available_actions",[]) or [])}
        if any(n not in legal for n in sequence):
            continue
        for n in sequence:
            result=env.step(getattr(GameAction,"ACTION"+str(n)))
            if result is None or getattr(result,"frame",None) is None:
                interrupted=True
                break
            after=grid(result).copy()
            delta=compact_delta(before, after)
            deltas.append({
                "action":n,
                "changed_cells":delta["changed_cells"],
                "color_translations":delta["exact_color_translations"],
                "color_exchanges":delta["color_exchanges"],
            })
            frames.append(after)
            before=after
            if int(getattr(result,"levels_completed",0))!=level:
                interrupted=True
                break
        if interrupted or len(frames)!=3:
            observations["".join(map(str,sequence))]={"interrupted":True,"deltas":deltas}
            continue
        snapshots=[snapshot(g) for g in frames]
        word="".join(map(str,sequence))
        observations[word]={
            "interrupted":False,
            "states":snapshots,
            "deltas":deltas,
            "full_root_return":snapshots[0]["whole"]==snapshots[-1]["whole"],
            "glyph_root_return":snapshots[0]["glyph"]==snapshots[-1]["glyph"],
            "trace_root_return":snapshots[0]["trace"]==snapshots[-1]["trace"],
        }
        full_grids[word]=np.stack(frames)
    pairs=[]
    for word in ("34","12","23"):
        other=word[::-1]
        if word in observations and other in observations and not any(observations[q]["interrupted"] for q in (word,other)):
            a=observations[word]["states"][-1]
            b=observations[other]["states"][-1]
            pairs.append({
                "words":[word,other],
                "same_full_frame":a["whole"]==b["whole"],
                "same_glyph_mask":a["glyph"]==b["glyph"],
                "same_trace_mask":a["trace"]==b["trace"],
            })
    result={
        "kind":"NATIVE_ARC_MIXED_ACTION_RELATIONS_FROM_PREOBSERVED_COLOR_GROUPS",
        "game":args.game,
        "predeclared_glyph_colors":GLYPH_COLORS,
        "predeclared_trace_color":TRACE_COLOR,
        "relation_boundary":"raw ARC pixels; no F3 color reduction, conjugacy claim, simulator, or goal inference",
        "traces":observations,
        "word_comparisons":pairs,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**full_grids)
    print("F3_NATIVE_MIXED_RELATIONS "+json.dumps({
        "game":args.game,
        "words":[{
            "word":word,
            "interrupted":o["interrupted"],
            "glyph_root_return":o.get("glyph_root_return"),
            "trace_root_return":o.get("trace_root_return"),
            "full_root_return":o.get("full_root_return"),
            "deltas":o["deltas"]
        } for word,o in observations.items()],
        "word_comparisons":pairs,
        "record":str(args.out)
    },sort_keys=True))

if __name__=="__main__":
    main()
