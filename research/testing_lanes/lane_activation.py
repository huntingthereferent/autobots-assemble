"""Independent research-lane source handoffs.

Each lane has a separate output, consumes only exact source receipts, and
remains scientifically UNTESTED. Source availability is not a scientific test.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from datetime import datetime

from source_admission import catalog

ROOT = Path(__file__).resolve().parent
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def accepted_receipt(source_id: str, cards: dict, receipt: dict) -> bool:
    """Require exact provider and signed-off source structure, not label-only claims."""
    card = cards[source_id]
    if (not isinstance(receipt, dict)
            or receipt.get("source_id") != source_id
            or receipt.get("state") != "METADATA_OBSERVED"
            or receipt.get("source_url") != card["probe"].get("url")
            or receipt.get("response_status") != 200
            or receipt.get("scientific_claim_verified") is not False
            or receipt.get("source_data_archived") is not False):
        return False
    checksum = receipt.get("body_sha256")
    seen_at = receipt.get("observed_at_utc")
    if not isinstance(checksum, str) or not SHA256.fullmatch(checksum):
        return False
    if not isinstance(seen_at, str):
        return False
    try:
        ts = datetime.fromisoformat(seen_at)
    except ValueError:
        return False
    if ts.tzinfo is None:
        return False
    inspection = receipt.get("inspection")
    if not isinstance(inspection, dict) or inspection.get("semantic_record_verified") is not True:
        return False
    if inspection.get("record_shape") != "expected_structure":
        return False
    return True


def handoff(lane_id: str, receipts: dict[str, dict], *, root: Path = ROOT) -> dict:
    cards = catalog(root)
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    lane = next((row for row in registry["lanes"] if row["id"] == lane_id), None)
    if lane is None:
        raise ValueError("unknown research test lane")
    sources = []
    verified = []
    for sid in lane["source_ids"]:
        receipt = receipts.get(sid)
        if accepted_receipt(sid, cards, receipt):
            status = "METADATA_AVAILABLE"
            verified.append(sid)
        elif cards[sid]["probe"]["url"] is None:
            status = "MANUAL_ACCESS_GATE"
        elif receipt is None:
            status = "NO_OBSERVATION"
        else:
            status = "SOURCE_UNVERIFIED"
        sources.append({"source_id": sid, "source_state": status,
                        "observation_receipt_present": receipt is not None})
    return {
        "schema_version": 1,
        "lane_id": lane_id,
        "lane_name": lane["name"],
        "source_feed_status": "SOURCE_METADATA_READY" if verified else "WAITING_FOR_SOURCES",
        "candidate_sources": lane["source_ids"],
        "witnessed_source_ids": verified,
        "sources": sources,
        "frozen_question": lane["question"],
        "test_contract": lane["test_contract"],
        "scientific_status": "NOT_TESTED",
        "experiment_runs": 0,
        "next_gate": (
            "Select and pin a concrete study/dataset with rights/ethics review and frozen test inputs."
            if verified else "Resolve one source observation or manual access gate before admitting a study."
        ),
    }


def read_receipts(directory: Path) -> dict[str, dict]:
    found = {}
    for path in sorted(directory.glob("*.json")):
        if not re.fullmatch(r"[a-z0-9-]+", path.stem):
            raise ValueError("unexpected receipt filename")
        if path.stem in found:
            raise ValueError("duplicate source receipt")
        found[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return found


def all_handoffs(receipts: dict[str, dict], *, root: Path = ROOT) -> list[dict]:
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    lanes = registry["lanes"]
    result = [handoff(lane["id"], receipts, root=root) for lane in lanes]
    if len({x["lane_id"] for x in result}) != len(result):
        raise ValueError("duplicate research lane output")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane_id", help="One registered lane ID, or 'all'")
    parser.add_argument("--receipts", type=Path, default=ROOT / "source_receipts")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    receipts = read_receipts(args.receipts) if args.receipts.exists() else {}
    if args.lane_id == "all":
        result = all_handoffs(receipts)
    else:
        result = [handoff(args.lane_id, receipts)]
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for entry in result:
            (args.output_dir / (entry["lane_id"] + ".json")).write_text(
                json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    print(json.dumps({
        "lanes_checked": len(result),
        "source_metadata_ready": sum(x["source_feed_status"] == "SOURCE_METADATA_READY" for x in result),
        "waiting_sources": sum(x["source_feed_status"] == "WAITING_FOR_SOURCES" for x in result),
        "scientific_tests_run": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
