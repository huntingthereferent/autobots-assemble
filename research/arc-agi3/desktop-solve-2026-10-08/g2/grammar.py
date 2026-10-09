from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any
import numpy as np

from symbolic import connected_components, detect_program


@dataclass(frozen=True)
class Resource:
    kind: str       # "terminal" | "call"
    color: int
    click: tuple[int, int]


@dataclass(frozen=True)
class Position:
    kind: str       # "slot" | "fixed_terminal"
    x: int
    click: tuple[int, int] | None = None
    color: int | None = None


@dataclass
class Function:
    color: int
    bbox: tuple[int, int, int, int]
    positions: list[Position]


def _target(g: np.ndarray) -> list[int]:
    out = []
    for q in connected_components(g):
        w = q["x1"] - q["x0"] + 1
        h = q["y1"] - q["y0"] + 1
        if q["size"] == 20 and w == 6 and h == 6 and q["y0"] <= 14:
            out.append((q["y0"], q["x0"], q["color"]))
    return [c for _, _, c in sorted(out)]


def _resources(g: np.ndarray) -> list[Resource]:
    out = []
    for q in connected_components(g):
        w = q["x1"] - q["x0"] + 1
        h = q["y1"] - q["y0"] + 1
        if q["y0"] < 54 or w != 4 or h != 4:
            continue
        click = ((q["x0"] + q["x1"]) // 2, (q["y0"] + q["y1"]) // 2)
        if q["size"] == 16:
            out.append(Resource("terminal", q["color"], click))
        elif q["size"] == 12:
            out.append(Resource("call", q["color"], click))
    return sorted(out, key=lambda r: (r.click[0], r.click[1]))


def _frames(g: np.ndarray) -> list[Function]:
    cs = connected_components(g)
    frame_boxes = []
    for q in cs:
        w = q["x1"] - q["x0"] + 1
        h = q["y1"] - q["y0"] + 1
        if not (10 <= q["y0"] <= 45 and h == 10 and 14 <= w <= 40):
            continue
        if q["color"] in (0, 2, 4, 5):
            continue
        perimeter = 2 * w + 2 * (h - 2)
        if q["size"] < perimeter - 4 or q["size"] > perimeter + 4:
            continue
        frame_boxes.append((q["y0"], q["x0"], q["color"], q["x0"], q["y0"], q["x1"], q["y1"]))

    functions = []
    for _, _, color, x0, y0, x1, y1 in sorted(frame_boxes):
        pos = []
        for q in cs:
            # item must be inside the frame interior
            if not (x0 < q["x0"] and q["x1"] < x1 and y0 < q["y0"] and q["y1"] < y1):
                continue
            w = q["x1"] - q["x0"] + 1
            h = q["y1"] - q["y0"] + 1
            cx = (q["x0"] + q["x1"]) // 2
            cy = (q["y0"] + q["y1"]) // 2
            if q["color"] == 2 and q["size"] == 4 and w == 2 and h == 2:
                pos.append(Position("slot", cx, (cx, cy), None))
            elif q["size"] == 16 and w == 4 and h == 4 and q["color"] not in (0, 2, 4, 5):
                pos.append(Position("fixed_terminal", cx, None, q["color"]))
        pos.sort(key=lambda p: p.x)
        if pos:
            functions.append(Function(color, (x0, y0, x1, y1), pos))
    return functions


def _expand(
    root_color: int,
    funcs: dict[int, Function],
    assignment: dict[tuple[int, int], tuple[str, int]],
    limit: int,
) -> list[int] | None:
    out: list[int] = []
    stack: list[tuple[int, int]] = [(root_color, 0)]
    steps = 0
    max_steps = max(100, limit * 20)

    while stack and len(out) < limit and steps < max_steps:
        steps += 1
        fcolor, idx = stack[-1]
        fn = funcs.get(fcolor)
        if fn is None:
            return None
        if idx >= len(fn.positions):
            stack.pop()
            continue

        stack[-1] = (fcolor, idx + 1)
        p = fn.positions[idx]
        if p.kind == "fixed_terminal":
            out.append(int(p.color))
            continue

        sym = assignment.get((fcolor, idx))
        if sym is None:
            return None
        kind, color = sym
        if kind == "terminal":
            out.append(int(color))
        elif kind == "call":
            if color not in funcs:
                return None
            stack.append((color, 0))
        else:
            return None

    if len(out) < limit:
        return None
    return out[:limit]


def _unique_multiset_permutations(counter: Counter, n: int):
    keys = sorted(counter.keys())
    cur = [None] * n

    def rec(i: int):
        if i == n:
            yield tuple(cur)
            return
        for k in keys:
            if counter[k] <= 0:
                continue
            counter[k] -= 1
            cur[i] = k
            yield from rec(i + 1)
            counter[k] += 1

    yield from rec(0)


def synthesize_recursive_program(g: np.ndarray):
    target = _target(g)
    resources = _resources(g)
    funcs_list = _frames(g)
    if not target or not resources or not funcs_list:
        return None, {
            "target": target,
            "resources": [(r.kind, r.color, r.click) for r in resources],
            "functions": [(f.color, f.bbox, [(p.kind, p.x, p.color) for p in f.positions]) for f in funcs_list],
        }

    funcs = {f.color: f for f in funcs_list}
    root = min(funcs_list, key=lambda f: (f.bbox[1], f.bbox[0]))

    variables = []
    for f in sorted(funcs_list, key=lambda z: (z.bbox[1], z.bbox[0])):
        for idx, p in enumerate(f.positions):
            if p.kind == "slot":
                variables.append((f.color, idx, p.click))

    if len(variables) != len(resources):
        return None, {
            "reason": "resource-slot-count-mismatch",
            "target": target,
            "slot_count": len(variables),
            "resource_count": len(resources),
            "functions": [(f.color, f.bbox, [(p.kind, p.x, p.color) for p in f.positions]) for f in funcs_list],
            "resources": [(r.kind, r.color, r.click) for r in resources],
        }

    type_counter = Counter((r.kind, r.color) for r in resources)
    found = None
    tested = 0
    for perm in _unique_multiset_permutations(type_counter, len(variables)):
        tested += 1
        assignment = {(fc, idx): sym for (fc, idx, _), sym in zip(variables, perm)}
        exp = _expand(root.color, funcs, assignment, len(target))
        if exp == target:
            found = assignment
            break

    if found is None:
        return None, {
            "reason": "no-program-matches-target-prefix",
            "target": target,
            "root": root.color,
            "tested": tested,
            "functions": [(f.color, f.bbox, [(p.kind, p.x, p.color) for p in f.positions]) for f in funcs_list],
            "resources": [(r.kind, r.color, r.click) for r in resources],
        }

    pools: dict[tuple[str, int], list[tuple[int, int]]] = defaultdict(list)
    for r in resources:
        pools[(r.kind, r.color)].append(r.click)

    actions = []
    symbolic = []
    for fc, idx, slot_click in variables:
        sym = found[(fc, idx)]
        if not pools[sym]:
            return None, {"reason": "resource-pool-underflow", "symbol": sym}
        select_click = pools[sym].pop(0)
        actions.append((select_click, slot_click))
        symbolic.append({
            "function": fc,
            "slot_index": idx,
            "symbol": sym,
            "select": select_click,
            "slot": slot_click,
        })

    expansion = _expand(root.color, funcs, found, len(target))
    return {
        "target": target,
        "root": root.color,
        "expansion": expansion,
        "assignments": symbolic,
        "click_pairs": actions,
        "tested": tested,
    }, None


def solve_visible_program(g: np.ndarray):
    # First use the simpler pre-wired-call parser when it applies.
    p, why = detect_program(g)
    if p is not None:
        pairs = [(p["tokens"][c], slot) for c, slot in zip(p["targets"], p["order"])]
        return {
            "mode": "prewired",
            "target": p["targets"],
            "click_pairs": pairs,
        }, None

    p2, why2 = synthesize_recursive_program(g)
    if p2 is not None:
        p2["mode"] = "synthesized"
        return p2, None
    return None, {"prewired": why, "synthesized": why2}
