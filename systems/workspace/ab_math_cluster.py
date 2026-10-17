"""Explicit local multi-process computation of the existing finite A/B worlds.

This is one bounded mathematical source experiment, not a definition of the
language referent, a native Workstation job, or an autonomous scheduler.
Worker reports are never accepted without an independently recomputed full graph.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import multiprocessing as mp
import os
from pathlib import Path
from itertools import product
from typing import Any

VERSION = "ab-f3-local-cluster/v1"
DEFAULT_PHIS = tuple((0, a, b) for a, b in product(range(3), repeat=2))
ROOT = (0, 0, 0)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_json(value).encode("utf-8")).hexdigest()


def _phis(values: Any) -> tuple[tuple[int, int, int], ...]:
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 9:
        raise ValueError("requires 1..9 finite candidate worlds")
    result = []
    for value in values:
        if (not isinstance(value, (list, tuple)) or len(value) != 3
                or any(type(v) is not int or v not in (0, 1, 2) for v in value)
                or value[0] != 0):
            raise ValueError("candidate phi must be an F3 triple with phi(0)=0")
        result.append(tuple(value))
    if len(set(result)) != len(result):
        raise ValueError("duplicate finite candidate worlds")
    return tuple(sorted(result))


def _source() -> dict[str, str]:
    root = Path(__file__).resolve().parents[2]
    paths = {"worker_math": root / "work/arc_like_maze/math.py",
             "cluster_driver": Path(__file__).resolve()}
    result = {}
    for key, path in paths.items():
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing or linked finite math source")
        result[key] = sha256(path.read_bytes()).hexdigest()
    return result


def _worker_graph(phi: tuple[int, int, int]) -> dict:
    from work.arc_like_maze.math import World
    world = World(3, phi)
    states = sorted(world.reachable())
    edges = [[list(state), action, list(world.step(state, action))]
             for state in states for action in "AB"]
    return {"phi": list(phi), "states": [list(state) for state in states], "edges": edges}


def _child(pipe, phis: tuple[tuple[int, int, int], ...]) -> None:
    try:
        raw = _json([_worker_graph(phi) for phi in phis]).encode("utf-8")
        if len(raw) > 120000:
            raise ValueError("oversized worker output")
        pipe.send_bytes(raw)
    finally:
        pipe.close()


def _reference_step(phi: tuple[int, int, int], state: tuple[int, int, int], action: str) -> tuple[int, int, int]:
    x, y, z = state
    if action == "A":
        return ((x + 1) % 3, y, z)
    if action == "B":
        return (x, (y + x + 1) % 3, (z + phi[y]) % 3)
    raise ValueError("unknown finite action")


def _reference_graph(phi: tuple[int, int, int]) -> dict:
    # Independent finite enumeration: no import from the worker's World class.
    visited = {ROOT}
    while True:
        expanded = visited | {_reference_step(phi, state, action)
                              for state in visited for action in "AB"}
        if expanded == visited:
            break
        visited = expanded
    states = sorted(visited)
    return {"phi": list(phi), "states": [list(state) for state in states],
            "edges": [[list(state), action, list(_reference_step(phi, state, action))]
                      for state in states for action in "AB"]}


def _verify_graphs(phis: tuple[tuple[int, int, int], ...], reports: Any) -> list[dict]:
    if not isinstance(reports, list) or len(reports) != len(phis):
        raise ValueError("missing or extra worker worlds")
    by_phi = {}
    for row in reports:
        if not isinstance(row, dict) or set(row) != {"phi", "states", "edges"}:
            raise ValueError("invalid worker graph envelope")
        phi = tuple(row["phi"]) if isinstance(row["phi"], list) else ()
        if (len(phi) != 3 or any(type(x) is not int for x in phi)
                or phi in by_phi or phi not in phis):
            raise ValueError("duplicate or unknown worker world")
        if row != _reference_graph(phi):
            raise ValueError("worker graph differs from independent F3 replay")
        by_phi[phi] = row
    if set(by_phi) != set(phis):
        raise ValueError("missing worker world")
    return [by_phi[p] for p in phis]


def _aligned(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
    # Complete reachable rooted labeled-graph bijection, not similarity or
    # projection. Discover the forced mapping by following both A and B.
    forward, backward = {ROOT: ROOT}, {ROOT: ROOT}
    pending = [ROOT]
    while pending:
        x = pending.pop()
        y = forward[x]
        for action in "AB":
            nx = _reference_step(a, x, action)
            ny = _reference_step(b, y, action)
            if nx in forward and forward[nx] != ny:
                return False
            if ny in backward and backward[ny] != nx:
                return False
            if nx not in forward:
                forward[nx] = ny
                backward[ny] = nx
                pending.append(nx)
    return len(forward) == len(_reference_graph(a)["states"]) == len(_reference_graph(b)["states"])


def _classes(phis: tuple[tuple[int, int, int], ...]) -> list[list[list[int]]]:
    remaining = list(phis)
    classes = []
    while remaining:
        anchor = remaining[0]
        members = [p for p in remaining if _aligned(anchor, p)]
        if any(not _aligned(a, b) for a in members for b in members):
            raise ValueError("inconsistent mathematical alignment")
        classes.append([list(x) for x in members])
        remaining = [p for p in remaining if p not in members]
    return classes


def _verify_receipt(row: Any, previous: str) -> None:
    fields = {"version", "source", "phis", "graphs", "classes", "process_ids",
              "run_key", "previous_hash", "receipt_hash"}
    if not isinstance(row, dict) or set(row) != fields or row["version"] != VERSION:
        raise ValueError("invalid cluster receipt fields")
    if row["previous_hash"] != previous or row["receipt_hash"] != _digest({k: v for k, v in row.items() if k != "receipt_hash"}):
        raise ValueError("broken cluster receipt hash chain")
    phis = _phis(row["phis"])
    if row["phis"] != [list(p) for p in phis]:
        raise ValueError("unsorted finite worlds")
    if (not isinstance(row["source"], dict)
            or set(row["source"]) != {"worker_math", "cluster_driver"}
            or any(not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v)
                   for v in row["source"].values())):
        raise ValueError("malformed source identity")
    if row["run_key"] != _digest([VERSION, row["source"], row["phis"]]):
        raise ValueError("changed run identity")
    _verify_graphs(phis, row["graphs"])
    if row["classes"] != _classes(phis):
        raise ValueError("unverified class correspondence")
    pids = row["process_ids"]
    if not isinstance(pids, list) or not pids or any(type(p) is not int or p <= 0 for p in pids) or len(set(pids)) != len(pids):
        raise ValueError("invalid local worker process references")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def read_receipts(path: Path) -> list[dict]:
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise ValueError("invalid receipt journal path")
    if path.stat().st_size > 2_000_000:
        raise ValueError("oversized cluster receipt journal")
    rows = []
    previous = "GENESIS"
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line, object_pairs_hook=_unique_object)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid cluster receipt JSON") from exc
        _verify_receipt(row, previous)
        if any(p["run_key"] == row["run_key"] for p in rows):
            raise ValueError("duplicate cluster run in receipt journal")
        rows.append(row)
        previous = row["receipt_hash"]
    return rows


def run_cluster(*, data_dir: Path, phis: Any = DEFAULT_PHIS,
                workers: int = 2, execute: bool = False, timeout: int = 15) -> dict:
    if not execute:
        raise PermissionError("explicit --execute required before starting processes")
    if type(workers) is not int or not 1 <= workers <= 4 or type(timeout) is not int or not 1 <= timeout <= 120:
        raise ValueError("workers must be 1..4 and timeout 1..120 seconds")
    selected = _phis(phis)
    source = _source()
    path = Path(data_dir) / "ab_math_cluster.jsonl"
    history = read_receipts(path)
    run_key = _digest([VERSION, source, [list(p) for p in selected]])
    for existing in history:
        if existing["run_key"] == run_key:
            return {"reused": True, "receipt": existing, "workers_started": 0}

    buckets = tuple(tuple(selected[i::min(workers, len(selected))])
                    for i in range(min(workers, len(selected))))
    ctx = mp.get_context("spawn")
    processes = []
    collected = []
    try:
        for bucket in buckets:
            incoming, outgoing = ctx.Pipe(duplex=False)
            process = ctx.Process(target=_child, args=(outgoing, bucket), daemon=False)
            process.start()
            outgoing.close()
            processes.append((process, incoming, bucket))
        for process, incoming, bucket in processes:
            if not incoming.poll(timeout):
                raise RuntimeError("finite cluster worker timed out")
            raw = incoming.recv_bytes(120000)
            try:
                result = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
            except (UnicodeError, ValueError) as exc:
                raise ValueError("invalid worker result encoding") from exc
            _verify_graphs(bucket, result)
            collected.extend(result)
            process.join(timeout)
            if process.exitcode != 0:
                raise RuntimeError("finite cluster child exited unexpectedly")
    finally:
        for process, incoming, _ in processes:
            incoming.close()
            if process.is_alive():
                process.terminate()
                process.join(2)
    if _source() != source:
        raise ValueError("finite source changed during cluster computation")
    graphs = _verify_graphs(selected, collected)
    previous = history[-1]["receipt_hash"] if history else "GENESIS"
    receipt = {"version": VERSION, "source": source, "phis": [list(p) for p in selected],
               "graphs": graphs, "classes": _classes(selected),
               "process_ids": [process.pid for process, _, _ in processes],
               "run_key": run_key, "previous_hash": previous}
    receipt["receipt_hash"] = _digest(receipt)
    _verify_receipt(receipt, previous)
    # One local writer only: another host/process must not write this path concurrently.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_json(receipt) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return {"reused": False, "receipt": receipt, "workers_started": len(processes)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Finite A/B local process cluster (explicit invocation)")
    parser.add_argument("--data-dir", default="runtime/data")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    path = Path(args.data_dir) / "ab_math_cluster.jsonl"
    if args.inspect:
        print(_json({"receipts": len(read_receipts(path))}))
        return
    result = run_cluster(data_dir=Path(args.data_dir), workers=args.workers, execute=args.execute)
    receipt = result["receipt"]
    print(_json({"reused": result["reused"], "workers_started": result["workers_started"],
                 "worlds_verified": len(receipt["graphs"]),
                 "equivalence_classes": receipt["classes"],
                 "receipt_hash": receipt["receipt_hash"],
                 "native_workstation_jobs_admitted": False}))


if __name__ == "__main__":
    main()
