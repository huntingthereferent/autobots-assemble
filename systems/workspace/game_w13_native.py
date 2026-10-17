"""Host-owned CP W13 native replay, independent from the copied game worker.

The only admissible native result is one finite WORLD W13 Movement 01
two-room trace. Previous BUILD/WITNESS browser evidence and GitHub artifacts
do not substitute for an actual admitted workstation computation.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from network.witness_w13_independent import (
    independent_w13_replay, WORLD_CONTRACT, W12_SOURCE_SHA256,
)

CP_ID = "GAME-W13-WORLDS"
WORKER_ROLE = "game-build"
VERIFIER = "cp-checker:GAME-W13-WORLDS"
VERSION = "game-w13-multiworld-v1"
ACTIONS = ["right", "interact", "advance", "right", "interact"]
WORLDS = [{"id": label, "spec": deepcopy(spec)} for label, spec in WORLD_CONTRACT]
REPORT_KIND = "game-w13-worlds-native/v1"


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validate_game_request(request: Any) -> dict:
    if type(request) is not dict or set(request) != {"contract", "worlds", "actions", "w12_sha256"}:
        raise ValueError("W13 CP request has missing or unexpected fields")
    expect = {"contract": VERSION, "worlds": WORLDS, "actions": ACTIONS,
              "w12_sha256": W12_SOURCE_SHA256}
    if canonical(request) != canonical(expect):
        raise ValueError("W13 CP request disagrees with WORLD's exact bounded game")
    return deepcopy(expect)


def verify_native_report(request: dict, report: dict) -> dict:
    validate_game_request(request)
    if type(report) is not dict or set(report) != {"receipt", "pid"}:
        raise ValueError("W13 worker output shape differs from contract")
    if type(report["pid"]) is not int or report["pid"] <= 0:
        raise ValueError("W13 worker subprocess pid invalid")
    # Separate WITNESS-authored oracle reads original W12 transition source.
    # It does not load copied worker or BUILD W13 verifier.
    result = independent_w13_replay(report["receipt"])
    if (not result["valid"] or not result["solved"] or result["worlds_completed"] != 2
            or result["boundaries_checked"] != 1
            or report["receipt"]["actions"] != ACTIONS
            or [w["id"] for w in report["receipt"]["worlds"]] != [w["id"] for w in WORLDS]):
        raise ValueError("W13 source-owned worker failed independent WORLD/W12 replay")
    return result
