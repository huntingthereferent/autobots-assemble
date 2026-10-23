"""Read-only, multi-repository capacity observation for the A/B research factory.

Consumes source-labelled API observations; never provisions accounts, executes
workers, admits handoffs, merges research results, or declares a scientific test.
Node count is not fixed; practical input size and provider limits are external.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

SCHEMA = "ab-factory-capacity-observation/v1"
MAX_AGE_SECONDS = 900
MIN_PRESSURE_SECONDS = 600
MIN_PRESSURE_SAMPLES = 3


def _instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("observation time must be an ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid observation time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("observation time needs a timezone")
    return parsed.astimezone(timezone.utc)


def _count(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(name + " must be a nonnegative integer")
    return value


def _ref(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1500:
        raise ValueError(name + " must be a nonblank source reference")
    return value.strip()


def _sample(row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError("capacity observation must be an object")
    stamps = row.get("source_refs")
    if not isinstance(stamps, dict):
        raise ValueError("provider-filtered counts need source_refs")
    limit = row.get("declared_concurrency_limit")
    if limit is not None:
        _count(limit, "declared_concurrency_limit")
        if limit == 0:
            raise ValueError("declared limit must be positive")
        _ref(row.get("limit_evidence_ref"), "limit_evidence_ref")
    elif row.get("limit_evidence_ref") is not None:
        raise ValueError("limit evidence without declared limit")
    return {
        "captured_at": _instant(row.get("captured_at")),
        "active": _count(row.get("active"), "active"),
        "queued": _count(row.get("queued"), "queued"),
        "historical_total": _count(row.get("historical_total"), "historical_total"),
        "active_ref": _ref(stamps.get("active"), "active source"),
        "queued_ref": _ref(stamps.get("queued"), "queued source"),
        "limit": limit,
        "limit_ref": row.get("limit_evidence_ref"),
    }


def evaluate(snapshot: dict, *, now: datetime | None = None) -> dict:
    """Return advisory capacity evidence, never an authorization to scale.

    A repeated queue is not proof of platform saturation. An optional declared
    concurrency ceiling remains operator-reported, even with its source ref.
    """
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise ValueError("unknown factory capacity schema")
    nodes = snapshot.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("nodes must be a list")
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("now must be timezone aware")
    now = now.astimezone(timezone.utc)
    output = []
    seen = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("node must be an object")
        node_id = _ref(node.get("node_id"), "node_id")
        if node_id in seen:
            raise ValueError("duplicate node: " + node_id)
        seen.add(node_id)
        provider = node.get("provider")
        if provider != "github-actions":
            raise ValueError("only github-actions is observed by this adapter")
        raw = node.get("observations")
        if not isinstance(raw, list) or not raw:
            raise ValueError("node requires at least one real observation")
        samples = [_sample(s) for s in raw]
        if any(a["captured_at"] >= b["captured_at"]
               for a, b in zip(samples, samples[1:])):
            raise ValueError("observations must be chronologically ordered")
        if samples[-1]["captured_at"] > now:
            raise ValueError("future observation")
        last = samples[-1]
        age = (now - last["captured_at"]).total_seconds()
        pressure = [x for x in samples if x["queued"] > 0]
        repeated = (
            len(samples) >= MIN_PRESSURE_SAMPLES
            and all(x["queued"] > 0 for x in samples[-MIN_PRESSURE_SAMPLES:])
            and (samples[-1]["captured_at"] -
                 samples[-MIN_PRESSURE_SAMPLES]["captured_at"]).total_seconds()
                >= MIN_PRESSURE_SECONDS
        )
        ceilings = [x["limit"] for x in samples[-MIN_PRESSURE_SAMPLES:]]
        # The provider's limit is not derived from history or sample counts.
        ceiling_declared = (
            repeated and len(ceilings) == MIN_PRESSURE_SAMPLES
            and ceilings[0] is not None and len(set(ceilings)) == 1
        )
        saturated = (ceiling_declared and all(
            x["active"] >= ceilings[0]
            for x in samples[-MIN_PRESSURE_SAMPLES:]
        ))
        if age > MAX_AGE_SECONDS:
            state = "STALE"
        elif saturated:
            state = "SCALE_REVIEW_CANDIDATE"
        elif repeated:
            state = "SUSTAINED_QUEUE_CAPACITY_UNKNOWN"
        elif last["queued"]:
            state = "QUEUE_OBSERVED_NOT_SATURATION"
        else:
            state = "NO_QUEUE_OBSERVED"
        output.append({
            "node_id": node_id, "provider": provider, "state": state,
            "latest": {
                "captured_at": last["captured_at"].isoformat(),
                "active": last["active"], "queued": last["queued"],
                "historical_total": last["historical_total"],
                "active_ref": last["active_ref"], "queued_ref": last["queued_ref"],
            },
            "observation_count": len(samples),
            "sustained_queue": bool(repeated),
            "concurrency_limit": ceilings[0] if ceiling_declared else None,
            "limit_evidence_ref": last["limit_ref"] if ceiling_declared else None,
            "limit_status": "OPERATOR_DECLARED_NOT_INDEPENDENTLY_VERIFIED"
                            if ceiling_declared else "UNKNOWN",
            "expansion_authorized": False,
            "research_results_verified": 0,
        })
    return {
        "schema": SCHEMA,
        "read_only": True,
        "measured_node_count": len(output),
        "totals": {
            "active": sum(n["latest"]["active"] for n in output
                          if n["state"] != "STALE"),
            "queued": sum(n["latest"]["queued"] for n in output
                          if n["state"] != "STALE"),
            "fresh_nodes": sum(n["state"] != "STALE" for n in output),
            "scale_review_candidates": sum(
                n["state"] == "SCALE_REVIEW_CANDIDATE" for n in output),
        },
        "nodes": output,
        "boundaries": [
            "GitHub Actions executions are not independent research results.",
            "Historical run counts are not throughput or research coverage.",
            "Queued work alone does not prove capacity saturation.",
            "An operator-declared concurrency limit requires independent review.",
            "A source reference in input is not itself authenticated by this script.",
            "No cross-account handoff, lineage transfer, provisioning or model-agent instance is created.",
            "No fixed architecture-wide node count is inferred from local finite experiment limits.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    if not args.input.is_file() or args.input.stat().st_size > 2_000_000:
        raise ValueError("input must be an existing JSON file of at most 2 MB")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(evaluate(raw), indent=2))


if __name__ == "__main__":
    main()
