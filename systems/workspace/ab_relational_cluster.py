"""Bounded A/B-led movement of actual local processes, not a task-splitting benchmark.

The existing finite math supplies A/B successor relations. Separate processes
report possible moves. The host independently recomputes them; previously unseen
states branch and a second independently traced arrival connects histories.

This models cluster *movement* in one finite F3 world. It does not redefine
James's language referent or admit native Process Workstation workers.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import multiprocessing as mp
import os
from pathlib import Path

VERSION = "finite-ab-relational-cluster/v1"
PHI = (0, 1, 2)
ROOT = (0, 0, 0)
MAX_NODES = 27
MAX_DEPTH = 10


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value):
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _sources():
    root = Path(__file__).resolve().parents[2]
    files = {
        "finite_world": root / "work" / "arc_like_maze" / "math.py",
        "movement_adapter": Path(__file__).resolve(),
    }
    if any(not f.is_file() or f.is_symlink() for f in files.values()):
        raise ValueError("finite source file absent or symlinked")
    return {key: sha256(p.read_bytes()).hexdigest() for key, p in files.items()}


def _independent_step(state, action):
    """Independent host witness: does not call the worker's World.step()."""
    x, y, z = state
    if action == "A":
        return ((x + 1) % 3, y, z)
    if action == "B":
        return (x, (y + x + 1) % 3, (z + PHI[y]) % 3)
    raise ValueError("unknown finite action")


def _worker(sender, path, state):
    """The source-owned World runs in an actual separate OS process."""
    try:
        from work.arc_like_maze.math import World
        world = World(3, PHI)
        reply = {
            "path": path,
            "pid": os.getpid(),
            "next": {a: list(world.step(tuple(state), a)) for a in "AB"},
        }
        sender.send_bytes(_canonical(reply).encode("utf-8"))
    finally:
        sender.close()


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate receipt JSON key")
        result[key] = value
    return result


def _initial():
    return {"nodes": {"": ROOT}, "state_owner": {ROOT: ""}, "expanded": set(),
            "connections": 0, "events": 0}


def _pending(state, depth):
    return [p for p in state["nodes"]
            if p not in state["expanded"] and len(p) < depth]


def _replay_entry(state, row, previous, sources):
    required = {"version", "source", "previous_hash", "depth_limit",
                "expanded_paths", "movements", "entry_hash"}
    if not isinstance(row, dict) or set(row) != required or row["version"] != VERSION:
        raise ValueError("malformed mathematical cluster receipt")
    if row["source"] != sources:
        raise ValueError("cluster mathematical source has changed")
    if row["previous_hash"] != previous or row["entry_hash"] != _hash({
            k: value for k, value in row.items() if k != "entry_hash"}):
        raise ValueError("cluster receipt chain or digest changed")
    depth = row["depth_limit"]
    paths = row["expanded_paths"]
    if type(depth) is not int or not 1 <= depth <= MAX_DEPTH:
        raise ValueError("invalid finite exploration depth")
    if (not isinstance(paths, list) or not 1 <= len(paths) <= 4
            or any(not isinstance(p, str) for p in paths)
            or paths != _pending(state, depth)[:len(paths)]):
        raise ValueError("inconsistent mathematical frontier")
    reported = row["movements"]
    if not isinstance(reported, list) or len(reported) != 2 * len(paths):
        raise ValueError("missing or extra mathematical worker movement")
    pids = []
    index = 0
    for path in paths:
        state_at_path = state["nodes"][path]
        for action in "AB":
            item = reported[index]
            index += 1
            destination = _independent_step(state_at_path, action)
            prior = state["state_owner"].get(destination)
            kind = "CONNECTION" if prior is not None else (
                "BRANCH" if len(state["nodes"]) < MAX_NODES else "OPEN_CAPACITY_WALL")
            if not isinstance(item, dict) or set(item) != {
                "from", "action", "word", "to", "kind", "existing_word", "pid"
            }:
                raise ValueError("invalid worker movement envelope")
            expected = {"from": path, "action": action, "word": path + action,
                        "to": list(destination), "kind": kind,
                        "existing_word": prior if kind == "CONNECTION" else None}
            if any(item.get(k) != v for k, v in expected.items()):
                raise ValueError("worker movement disagrees with independent A/B replay")
            if type(item["pid"]) is not int or item["pid"] <= 0:
                raise ValueError("invalid process identity")
            pids.append(item["pid"])
            if kind == "BRANCH":
                state["nodes"][path + action] = destination
                state["state_owner"][destination] = path + action
            elif kind == "CONNECTION":
                # This is a mathematical confluence, not cross-domain proof.
                state["connections"] += 1
        state["expanded"].add(path)
    # Each expanded path was computed by a separate process this pass.
    if len(set(pids[::2])) != len(paths) or any(pids[i] != pids[i + 1]
                                                 for i in range(0, len(pids), 2)):
        raise ValueError("invalid independent worker identities")
    state["events"] += 1
    return row["entry_hash"]


def read_history(path):
    """Independently re-evaluate the complete append-only mathematical trail."""
    state = _initial()
    if not path.exists():
        return state, "GENESIS"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 500000:
        raise ValueError("unsafe or oversized mathematical journal")
    sources = _sources()
    previous = "GENESIS"
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line, object_pairs_hook=_strict_object)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid mathematical cluster JSON") from exc
        previous = _replay_entry(state, row, previous, sources)
    return state, previous


def _compute_many(selected, nodes, timeout):
    context = mp.get_context("spawn")
    children = []
    try:
        for path in selected:
            receiver, sender = context.Pipe(duplex=False)
            process = context.Process(target=_worker, args=(sender, path, nodes[path]))
            process.start()
            sender.close()
            children.append((process, receiver, path))
        results = []
        for process, receiver, path in children:
            if not receiver.poll(timeout):
                raise TimeoutError("math worker movement timed out")
            raw = receiver.recv_bytes(4096)
            try:
                result = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
            except (ValueError, UnicodeError) as exc:
                raise ValueError("invalid mathematical worker report") from exc
            process.join(timeout)
            if process.exitcode != 0 or result.get("path") != path or result.get("pid") != process.pid:
                raise ValueError("worker process or source path mismatch")
            if (not isinstance(result.get("next"), dict)
                    or set(result["next"]) != {"A", "B"}
                    or any(result["next"][a] != list(_independent_step(nodes[path], a))
                           for a in "AB")):
                raise ValueError("worker failed independent finite A/B check")
            results.append(result)
        return results
    finally:
        for process, receiver, _ in children:
            receiver.close()
            if process.is_alive():
                process.terminate()
                process.join(2)


def advance(data_dir, *, workers=3, depth=MAX_DEPTH, execute=False, timeout=15):
    """One explicitly invoked wave. New work follows admitted mathematical edges."""
    if not execute:
        raise PermissionError("explicit execution authorization required")
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError("worker budget must be 1..4")
    if type(depth) is not int or not 1 <= depth <= MAX_DEPTH:
        raise ValueError("depth budget must be 1..10")
    if type(timeout) is not int or not 1 <= timeout <= 120:
        raise ValueError("invalid timeout")
    path = Path(data_dir) / "ab_relational_cluster.jsonl"
    state, previous = read_history(path)
    selected = _pending(state, depth)[:workers]
    if not selected:
        return {"status": "QUIET", "workers_started": 0, "branches": 0,
                "connections": 0, "pending": 0, "known_states": len(state["nodes"])}
    sources = _sources()
    result = _compute_many(selected, state["nodes"], timeout)
    if _sources() != sources:
        raise ValueError("source changed during mathematical work")
    # Replay the same admission rules against each returned transition.
    known = dict(state["state_owner"])
    movements = []
    for item in result:
        parent = item["path"]
        for action in "AB":
            dest = tuple(item["next"][action])
            prior = known.get(dest)
            kind = "CONNECTION" if prior is not None else (
                "BRANCH" if len(known) < MAX_NODES else "OPEN_CAPACITY_WALL")
            movements.append({"from": parent, "action": action, "word": parent + action,
                              "to": list(dest), "kind": kind,
                              "existing_word": prior if kind == "CONNECTION" else None,
                              "pid": item["pid"]})
            if kind == "BRANCH":
                known[dest] = parent + action
    row = {"version": VERSION, "source": sources, "previous_hash": previous,
           "depth_limit": depth, "expanded_paths": selected, "movements": movements}
    row["entry_hash"] = _hash(row)
    # Verify the exact journal addition before writing; never invent a connection.
    verified_state, _ = read_history(path)
    _replay_entry(verified_state, row, previous, sources)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("unsafe mathematical journal")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(_canonical(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return {"status": "MOVED", "workers_started": len(selected),
            "branches": sum(m["kind"] == "BRANCH" for m in movements),
            "connections": sum(m["kind"] == "CONNECTION" for m in movements),
            "pending": len(_pending(verified_state, depth)),
            "known_states": len(verified_state["nodes"]),
            "paths": selected, "process_ids": [item["pid"] for item in result],
            "entry_hash": row["entry_hash"]}


def main():
    parser = argparse.ArgumentParser(description="Witness-gated finite A/B relational movement")
    parser.add_argument("--data-dir", default="runtime/data")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--depth", type=int, default=MAX_DEPTH)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    path = Path(args.data_dir) / "ab_relational_cluster.jsonl"
    if args.inspect:
        state, head = read_history(path)
        print(_canonical({"known_states": len(state["nodes"]),
                          "connections": state["connections"],
                          "pending": len(_pending(state, args.depth)),
                          "journal_entries": state["events"], "head": head}))
    else:
        print(_canonical(advance(args.data_dir, workers=args.workers, depth=args.depth,
                                 execute=args.execute)))


if __name__ == "__main__":
    main()
