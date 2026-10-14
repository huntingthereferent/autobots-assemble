"""Finite admission contract for CP30's historical *synthetic fixture* audit.

Host does not import the selected edition; verification replays from separately
manifest-checked historical bytes. This is same-algorithm reference replay,
NOT an independent mathematical proof or external owner authentication.
"""
from __future__ import annotations

import re
from typing import Any

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
_MODES = {"intact", "revoke-selected", "revoke-neighbor", "untrusted-key"}


def validate_route_request(value: Any) -> dict:
    if type(value) is not dict or set(value) != {"route", "tasks", "scenario"}:
        raise ValueError("expected route, tasks, scenario only")
    if value["route"] not in ("left", "right") or value["scenario"] not in _MODES:
        raise ValueError("unknown route or synthetic control")
    entries = value["tasks"]
    if type(entries) is not list or not 1 <= len(entries) <= 8:
        raise ValueError("task list must contain 1..8 exact obligations")
    names = set()
    rows = []
    for t in entries:
        if type(t) is not dict or set(t) != {"name", "state", "action"}:
            raise ValueError("malformed task obligation")
        name, state, action = t["name"], t["state"], t["action"]
        if type(name) is not str or not _ID.fullmatch(name) or name in names:
            raise ValueError("task names must be distinct safe identifiers")
        names.add(name)
        if type(state) is not list or len(state) != 3 or any(type(x) is not int or x not in (0,1,2) for x in state):
            raise ValueError("state must be an F3 triple")
        if action not in ("A", "B"):
            raise ValueError("task action must be A or B")
        rows.append({"name": name, "state": list(state), "action": action})
    return {"route": value["route"], "scenario": value["scenario"], "tasks": rows}


def verify_report_shape(report: Any, inputs: dict) -> None:
    if type(report) is not dict or set(report) != {
        "issued_status", "receive_status", "task_statuses", "usable", "replay_calls",
        "replay_trace", "source_observations_unchanged", "proof_for_all",
        "distinct_signer_verifier", "synthetic_fixture",
    }:
        raise ValueError("CP30 route audit report shape invalid")
    if (type(report["issued_status"]) is not str or type(report["receive_status"]) is not str or
            type(report["replay_calls"]) is not int or not 0 <= report["replay_calls"] <= 2 or
            type(report["replay_trace"]) is not dict or set(report["replay_trace"]) != {"left", "right"} or
            any(type(n) is not int or n < 0 or n > 2 for n in report["replay_trace"].values()) or
            type(report["source_observations_unchanged"]) is not bool or
            type(report["proof_for_all"]) is not bool or
            type(report["distinct_signer_verifier"]) is not bool or
            report["synthetic_fixture"] is not True):
        raise ValueError("CP30 route audit report has invalid values")
    names = [t["name"] for t in inputs["tasks"]]
    if (type(report["task_statuses"]) is not list or
            any(type(x) is not list or len(x) != 2 or
                type(x[0]) is not str or type(x[1]) is not str for x in report["task_statuses"]) or
            type(report["usable"]) is not list or any(type(x) is not str for x in report["usable"])):
        raise ValueError("CP30 route audit task report invalid")
    if report["task_statuses"] and [a[0] for a in report["task_statuses"]] != names:
        raise ValueError("CP30 task report mismatches declared names")
    if not set(report["usable"]).issubset(names) or len(report["usable"]) != len(set(report["usable"])):
        raise ValueError("CP30 usable tasks must be distinct declared tasks")
