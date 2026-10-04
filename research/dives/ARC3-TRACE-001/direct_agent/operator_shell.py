"""Interactive ARC-AGI-3 operator shell for first-contact play.

This is the control surface intended for ChatGPT + an authorized computer.
It uses the official public ARC runtime, exposes only observations/actions,
and records an append-only transcript.

Example:
    python operator_shell.py --game ls20 --log runs/ls20.jsonl

Commands:
    show
    info
    act 1
    act 6 31 22
    reset
    save-frame frame.npy
    quit
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
from datetime import datetime, timezone

import numpy as np

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction


SIMPLE = {
    1: GameAction.ACTION1,
    2: GameAction.ACTION2,
    3: GameAction.ACTION3,
    4: GameAction.ACTION4,
    5: GameAction.ACTION5,
    7: GameAction.ACTION7,
}


def latest_grid(obs) -> np.ndarray:
    a = np.asarray(obs.frame)
    if a.ndim == 3:
        a = a[-1]
    return a.reshape(64, 64).astype(np.int8, copy=False)


def digest(g: np.ndarray) -> str:
    return hashlib.blake2b(np.ascontiguousarray(g).tobytes(), digest_size=12).hexdigest()


def diff_summary(a: np.ndarray | None, b: np.ndarray) -> dict:
    if a is None:
        return {"changed_cells": None, "bbox": None}
    ys, xs = np.where(a != b)
    if len(xs) == 0:
        return {"changed_cells": 0, "bbox": None}
    return {
        "changed_cells": int(len(xs)),
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
    }


def color_counts(g: np.ndarray) -> list[list[int]]:
    vals, counts = np.unique(g, return_counts=True)
    return [[int(v), int(n)] for v, n in zip(vals, counts)]


def components(g: np.ndarray) -> list[dict]:
    h, w = g.shape
    seen = np.zeros_like(g, dtype=bool)
    raw = []
    for y in range(h):
        for x in range(w):
            if seen[y, x]:
                continue
            color = int(g[y, x])
            stack = [(y, x)]
            seen[y, x] = True
            pts = []
            while stack:
                cy, cx = stack.pop()
                pts.append((cy, cx))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and int(g[ny, nx]) == color:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            raw.append({
                "color": color,
                "size": len(pts),
                "bbox": [min(xs), min(ys), max(xs), max(ys)],
            })
    if raw:
        biggest = max(range(len(raw)), key=lambda i: raw[i]["size"])
        raw = [c for i, c in enumerate(raw) if i != biggest]
    raw.sort(key=lambda c: (c["color"], c["size"], c["bbox"]))
    return raw


def crop_bounds(g: np.ndarray, pad: int = 2) -> tuple[int, int, int, int]:
    vals, counts = np.unique(g, return_counts=True)
    bg = int(vals[int(np.argmax(counts))])
    ys, xs = np.where(g != bg)
    if len(xs) == 0:
        return 0, 0, 63, 63
    return (
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(63, int(xs.max()) + pad),
        min(63, int(ys.max()) + pad),
    )


SYMS = "0123456789ABCDEF"


def ascii_crop(g: np.ndarray, bounds=None) -> str:
    x0, y0, x1, y1 = bounds or crop_bounds(g)
    rows = []
    rows.append(f"crop x={x0}..{x1} y={y0}..{y1}")
    rows.append("    " + "".join(str((x // 10) % 10) if x % 10 == 0 else " " for x in range(x0, x1 + 1)))
    rows.append("    " + "".join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        rows.append(f"{y:02d}  " + "".join(SYMS[int(v)] for v in g[y, x0:x1+1]))
    return "\n".join(rows)


def serialize_obs(obs, grid: np.ndarray, previous: np.ndarray | None) -> dict:
    available = []
    for a in getattr(obs, "available_actions", []) or []:
        available.append(int(getattr(a, "value", a)))
    return {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "frame_hash": digest(grid),
        "state": str(getattr(obs, "state", None)),
        "levels_completed": int(getattr(obs, "levels_completed", 0)),
        "win_levels": int(getattr(obs, "win_levels", 0)),
        "available_actions": sorted(available),
        "diff_from_previous": diff_summary(previous, grid),
        "color_counts": color_counts(grid),
        "components": components(grid)[:80],
        "crop": list(crop_bounds(grid)),
    }


class Session:
    def __init__(self, game: str, log: Path):
        self.game = game
        self.log = log
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
        self.env = self.arcade.make(game)
        if self.env is None:
            raise RuntimeError(f"Could not create ARC environment {game!r}")
        self.obs = self.env.reset()
        self.previous_grid = None
        self.grid = latest_grid(self.obs)
        self._append({"event": "session_start", "game": game, "observation": self.summary()})

    def _append(self, row: dict) -> None:
        with self.log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")

    def summary(self) -> dict:
        return serialize_obs(self.obs, self.grid, self.previous_grid)

    def show(self) -> None:
        print(json.dumps(self.summary(), indent=2))
        print(ascii_crop(self.grid, tuple(self.summary()["crop"])))

    def reset(self) -> None:
        before = self.grid.copy()
        self.previous_grid = before
        self.obs = self.env.reset()
        self.grid = latest_grid(self.obs)
        row = {"event": "reset", "observation": self.summary()}
        self._append(row)
        self.show()

    def act(self, action_id: int, x: int | None = None, y: int | None = None) -> None:
        before = self.grid.copy()
        before_hash = digest(before)
        if action_id == 6:
            if x is None or y is None:
                raise ValueError("ACTION6 requires x y")
            obs = self.env.step(GameAction.ACTION6, {"x": int(x), "y": int(y)})
            action = [6, int(x), int(y)]
        else:
            if action_id not in SIMPLE:
                raise ValueError("action must be 1..7 (6 requires x y)")
            obs = self.env.step(SIMPLE[action_id])
            action = [action_id]

        self.previous_grid = before
        if obs is None or getattr(obs, "frame", None) is None:
            self._append({
                "event": "action",
                "action": action,
                "before_hash": before_hash,
                "terminal_without_frame": True,
            })
            print(json.dumps({"action": action, "terminal_without_frame": True}, indent=2))
            return

        self.obs = obs
        self.grid = latest_grid(obs)
        row = {
            "event": "action",
            "action": action,
            "before_hash": before_hash,
            "observation": self.summary(),
        }
        self._append(row)
        self.show()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--game", required=True)
    p.add_argument("--log", type=Path, default=None)
    args = p.parse_args()

    log = args.log or Path("arc3_operator_runs") / f"{args.game}.jsonl"
    s = Session(args.game, log)
    print(f"ARC3 operator shell: {args.game} | log={log}")
    s.show()

    while True:
        try:
            line = input("arc3> ").strip()
        except EOFError:
            break
        if not line:
            continue
        parts = shlex.split(line)
        cmd = parts[0].lower()
        try:
            if cmd in {"quit", "exit", "q"}:
                break
            if cmd == "show":
                s.show()
            elif cmd == "info":
                print(json.dumps(s.summary(), indent=2))
            elif cmd == "reset":
                s.reset()
            elif cmd == "act":
                nums = [int(v) for v in parts[1:]]
                if not nums:
                    raise ValueError("usage: act ACTION [x y]")
                s.act(nums[0], *(nums[1:] + [None, None])[:2])
            elif cmd == "save-frame":
                if len(parts) != 2:
                    raise ValueError("usage: save-frame PATH")
                np.save(parts[1], s.grid)
                print(parts[1])
            else:
                print("commands: show | info | act A [x y] | reset | save-frame PATH | quit")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
