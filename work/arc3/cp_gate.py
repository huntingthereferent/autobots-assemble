"""A/entry and B/output CP-style evidence boundary for selected native ARC lanes.

Source-owned ARC observations only. Original finite-correspondence CP20–CP30
is historical research, not automatic authority to admit an unrelated ARC job.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[2]
CONTEXT_FILES = (
    "work/arc3/AGENTS.md",
    "work/arc3/ARC_LANES_G_P.md",
)
LANES = {
    "sp80-stage3": {
        "source": "work/arc3/native_sp80_stage3_native_feedback.py",
        "output": "runtime/data/arc3/original-sp80-stage3-native-feedback.json",
        "prior": "Original stage3 measurement run 39463571663; proposals frozen in source",
        "kind": "ACTUAL_ORIGINAL_SP80_STAGE3_SOURCE_FEEDBACK_CONTRAST",
    },
    **{
        "window48-" + game: {
            "source": "work/arc3/native_smoke.py",
            "extra_source": "work/arc3/agent/my_agent.py",
            "output": "runtime/data/arc3/window48-" + game + ".json",
            "prior": "Source-owned window48 experiment; reset/action evidence only",
            "game": game,
        }
        for game in ("sk48", "ls20", "ft09")
    },
}


def _sha(path: Path) -> str:
    if not path.is_file():
        raise ValueError("CP_WALL: missing pinned source: " + str(path))
    return sha256(path.read_bytes()).hexdigest()


def _commit(root: Path) -> str:
    if not (root / ".git").exists():
        return "UNAVAILABLE_LOCAL_FIXTURE"
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("CP_WALL: source checkout identity unavailable") from exc


def _spec(lane: str):
    if lane not in LANES:
        raise ValueError("CP_WALL: ARC lane not registered")
    return LANES[lane]


def entry(lane: str, *, root: Path = ROOT) -> dict:
    """A: only an exact existing source-bound task, without running SDK."""
    spec = _spec(lane)
    files = (spec["source"], *CONTEXT_FILES)
    if "extra_source" in spec:
        files += (spec["extra_source"],)
    pins = {name: _sha(root / name) for name in files}
    return {
        "schema": "arc-native-cp-boundary/v1",
        "side": "A/ENTRY",
        "lane": lane,
        "referent": "original ARC-AGI-3 native SDK observation",
        "source_commit": _commit(root),
        "source_pins": pins,
        "source_owned_historical_observation": spec["prior"],
        "preserved": "Exact native SDK frames/status, independent resets and previous negative results",
        "boundary": "No predicted win, inferred game law or borrowed CP30 authority",
        "expected_output": spec["output"],
        "next_possible_not_automatic": "Compare source-observed result with frozen native question",
        "task_selected_by_historical_record": False,
        "worker_executed": False,
        "admission": "THIS_EXACT_LANE_SOURCE_ONLY",
    }


def verify_entry(lane: str, receipt: dict, *, root: Path = ROOT) -> None:
    spec = _spec(lane)
    expected = entry(lane, root=root)
    if receipt != expected:
        raise ValueError("CP_WALL: stale, changed or unrelated A/entry CP context")
    if receipt["expected_output"] != spec["output"]:
        raise ValueError("CP_WALL: unrelated native output destination")


def _npz_pin(path: Path) -> str:
    if not path.is_file():
        raise ValueError("CP_WALL: native raw-frame NPZ missing: " + str(path))
    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            if not names or any(not name.endswith(".npy") for name in names):
                raise ValueError("CP_WALL: native NPZ does not contain raw-frame arrays")
    except BadZipFile as exc:
        raise ValueError("CP_WALL: native raw-frame NPZ corrupted") from exc
    return _sha(path)  # Presence/container and bytes only, not independent pixel replay.


def _stage3_check(data: dict) -> dict:
    if data.get("kind") != LANES["sp80-stage3"]["kind"]:
        raise ValueError("CP_WALL: wrong original SDK report kind")
    rows = data.get("all_actual_original_sdk_records")
    plans = data.get("precommitted_candidate_words")
    if not isinstance(rows, list) or len(rows) != 32 or not isinstance(plans, list) or len(plans) != 16:
        raise ValueError("CP_WALL: original 16x2 native trial accounting missing")
    names = [x[0] for x in plans if isinstance(x, (list, tuple)) and len(x) == 2]
    if len(names) != 16 or len(set(names)) != 16:
        raise ValueError("CP_WALL: frozen source proposals changed")
    by_name = Counter(x.get("frozen_candidate") for x in rows if isinstance(x, dict))
    if by_name != Counter({n: 2 for n in names}):
        raise ValueError("CP_WALL: incomplete paired native source trials")
    roots = {x.get("original_verified_stage3_root", {}).get("original_source_sha256") for x in rows}
    if len(roots) != 1 or None in roots or next(iter(roots)) != data.get("original_source_stage3_entry_hash"):
        raise ValueError("CP_WALL: original stage3 root identity diverged")
    wins = sum(x.get("official_original_level4_or_WIN") is True for x in rows)
    if any(type(x.get("official_original_level4_or_WIN")) is not bool for x in rows):
        raise ValueError("CP_WALL: untyped original native result")
    if wins != data.get("actual_original_source_level4_or_WIN") or wins != len(data.get("original_source_successes", [])):
        raise ValueError("CP_WALL: observed native outcome and promoted successes differ")
    if dict(Counter(str(x.get("official_original_final_level")) for x in rows)) != data.get("original_sdk_final_levels"):
        raise ValueError("CP_WALL: original SDK level accounting differs")
    return {"trials": len(rows), "native_level4_or_win": wins, "negative_or_unproved": len(rows) - wins}


def _smoke_check(lane: str, data: dict, receipt: dict) -> dict:
    spec = LANES[lane]
    if data.get("game") != spec["game"] or data.get("kind") not in (
        "ORIGINAL_WINDOW48_NATIVE_INTERFACE_WALL",
        "ORIGINAL_WINDOW48_ON_NATIVE_ARC_PUBLIC_GAME_SMOKE",
    ):
        raise ValueError("CP_WALL: original SDK game/kind differs")
    n = data.get("native_environment_actions")
    if type(n) is not int or not 0 <= n <= 12:
        raise ValueError("CP_WALL: source action budget missing or exceeded")
    if data.get("source_agent_sha256") != receipt["source_pins"][spec["extra_source"]]:
        raise ValueError("CP_WALL: executed agent differs from A/entry source")
    if data["kind"] == "ORIGINAL_WINDOW48_NATIVE_INTERFACE_WALL":
        if n != 0 or data.get("status") != "WALL_NO_OBSERVED_NATIVE_A_B_GENERATORS":
            raise ValueError("CP_WALL: missing native interface-wall evidence")
    elif data.get("source_original_law_count") != 48:
        raise ValueError("CP_WALL: source mathematical family changed")
    return {"native_environment_actions": n, "interface_wall": data["kind"].endswith("_WALL")}


def exit_gate(lane: str, receipt: dict, *, root: Path = ROOT) -> dict:
    """B: link a real emitted report and frame archive to unchanged A source."""
    verify_entry(lane, receipt, root=root)
    spec = _spec(lane)
    output = root / spec["output"]
    if not output.is_file():
        raise ValueError("CP_WALL: native output was not emitted")
    data = json.loads(output.read_text(encoding="utf-8"))
    evidence = _stage3_check(data) if lane == "sp80-stage3" else _smoke_check(lane, data, receipt)
    return {
        "schema": "arc-native-cp-boundary/v1",
        "side": "B/OUTPUT",
        "lane": lane,
        "source_commit": receipt["source_commit"],
        "source_pins": receipt["source_pins"],
        "entry_sha256": sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest(),
        "native_report": spec["output"],
        "native_report_sha256": _sha(output),
        "native_frames_npz_sha256": _npz_pin(output.with_suffix(".npz")),
        "observed": evidence,
        "status": "RECORDED_NATIVE_SDK_REPORT_NOT_INDEPENDENTLY_REPLAYED",
        "worker_executed": True,
        "boundary": "Negative trials preserved; raw NPZ presence is not independent pixel verification or ARC solve",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("side", choices=("entry", "exit"))
    p.add_argument("--lane", choices=tuple(LANES), required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.side == "entry":
            result = entry(args.lane)
        else:
            result = exit_gate(args.lane, json.loads(args.receipt.read_text(encoding="utf-8")))
        destination = args.receipt if args.side == "entry" else args.receipt.with_name(args.receipt.stem + "-output.json")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(args.side.upper() + " CP " + args.lane + ": " + result.get("status", "admitted"))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("CP_WALL: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
