"""Direct ARC operator-transcript lane: observation only, never game actuation.

This module cannot start the ARC SDK, choose actions, or pretend a saved route
is a first-contact solve. It only summarizes the existing operator shell's
native-session log and writes an explicitly invoked workspace return point.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from systems.workspace import WorkspaceStore

LANE_ID = "arc3-direct-observation"
SOURCES = (
    "research/dives/ARC3-TRACE-001/DIRECT_SOLVE.md",
    "research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py",
    "research/dives/ARC3-TRACE-001/direct_agent/OPERATOR.md",
    "runtime/ARC_NATIVE_OBSERVATIONS.md",
)


def open_arc_lane(store: WorkspaceStore, *, actor_id: str = "james"):
    existing = next((lane for lane in store.lanes() if lane.lane_id == LANE_ID), None)
    if existing:
        if existing.actor_id != actor_id:
            raise ValueError("existing ARC lane belongs to another actor")
        return existing
    return store.open_lane(
        LANE_ID,
        label="ARC-AGI-3 — direct observation",
        referent="solve native ARC-AGI-3 games from observed actions",
        actor_id=actor_id,
        sources=SOURCES,
    )


def _frame_hash(obs: dict) -> str:
    value = obs.get("frame_hash")
    if not isinstance(value, str) or len(value) != 24 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("missing or invalid source-reported frame hash")
    return value


def _action(value) -> list[int]:
    if not isinstance(value, list) or not value or any(type(x) is not int for x in value):
        raise ValueError("invalid ARC action")
    if value[0] == 6:
        if len(value) != 3 or not all(0 <= n < 64 for n in value[1:]):
            raise ValueError("ACTION6 requires in-frame x/y")
    elif value[0] not in (1, 2, 3, 4, 5, 7) or len(value) != 1:
        raise ValueError("unrecognized ARC action")
    return value


def summarize_operator_trace(path: str | Path) -> dict:
    """Check internal transcript continuity, not independently replay ARC pixels."""
    raw = Path(path).read_bytes()
    if not raw or len(raw) > 32_000_000:
        raise ValueError("empty or oversized ARC operator transcript")
    lines = raw.decode("utf-8").splitlines()
    if any(not line.strip() for line in lines):
        raise ValueError("blank ARC transcript event")
    rows = [json.loads(line) for line in lines]
    start = rows[0]
    if start.get("event") != "session_start" or not isinstance(start.get("game"), str) or not start["game"]:
        raise ValueError("operator transcript must begin with session_start")
    prev = _frame_hash(start.get("observation") or {})
    steps = []
    resets = 0
    last = start["observation"]
    ended = False
    for pos, row in enumerate(rows[1:], 2):
        if ended:
            raise ValueError("an action appears after a frameless terminal event")
        event = row.get("event")
        if event not in ("action", "reset"):
            raise ValueError(f"unexpected operator event at line {pos}")
        if event == "action":
            act = _action(row.get("action"))
            if row.get("before_hash") != prev:
                raise ValueError(f"broken before/after frame-hash chain at line {pos}")
            if row.get("terminal_without_frame") is True:
                steps.append({"action": act, "changed_cells": None, "bbox": None,
                              "level_delta": None, "terminal_without_frame": True})
                ended = True
                continue
        else:
            act = None
            resets += 1
        obs = row.get("observation")
        if not isinstance(obs, dict):
            raise ValueError(f"missing observation at line {pos}")
        next_hash = _frame_hash(obs)
        delta = obs.get("diff_from_previous")
        if not isinstance(delta, dict):
            raise ValueError(f"missing observed delta at line {pos}")
        changed = delta.get("changed_cells")
        if type(changed) is not int or changed < 0 or changed > 4096:
            raise ValueError(f"invalid changed-cell count at line {pos}")
        bbox = delta.get("bbox")
        if changed == 0 and bbox is not None:
            raise ValueError("zero changed cells cannot have a bounding box")
        if changed > 0 and (
            not isinstance(bbox, list) or len(bbox) != 4 or
            any(type(n) is not int or n < 0 or n >= 64 for n in bbox) or
            bbox[0] > bbox[2] or bbox[1] > bbox[3]
        ):
            raise ValueError("invalid changed-cell bounding box")
        level_before, level_after = last.get("levels_completed"), obs.get("levels_completed")
        if type(level_before) is not int or type(level_after) is not int or level_before < 0 or level_after < 0:
            raise ValueError("invalid levels_completed")
        if event == "action" and level_after < level_before:
            raise ValueError("level count decreased without a reset")
        if event == "action":
            steps.append({"action": act, "changed_cells": changed, "bbox": bbox,
                          "level_delta": level_after - level_before,
                          "terminal_without_frame": False})
        last = obs
        prev = next_hash
    return {
        "kind": "ARC3_OPERATOR_SOURCE_REPORTED",
        "game": start["game"],
        "sha256": hashlib.sha256(raw).hexdigest(),
        "environment_actions": len(steps),
        "resets_recorded_separately": resets,
        "frames_reported_after_actions": sum(not x["terminal_without_frame"] for x in steps),
        "last_frame_hash": prev,
        "last_state": last.get("state"),
        "last_levels_completed": last.get("levels_completed"),
        "steps": steps,
        "boundary": "log hashes and deltas checked for internal consistency; no raw-frame or native SDK replay",
    }


def record_trace(store: WorkspaceStore, summary: dict, *, actor_id: str = "james"):
    if summary["frames_reported_after_actions"] < 1:
        raise ValueError("no native post-action observation; nothing to record")
    open_arc_lane(store, actor_id=actor_id)
    evidence = f"operator-log-sha256:{summary['sha256']}"
    if any(evidence in ev.get("data", {}).get("evidence_refs", ())
           for ev in store.history(LANE_ID)):
        return store.get_lane(LANE_ID)
    return store.record_movement(
        LANE_ID,
        changes=(f"{summary['game']}: {summary['environment_actions']} source-reported actions, "
                 f"{summary['resets_recorded_separately']} resets; actual deltas in original log"),
        preserved="Prior replay and autonomous-trial outcomes remain distinct from this session.",
        next_movement="Inspect native frames; predict the next action effect before acting and test it.",
        evidence_refs=(evidence, "source:research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py"),
        walls=("Log-level validation is not independent frame replay or a game-win witness.",),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Direct ARC-AGI-3 observation work lane; no game control")
    commands = parser.add_subparsers(dest="command", required=True)
    opening = commands.add_parser("open", help="open independent lane in a local workspace journal")
    opening.add_argument("--journal", type=Path, default=Path("runtime/data/workspace.jsonl"))
    opening.add_argument("--actor-id", default="james")
    inspection = commands.add_parser("inspect", help="read source-reported operator transcript")
    inspection.add_argument("--trace", type=Path, required=True)
    recording = commands.add_parser("record", help="append transcript return point, no game action")
    recording.add_argument("--trace", type=Path, required=True)
    recording.add_argument("--journal", type=Path, default=Path("runtime/data/workspace.jsonl"))
    recording.add_argument("--actor-id", default="james")
    args = parser.parse_args()

    if args.command == "inspect":
        print(json.dumps(summarize_operator_trace(args.trace), indent=2, sort_keys=True))
        return
    store = WorkspaceStore(args.journal)
    if args.command == "open":
        lane = open_arc_lane(store, actor_id=args.actor_id)
    else:
        lane = record_trace(store, summarize_operator_trace(args.trace), actor_id=args.actor_id)
    print(json.dumps({"lane_id": lane.lane_id, "movements": lane.movements,
                      "return_event_id": lane.latest_event_id, "journal": str(args.journal)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
