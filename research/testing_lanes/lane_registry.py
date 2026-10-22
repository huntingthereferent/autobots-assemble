"""Read-only research test lane registry and explicit study intake plan.

Never downloads external datasets, runs experiments, or infers validated claims.
Every test plan begins as unobserved. No network I/O is performed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

REGISTRY = Path(__file__).with_name("registry.json")
STATUSES = {"candidate", "active", "tested"}
DEPTHS = {"researched", "represented", "modeled", "simulated", "implemented", "measured", "externally_validated"}
ID_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_registry(data: dict) -> dict:
    """Validate source keys, boundary text, lane contracts and evidence promotions."""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported registry schema")
    if data.get("default_fetch") != "disabled" or data.get("default_admission") != "manual-per-record":
        raise ValueError("automated intake must not be silently enabled")
    if not isinstance(data.get("global_boundaries"), list) or len(data["global_boundaries"]) < 4:
        raise ValueError("required global boundaries absent")
    if not all(_nonempty(x) for x in data["global_boundaries"]):
        raise ValueError("blank global boundary")
    sources, lanes = data.get("sources"), data.get("lanes")
    if not isinstance(sources, list) or not sources:
        raise ValueError("no source catalog")
    if not isinstance(lanes, list) or not lanes:
        raise ValueError("no lane catalog")
    source_ids, lane_ids = set(), set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("invalid source")
        sid = source.get("id")
        if not _nonempty(sid) or sid in source_ids:
            raise ValueError("blank or duplicate source ID")
        source_ids.add(sid)
        u = urlsplit(str(source.get("doc_url", "")))
        if u.scheme != "https" or not u.hostname or u.username or u.password:
            raise ValueError("invalid source documentation URL")
        if not all(_nonempty(source.get(k)) for k in ("name", "kind", "boundary", "access")):
            raise ValueError("source provenance/access boundary missing")
    for lane in lanes:
        if not isinstance(lane, dict):
            raise ValueError("invalid lane")
        lid = lane.get("id")
        if (not _nonempty(lid) or not set(lid) <= ID_CHARS or lid in lane_ids):
            raise ValueError("invalid or duplicate lane ID")
        lane_ids.add(lid)
        refs = lane.get("source_ids")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            raise ValueError("missing or duplicate lane source references")
        if not set(refs) <= source_ids:
            raise ValueError("dangling source reference")
        contract = lane.get("test_contract")
        if not isinstance(contract, dict) or not all(
            _nonempty(contract.get(k)) for k in ("kind", "measurement", "counterexample")
        ):
            raise ValueError("missing falsifiable test contract")
        if not _nonempty(lane.get("name")) or not _nonempty(lane.get("question")):
            raise ValueError("missing lane identity/question")
        status = lane.get("status")
        if status not in STATUSES or lane.get("reached_depth") not in DEPTHS:
            raise ValueError("invalid lane evidence classification")
        witnesses = lane.get("witnesses")
        if not isinstance(witnesses, list):
            raise ValueError("invalid witness list")
        if status == "candidate" and (witnesses or lane.get("last_run") is not None):
            raise ValueError("candidate cannot claim existing experiment evidence")
        if status == "tested" and (not witnesses or not lane.get("last_run")):
            raise ValueError("tested lane requires real witness and last run")
        if status != "candidate" and not witnesses:
            raise ValueError("active/tested lane requires explicit source/witness")
    return {"schema_version": 1, "sources": len(sources), "lanes": len(lanes)}


def read_registry(path: str | Path = REGISTRY) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_registry(data)
    return data


def make_plan(lane_id: str, data: dict) -> dict:
    """Freeze a candidate test question; an actual source receipt is still required."""
    validate_registry(data)
    lane = next((x for x in data["lanes"] if x["id"] == lane_id), None)
    if lane is None:
        raise ValueError("unknown research test lane")
    source_by_id = {s["id"]: s for s in data["sources"]}
    return {
        "schema_version": 1,
        "lane_id": lane_id,
        "status": "UNOBSERVED",
        "question": lane["question"],
        "test_contract": lane["test_contract"],
        "source_candidates": [
            {"id": source_by_id[sid]["id"], "documentation_url": source_by_id[sid]["doc_url"],
             "access_boundary": source_by_id[sid]["boundary"]}
            for sid in lane["source_ids"]
        ],
        "source_receipt": {
            "record_id": None, "record_type": None, "version": None, "retrieved_at_utc": None,
            "rights_review": None, "raw_sha256": None, "source_url": None,
        },
        "experimental_witness": {
            "code_commit": None, "environment": None, "inputs_sha256": None,
            "outputs_sha256": None, "metric": None, "comparison": None, "outcome": "UNKNOWN",
        },
        "next_gate": "Select a single public record, review access rights, freeze identifiers and timestamps; only then run bounded reproduction.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "list", "plan"))
    parser.add_argument("lane_id", nargs="?")
    args = parser.parse_args()
    data = read_registry()
    if args.command == "check":
        print(json.dumps(validate_registry(data), sort_keys=True))
    elif args.command == "list":
        for lane in data["lanes"]:
            print(f'{lane["id"]:8} {lane["status"]:10} {lane["name"]}')
    elif args.command == "plan":
        if not args.lane_id:
            parser.error("plan requires a lane ID")
        print(json.dumps(make_plan(args.lane_id, data), indent=2))


if __name__ == "__main__":
    main()
