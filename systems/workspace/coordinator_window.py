"""Read-only, one-window projection over the EXISTING Process Workstation.

This module does not admit work, execute jobs, replace source-native verifiers,
create a scheduler, or turn another ChatGPT conversation into a live agent.
The native source of live worker status is workstation_snapshot(runtime=...).
Archive links are integrity-checked observations, never live job proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import argparse
import json
import os
import re

_SAFE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}$")
_KINDS = {"runtime-job", "artifact", "planned"}
_LANES = {"correspondence", "game", "nih"}


def _id(value: str) -> str:
    if not isinstance(value, str) or not _SAFE.fullmatch(value) or value in {".", ".."}:
        raise ValueError("unsafe or empty identifier")
    return value


def _canonical(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


class CoordinatorIndex:
    """Append-only INDEX over independently owned work; no task ownership."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.events: list[dict] = []
        previous = "0" * 64
        if self.path.is_file():
            for line_number, line in enumerate(self.path.read_text(encoding="utf8").splitlines(), 1):
                if not line.strip():
                    raise ValueError("empty line in coordinator index")
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid coordinator record at line {line_number}") from exc
                if not isinstance(row, dict) or set(row) != {"seq", "prev_sha256", "event", "sha256"}:
                    raise ValueError("coordinator record shape changed")
                digest = sha256(_canonical({k: row[k] for k in ("seq", "prev_sha256", "event")})).hexdigest()
                if row["seq"] != line_number or row["prev_sha256"] != previous or digest != row["sha256"]:
                    raise ValueError(f"coordinator history mismatch at line {line_number}")
                self.events.append(row)
                previous = digest
        self._validate_history()

    def _validate_history(self) -> None:
        windows: dict[str, set[str]] = {}
        entries: dict[tuple[str, str, str], str] = {}
        bound: set[tuple[str, str, str]] = set()
        for row in self.events:
            ev = row["event"]
            if not isinstance(ev, dict):
                raise ValueError("invalid coordinator event")
            kind = ev.get("kind")
            if kind == "WINDOW":
                name = _id(ev.get("window"))
                if name in windows:
                    raise ValueError("duplicate coordinator window")
                lanes = ev.get("lanes")
                if not isinstance(lanes, list) or len(lanes) != len(set(lanes)) or not set(lanes).issubset(_LANES):
                    raise ValueError("invalid window lanes")
                windows[name] = set(lanes)
            elif kind == "LINK":
                window, lane, slot = _id(ev.get("window")), _id(ev.get("lane")), _id(ev.get("slot"))
                if window not in windows or lane not in windows[window] or (window, lane, slot) in entries:
                    raise ValueError("invalid or repeated worker-lane link")
                if ev.get("source_kind") not in _KINDS:
                    raise ValueError("invalid lane source kind")
                if ev["source_kind"] == "runtime-job":
                    _id(ev.get("job_id")); _id(ev.get("worker_id")); _id(ev.get("version_id"))
                elif ev["source_kind"] == "artifact":
                    if not isinstance(ev.get("source_locator"), str) or not ev["source_locator"]:
                        raise ValueError("artifact requires source locator")
                    if not re.fullmatch("[0-9a-f]{64}", ev.get("artifact_sha256", "")):
                        raise ValueError("artifact requires SHA-256")
                entries[(window, lane, slot)] = ev["source_kind"]
            elif kind == "BIND":
                window, lane, slot = _id(ev.get("window")), _id(ev.get("lane")), _id(ev.get("slot"))
                key = (window, lane, slot)
                if entries.get(key) != "planned" or key in bound:
                    raise ValueError("binding requires an existing unbound planned slot")
                _id(ev.get("job_id")); _id(ev.get("worker_id")); _id(ev.get("version_id"))
                bound.add(key)
            else:
                raise ValueError("unknown coordinator event type")

    def _append(self, event: dict) -> None:
        previous = self.events[-1]["sha256"] if self.events else "0" * 64
        row = {"seq": len(self.events) + 1, "prev_sha256": previous, "event": event}
        row["sha256"] = sha256(_canonical(row)).hexdigest()
        # Refuse a broken/unavailable source before appending; never repair history.
        candidate = CoordinatorIndex.__new__(CoordinatorIndex)
        candidate.events = [*self.events, row]
        candidate._validate_history()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.events.append(row)

    def create_window(self, name: str, *, lanes: tuple[str, ...] = ("game", "correspondence", "nih")) -> None:
        self._append({"kind": "WINDOW", "window": _id(name), "lanes": list(lanes)})

    def link_runtime(self, window: str, lane: str, *, job_id: str, worker_id: str, version_id: str, slot: str | None = None) -> None:
        self._append({"kind": "LINK", "window": _id(window), "lane": _id(lane),
                      "slot": _id(slot or lane), "source_kind": "runtime-job", "job_id": _id(job_id),
                      "worker_id": _id(worker_id), "version_id": _id(version_id)})

    def bind_planned(self, window: str, lane: str, *, slot: str, job_id: str,
                     worker_id: str, version_id: str) -> None:
        """Assign one actual native job to a planned CP without overwriting its intake event."""
        self._append({"kind": "BIND", "window": _id(window), "lane": _id(lane),
                      "slot": _id(slot), "job_id": _id(job_id),
                      "worker_id": _id(worker_id), "version_id": _id(version_id)})

    def link_artifact(self, window: str, lane: str, *, locator: str, sha256_hex: str,
                      historical_note: str, slot: str | None = None) -> None:
        if not isinstance(historical_note, str):
            raise ValueError("note must be text")
        self._append({"kind": "LINK", "window": _id(window), "lane": _id(lane),
                      "slot": _id(slot or lane), "source_kind": "artifact", "source_locator": locator,
                      "artifact_sha256": sha256_hex, "historical_note": historical_note})

    def link_planned(self, window: str, lane: str, *, next_movement: str, slot: str | None = None) -> None:
        if not isinstance(next_movement, str) or not next_movement:
            raise ValueError("next movement required")
        self._append({"kind": "LINK", "window": _id(window), "lane": _id(lane),
                      "slot": _id(slot or lane), "source_kind": "planned", "next_movement": next_movement})

    def definition(self, name: str) -> tuple[list[str], dict[str, list[dict]]]:
        name = _id(name)
        lanes = None
        links = {}
        for row in self.events:
            ev = row["event"]
            if ev["window"] != name:
                continue
            if ev["kind"] == "WINDOW":
                lanes = ev["lanes"]
            elif ev["kind"] == "LINK":
                links.setdefault(ev["lane"], []).append(dict(ev))
            elif ev["kind"] == "BIND":
                planned = next(x for x in links[ev["lane"]] if x["slot"] == ev["slot"])
                planned["original_planned_movement"] = planned.pop("next_movement")
                planned.update({"source_kind": "runtime-job",
                                "job_id": ev["job_id"], "worker_id": ev["worker_id"],
                                "version_id": ev["version_id"]})
        if lanes is None:
            raise KeyError("unknown coordinator window")
        return lanes, links


def one_window_status(index: CoordinatorIndex, window: str, workstation_view: dict,
                      *, artifact_dir: str | Path | None = None) -> dict:
    """Render native current state without silently upgrading archived evidence."""
    lanes, links = index.definition(window)
    jobs = {row["job_id"]: row for row in workstation_view.get("jobs", ())}
    children = []
    for lane in lanes:
        entries = links.get(lane, [])
        if not entries:
            children.append({"lane": lane, "slot": "none", "kind": "planned", "status": "NOT_ADMITTED",
                             "verification": "none", "next_movement": None})
            continue
        for entry in entries:
            slot = entry["slot"]
            if entry["source_kind"] == "planned":
                children.append({"lane": lane, "slot": slot, "kind": "planned", "status": "NOT_ADMITTED",
                                 "verification": "none", "next_movement": entry.get("next_movement")})
                continue
            if entry["source_kind"] == "runtime-job":
                job = jobs.get(entry["job_id"])
                if job is None:
                    children.append({"lane": lane, "slot": slot, "kind": "runtime-job", "job_id": entry["job_id"],
                                     "status": "UNAVAILABLE", "verification": "not-observed",
                                     "source_state": "UNKNOWN"})
                elif job.get("worker_id") != entry["worker_id"] or job.get("version_id") != entry["version_id"]:
                    children.append({"lane": lane, "slot": slot, "kind": "runtime-job", "job_id": entry["job_id"],
                                     "status": "IDENTITY_MISMATCH", "verification": "invalid",
                                     "source_state": job.get("source_state")})
                else:
                    children.append({"lane": lane, "slot": slot, "kind": "runtime-job", "job_id": entry["job_id"],
                                     "worker_id": job["worker_id"], "version_id": job["version_id"],
                                     "status": job["status"], "source_state": job.get("source_state"),
                                     "verification": job.get("verification", "not-reverified"),
                                     "native_verifier": job.get("native_verifier"),
                                     "missing_witnesses": job.get("missing_witnesses", []),
                                     "blocked_by": job.get("blocked_by", []),
                                     "last_event_at": job.get("last_event_at"),
                                     "last_events": job.get("events", [])[-3:]})
                continue
            locator = entry["source_locator"]
            checksum = "UNAVAILABLE"
            if artifact_dir is not None:
                base = Path(artifact_dir).resolve()
                p = (base / locator).resolve()
                # A coordinator must not read outside its explicitly supplied artifact root.
                if p.is_relative_to(base) and p.is_file() and not p.is_symlink():
                    checksum = "MATCH" if sha256(p.read_bytes()).hexdigest() == entry["artifact_sha256"] else "MISMATCH"
            children.append({"lane": lane, "slot": slot, "kind": "artifact", "status": "HISTORICAL_ONLY",
                             "verification": "integrity-only" if checksum == "MATCH" else "not-integrity-verified",
                             "artifact_integrity": checksum, "source_locator": locator,
                             "historical_note": entry["historical_note"]})
    # A lane requires at least one admitted native worker to claim native completion.
    # Every admitted job must have freshly reverified evidence; historical artifacts
    # never count as proof but also don't penalize an otherwise verified lane.
    unresolved = []
    for lane in lanes:
        active = [r for r in children if r["lane"] == lane and r["kind"] == "runtime-job"]
        planned = [r for r in children if r["lane"] == lane and r["kind"] == "planned"]
        if not active or planned or not all(
            r["status"] == "COMPLETE" and r.get("source_state") == "MATCHES_ADMISSION"
            and not r.get("missing_witnesses") and r.get("verification") == "natively-reverified"
            for r in active
        ):
            unresolved.append(lane)
    return {"schema_version": 1, "coordinator_window": window, "read_only": True,
            "triggered_execution": False, "complete": not unresolved,
            "unresolved_lanes": unresolved, "workers": children,
            "status_semantics": "HISTORICAL_ONLY and COMPLETE/recorded-not-reverified are never current proof"}


def markdown_handoff(status: dict) -> str:
    rows = [f"# COORDINATOR — {status['coordinator_window']}", "",
            "Single-window return packet. Source workers remain native; no worker was started.", "",
            "| Lane | Worker | Status | Evidence depth |", "|---|---|---|---|"]
    for w in status["workers"]:
        rows.append(f"| {w['lane']} | {w['slot']} | {w['status']} | {w['verification']} |")
    rows.extend(["", "## Current movement", "",
                 "All lanes complete with native re-verification." if status["complete"]
                 else "Unresolved lanes: " + ", ".join(status["unresolved_lanes"]), "",
                 "## Native boundaries", "",
                 "- An artifact hash validates file identity only, never a worker run.",
                 "- Runtime COMPLETE is a recorded computation, not universal task proof.",
                 "- A changed worker edition or missing witness blocks promotion.",
                 "- Other ChatGPT windows have no live status unless they publish shared evidence.",
                 "- Submit/execute jobs using the existing workstation controls; this coordinator is read-only.", ""])
    return "\n".join(rows)


def freshly_reverify_linked_jobs(index: CoordinatorIndex, window: str,
                                 workstation_view: dict, checker) -> dict:
    """Opt-in; delegates validation to EXISTING controls.reverify_job.

    Only marked fresh when the exact linked job/source currently match and its
    native reverify callback actually returns a positive result. Never executes.
    """
    _, links = index.definition(window)
    copied = {**workstation_view, "jobs": [dict(j) for j in workstation_view.get("jobs", ())]}
    by_id = {job.get("job_id"): job for job in copied["jobs"]}
    for rows in links.values():
        for link in rows:
            if link["source_kind"] != "runtime-job":
                continue
            job = by_id.get(link["job_id"])
            if job is None or job.get("status") != "COMPLETE" or job.get("source_state") != "MATCHES_ADMISSION":
                continue
            if (job.get("worker_id"), job.get("version_id")) != (link["worker_id"], link["version_id"]):
                continue
            try:
                result = checker(link["job_id"])
                if (not isinstance(result, dict) or result.get("job_id") != link["job_id"]
                        or result.get("status") != "COMPLETE" or result.get("reverified") is not True
                        or result.get("executed") is not False):
                    raise ValueError("native reverify result did not confirm read-only COMPLETE")
            except (Exception) as exc:
                # A failed reverify never upgrades status; preserve the recorded state.
                job["verification"] = "reverification-failed"
                job["reverification_error"] = type(exc).__name__
            else:
                job["verification"] = "natively-reverified"
    return copied


def run_exact_linked_job(index: CoordinatorIndex, window: str, lane: str, slot: str,
                         confirm_execute: str, workstation_view: dict, dispatcher) -> dict:
    """Route ONE exact already-admitted job to the EXISTING controls.run_job.

    No new worker runtime, auto-admission, background scheduling or all-job launch.
    Caller must explicitly confirm exact native job ID. The source-native bridge
    inside the existing controls module remains the only execution authority.
    """
    _, links = index.definition(window)
    matching = [l for l in links.get(_id(lane), ()) if l["slot"] == _id(slot)]
    if len(matching) != 1 or matching[0]["source_kind"] != "runtime-job":
        raise ValueError("slot is not a linked native workstation job")
    binding = matching[0]
    if confirm_execute != binding["job_id"]:
        raise PermissionError("confirm-execute must match exact native job ID")
    matches = [j for j in workstation_view.get("jobs", ()) if j.get("job_id") == binding["job_id"]]
    if len(matches) != 1:
        raise ValueError("native workstation job not currently observed")
    job = matches[0]
    if (job.get("worker_id"),job.get("version_id")) != (binding["worker_id"],binding["version_id"]):
        raise ValueError("worker/edition changed from coordinator binding")
    if job.get("source_state") != "MATCHES_ADMISSION":
        raise ValueError("worker source does not match admission")
    if job.get("status") not in {"READY", "COMPLETE"}:
        raise ValueError("job not ready or completed for safe native dispatch")
    return dispatcher(binding["job_id"], confirm_execute)


def from_existing_workstation(data_dir: str | Path) -> dict:
    """Read the real workstation snapshot; no second runtime or execution path."""
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from systems.workspace.monitor import workstation_snapshot
    root = Path(data_dir)
    # Reopening journal replays source-owned job records, not computations.
    runtime = HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl"))
    return workstation_snapshot(root=root / "workstation", runtime=runtime,
                                workspace_journal=root / "workspace.jsonl")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One-window status over existing workstation")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--window", default="complete-stack")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--lanes", nargs="+", choices=sorted(_LANES), default=["game", "correspondence", "nih"])
    p = sub.add_parser("link-job")
    p.add_argument("--lane", required=True, choices=sorted(_LANES))
    p.add_argument("--slot")
    p.add_argument("--job-id", required=True)
    p.add_argument("--worker-id", required=True)
    p.add_argument("--version", required=True)
    p = sub.add_parser("bind-job")
    p.add_argument("--lane", required=True, choices=sorted(_LANES))
    p.add_argument("--slot", required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--worker-id", required=True)
    p.add_argument("--version", required=True)
    p = sub.add_parser("link-artifact")
    p.add_argument("--lane", required=True, choices=sorted(_LANES))
    p.add_argument("--slot")
    p.add_argument("--file", required=True)
    p.add_argument("--note", required=True)
    p = sub.add_parser("link-planned")
    p.add_argument("--lane", required=True, choices=sorted(_LANES))
    p.add_argument("--slot")
    p.add_argument("--next", required=True)
    p = sub.add_parser("run-linked")
    p.add_argument("--lane", required=True, choices=sorted(_LANES))
    p.add_argument("--slot", required=True)
    p.add_argument("--confirm-execute", required=True, help="exact native job ID; no wildcard")
    p = sub.add_parser("status")
    p.add_argument("--artifact-dir")
    p.add_argument("--markdown", action="store_true")
    p.add_argument("--reverify", action="store_true", help="Opt in to existing source-native read-only reverify")
    args = ap.parse_args(argv)
    directory = Path(args.data_dir)
    index = CoordinatorIndex(directory / "coordinator-windows.jsonl")
    if args.cmd == "init":
        index.create_window(args.window, lanes=tuple(args.lanes))
    elif args.cmd == "link-job":
        # Link to an actual EXISTING native job; cannot invent an admission.
        view = from_existing_workstation(directory)
        job = next((r for r in view["jobs"] if r["job_id"] == args.job_id), None)
        if job is None or (job["worker_id"], job["version_id"]) != (args.worker_id, args.version):
            raise ValueError("job not found in existing Process Workstation with exact worker edition")
        index.link_runtime(args.window, args.lane, job_id=args.job_id,
                           worker_id=args.worker_id, version_id=args.version, slot=args.slot)
    elif args.cmd == "bind-job":
        view = from_existing_workstation(directory)
        job = next((r for r in view["jobs"] if r["job_id"] == args.job_id), None)
        if job is None or (job["worker_id"], job["version_id"]) != (args.worker_id, args.version):
            raise ValueError("job not found in existing Process Workstation with exact worker edition")
        index.bind_planned(args.window, args.lane, slot=args.slot, job_id=args.job_id,
                           worker_id=args.worker_id, version_id=args.version)
    elif args.cmd == "link-artifact":
        path = Path(args.file)
        if not path.is_file():
            raise ValueError("artifact is missing")
        index.link_artifact(args.window, args.lane, locator=path.name,
                            sha256_hex=sha256(path.read_bytes()).hexdigest(),
                            historical_note=args.note, slot=args.slot)
    elif args.cmd == "link-planned":
        index.link_planned(args.window, args.lane, next_movement=args.next, slot=args.slot)
    elif args.cmd == "run-linked":
        from systems.workspace.controls import run_job
        result = run_exact_linked_job(index, args.window, args.lane, args.slot,
                                     args.confirm_execute, from_existing_workstation(directory),
                 lambda job_id, confirmation: run_job(data_dir=directory, job_id=job_id,
                                                      confirm_execute=confirmation))
        print(json.dumps(result, indent=2))
        return 0
    else:
        current = from_existing_workstation(directory)
        if args.reverify:
            from systems.workspace.controls import reverify_job
            current = freshly_reverify_linked_jobs(index, args.window, current,
                       lambda job_id: reverify_job(data_dir=directory, job_id=job_id))
        output = one_window_status(index, args.window, current,
                                   artifact_dir=args.artifact_dir)
        print(markdown_handoff(output) if args.markdown else json.dumps(output, indent=2))
        return 0
    print(f"Index updated: {args.window} ({args.cmd}) — no worker executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())