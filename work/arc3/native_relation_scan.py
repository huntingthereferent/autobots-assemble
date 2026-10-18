"""Inspect native ARC variables BEFORE proposing an F3 state correspondence.

Only real ARC SDK frames/actions. No game source, learned oracle, generated
world, stochastic solver, hard-coded path, or modulo-three pixel projection.

A strict observed 3-cycle is a *candidate witness* for the necessary A^3
relation, NOT evidence of two-generator F3 alignment or hidden-state equality.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import blake2b
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction


def grid(obs) -> np.ndarray:
    a = np.asarray(obs.frame)
    if a.ndim == 3:
        a = a[-1]
    if a.size != 4096:
        raise ValueError("native observation is not a 64x64 grid")
    return a.reshape(64, 64).astype(np.uint8, copy=False)


def digest(g):
    return blake2b(np.ascontiguousarray(g).tobytes(), digest_size=16).hexdigest()


def component_boxes(g, color):
    """4-connected component extents for one EXACT native color (not F3 data)."""
    h, w = g.shape
    mask = g == color
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            seen[y, x] = True
            stack = [(y, x)]
            pts = []
            while stack:
                qy, qx = stack.pop()
                pts.append((qy, qx))
                for ny, nx in ((qy-1,qx),(qy+1,qx),(qy,qx-1),(qy,qx+1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            out.append((len(pts), min(xs), min(ys), max(xs), max(ys)))
    return tuple(sorted(out))



def rigid_color_motion(before, after):
    """Exact transport witness for changed pixels of each unmodified color.

    Identify outgoing/incoming coordinates for each color independently. Only
    report translation when ALL outgoing pixels map to ALL incoming pixels by
    one shift. A color can move while other static cells of that color remain.
    This is native pixel geometry, never a finite-field coordinate.
    """
    touched = before != after
    motions = []
    for color in sorted(set(map(int, before[touched])) | set(map(int, after[touched]))):
        removed = {(int(x), int(y)) for y,x in zip(*np.nonzero(touched & (before == color)))}
        added = {(int(x), int(y)) for y,x in zip(*np.nonzero(touched & (after == color)))}
        if len(removed) != len(added) or len(removed) < 4:
            continue
        anchor_x, anchor_y = min(removed)
        matches = []
        for x,y in added:
            dx,dy = x-anchor_x, y-anchor_y
            if dx == 0 and dy == 0:
                continue
            if {(px+dx,py+dy) for px,py in removed} == added:
                matches.append((dx,dy))
        if len(matches) == 1:
            dx,dy = matches[0]
            motions.append({"native_color":color, "moved_cells":len(removed),
                            "dx":dx,"dy":dy, "exact_transport":True})
    return motions


def native_features(g):
    unique, counts = np.unique(g, return_counts=True)
    count = dict(zip(map(int, unique), map(int, counts)))
    background = max(count, key=count.get)
    features = {}
    for color in sorted(count):
        ys, xs = np.nonzero(g == color)
        features[f"color:{color}:count"] = count[color]
        # Include centroid and bounding box as observational properties,
        # never assume colors denote mathematical field elements.
        features[f"color:{color}:bbox"] = (int(xs.min()), int(ys.min()),
                                            int(xs.max()), int(ys.max()))
        features[f"color:{color}:center2"] = (int(xs.sum() * 2), int(ys.sum() * 2), count[color])
        if color != background:
            components = component_boxes(g, color)
            features[f"color:{color}:components"] = components
    features["full-frame"] = digest(g)
    return features


def compact_delta(before, after):
    change = before != after
    ys, xs = np.nonzero(change)
    if len(xs) == 0:
        return {"changed_cells": 0, "bbox": None, "color_exchanges": []}
    pairs = Counter((int(before[y,x]),int(after[y,x])) for y,x in zip(ys,xs))
    return {
        "changed_cells": int(len(xs)),
        "bbox": [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
        "exact_color_translations": rigid_color_motion(before, after),
        "color_exchanges": [
            {"before": a, "after": b, "cells": n}
            for (a,b), n in pairs.most_common(12)
        ],
    }


def feature_cycle(features):
    """Find period-three return AFTER visible change, not static equality."""
    names = set(features[0])
    for f in features[1:]:
        names &= set(f)
    states = []
    for name in sorted(names):
        vals = [f[name] for f in features]
        # Qualifies as nontrivial three-step return at this root only if it
        # exhibits THREE distinct observable values before returning.
        first_three = [json.dumps(v, sort_keys=True) for v in vals[:3]]
        if len(set(first_three)) == 3 and vals[0] == vals[3]:
            states.append({
                "feature": name,
                "values": [str(v)[:160] for v in vals],
                "status": "OBSERVED_3_RETURN_NOT_F3_CORRESPONDENCE",
            })
    return states


def ascii_root(g, max_rows=64):
    # Full exact grid in hexadecimal native color notation, not field values.
    symbols = "0123456789ABCDEF"
    return "\n".join(f"{y:02d} "+ "".join(symbols[int(c)] for c in g[y]) for y in range(min(max_rows,len(g))))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--game", default="ls20")
    p.add_argument("--out", type=Path, default=Path("runtime/data/arc3/f3-relation-scan.json"))
    args = p.parse_args()

    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    probes = []
    frames = {}
    root_ascii = None
    for act in (1,2,3,4,5):
        env = arcade.make(args.game)
        if env is None:
            raise RuntimeError("native ARC public environment unavailable")
        initial = env.reset()
        legal = {int(getattr(a, "value", a)) for a in (initial.available_actions or ())}
        if act not in legal:
            continue
        before = grid(initial).copy()
        if root_ascii is None:
            root_ascii = ascii_root(before)
        states = [before]
        level = int(getattr(initial,"levels_completed",0))
        metadata = [{"state":str(getattr(initial,"state",None)),
                     "levels_completed":level, "hash":digest(before)}]
        deltas = []
        interrupted = False
        for i in range(3):
            obs = env.step(getattr(GameAction, "ACTION"+str(act)))
            if obs is None or getattr(obs,"frame",None) is None:
                interrupted = True
                break
            after = grid(obs).copy()
            deltas.append(compact_delta(before,after))
            states.append(after)
            metadata.append({"state":str(getattr(obs,"state",None)),
                             "levels_completed":int(getattr(obs,"levels_completed",0)),
                             "hash":digest(after)})
            if int(getattr(obs,"levels_completed",0)) != level:
                interrupted = True
                break
            before = after
        if not interrupted and len(states) == 4:
            features = [native_features(g) for g in states]
            candidates = feature_cycle(features)
        else:
            candidates = []
        probes.append({
            "action":act,
            "metadata":metadata,
            "deltas":deltas,
            "nontrivial_observed_three_returns":candidates,
            "complete_same_level": not interrupted and len(states)==4,
            "raw_full_frame_root_return": len(states)==4 and np.array_equal(states[0],states[-1]),
        })
        frames[f"action{act}"] = np.stack(states)

    if not probes:
        raise RuntimeError("no advertised simple native actions")
    result = {
        "kind":"F3_OBSERVABLE_RELATION_SCAN_OVER_NATIVE_FRAMES",
        "game":args.game,
        "mathematical_requirement":"F3 A^3 = identity",
        "observation_source":"official arc-agi Arcade NORMAL; independently reset for every action",
        "features":"exact native full frame, per-original-color count, bbox, center2, components",
        "interpretation":"3-return is necessary, not sufficient, for a witnessed F3 generator; no modulo color reduction or game-ID solution policy",
        "probes":probes,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **frames)
    print("F3_NATIVE_FRAME_ROOT\n"+(root_ascii or ""))
    print("F3_NATIVE_RELATION_SCAN "+json.dumps({
        "game":args.game,
        "probes":[{
            "action":r["action"],
            "hashes":[m["hash"] for m in r["metadata"]],
            "changed_cells":[d["changed_cells"] for d in r["deltas"]],
            "bbox":[d["bbox"] for d in r["deltas"]],
            "first_color_exchanges":[d["color_exchanges"][:5] for d in r["deltas"]],
            "exact_color_translations":[d["exact_color_translations"] for d in r["deltas"]],
            "three_returns":r["nontrivial_observed_three_returns"],
            "raw_frame_3_return":r["raw_full_frame_root_return"],
        } for r in probes],
        "record":str(args.out),
        "raw_frames":str(args.out.with_suffix(".npz")),
    },sort_keys=True))

if __name__ == "__main__":
    main()
