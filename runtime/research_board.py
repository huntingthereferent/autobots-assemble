"""Read-only projection of versioned research question checkpoints.

Research source records, not browser actions, determine answer states.
Registered checkpoint IDs avoid path traversal and stale implicit guesses.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / "research" / "questions"
STATES = ("REVIEW", "ANSWERED", "PARTIAL", "UNKNOWN", "OPEN")


def _https_link(url: object) -> bool:
    if not isinstance(url, str):
        return False
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.netloc)


def load_research_board(
    *, checkpoint: str | None = None, root: str | Path = ROOT
) -> dict:
    """Project a registered immutable checkpoint without modifying it."""
    base = Path(root)
    index_file = base / "index.json"
    if not index_file.is_file():
        return {
            "available": False,
            "reason": "research question checkpoint index is unavailable",
            "checkpoints": [],
            "questions": [],
        }
    index = json.loads(index_file.read_text(encoding="utf-8"))
    if index.get("schema_version") != 1 or not isinstance(index.get("checkpoints"), list):
        raise ValueError("unsupported research board index")
    registered = index["checkpoints"]
    ids = [entry.get("id") for entry in registered]
    if len(set(ids)) != len(ids) or not ids or not all(isinstance(x, str) for x in ids):
        raise ValueError("invalid or duplicate checkpoint IDs")
    selected = checkpoint if checkpoint is not None else index.get("current")
    if selected not in ids:
        raise ValueError("unknown research checkpoint")
    entry = registered[ids.index(selected)]
    # Do not allow the index to point outside the contract's local directory.
    filename = entry.get("file")
    if (not isinstance(filename, str) or
            not filename.endswith(".json") or
            Path(filename).name != filename or
            filename.startswith(".")):
        raise ValueError("invalid registered checkpoint filename")
    record = json.loads((base / filename).read_text(encoding="utf-8"))
    if record.get("schema_version") != 1 or record.get("checkpoint_id") != selected:
        raise ValueError("checkpoint identity or schema mismatch")
    rows = record.get("questions")
    if not isinstance(rows, list):
        raise ValueError("invalid question records")
    seen: set[str] = set()
    counts = {state: 0 for state in STATES}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid question row")
        qid, question, status = row.get("id"), row.get("question"), row.get("status")
        if not isinstance(qid, str) or not qid.strip() or qid in seen:
            raise ValueError("empty or duplicate question ID")
        seen.add(qid)
        if not isinstance(question, str) or not question.strip() or status not in STATES:
            raise ValueError("invalid question or classification")
        counts[status] += 1
        witnesses = row.get("witnesses", [])
        if not isinstance(witnesses, list):
            raise ValueError("invalid witness list")
        if any(not isinstance(w, dict) or
               not isinstance(w.get("label"), str) or
               not _https_link(w.get("url")) for w in witnesses):
            raise ValueError("invalid witness locator")
        for field in ("derived_from", "next_question_ids"):
            if (not isinstance(row.get(field, []), list) or
                    not all(isinstance(x, str) for x in row[field])):
                raise ValueError("invalid question lineage")
        if row.get("origin") and not _https_link(row["origin"]):
            raise ValueError("invalid question origin")
        if status in {"ANSWERED", "PARTIAL"}:
            if not (isinstance(row.get("answer"), str) and row["answer"].strip()
                    and isinstance(row.get("scope"), str) and row["scope"].strip()
                    and witnesses):
                raise ValueError("answered/partial questions require answer, scope, and witnesses")
        if status in {"PARTIAL", "UNKNOWN"} and not str(row.get("boundary", "")).strip():
            raise ValueError("partial/unknown questions require an explicit boundary")
    return {
        "available": True,
        "checkpoint": {
            "id": selected,
            "title": record.get("title", selected),
            "frozen_date": record.get("frozen_date", ""),
            "note": record.get("note", ""),
        },
        "checkpoints": [
            {"id": x["id"], "label": x.get("label", x["id"])}
            for x in registered
        ],
        "counts": counts,
        "questions": rows,
    }
