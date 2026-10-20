"""Explicit, reviewable Continuity Engine -> research board checkpoint proposals.

The board's original freezes are never edited. Each proposal is materialized
in a NEW directory and is not implicitly published to a live board.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from research.continuity_engine import ContinuityEngine, ContinuityRecord
from runtime.research_board import load_research_board


@dataclass(frozen=True)
class BoardProposal:
    checkpoint_id: str
    directory: Path
    board_status: str
    mathematical_status: str
    question_id: str
    mathematical_question_id: str


def _valid_url(raw: str | None) -> bool:
    if not isinstance(raw, str):
        return False
    try:
        u = urlsplit(raw)
        return u.scheme == "https" and bool(u.netloc) and not u.username and not u.password
    except ValueError:
        return False


def _clean_id(question_id: str) -> str:
    if not isinstance(question_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,59}", question_id):
        raise ValueError("question ID must be an unambiguous board-safe identifier")
    return question_id


def _status_and_answer(record: ContinuityRecord, witness_url: str | None) -> tuple[str, str, str]:
    """A correct mathematical outcome is distinct from board publication."""
    remaining = "Full simultaneous A/B action has not been watched or certified."
    if record.status == "UNKNOWN_BUDGET":
        return "UNKNOWN", "", "B-only observation budget exhausted without a proof. " + remaining
    if record.status == "DISTINGUISHED_B_ACTIONS":
        answer = "No: differing B^n fixed-point counts obstruct restricted B-conjugacy."
    elif record.status == "B_ONLY_CONJUGACY_WITNESSED":
        answer = "Yes: a complete B-intertwining bijection was constructed and verified."
    else:
        raise ValueError("unadmitted mathematical outcome")
    if witness_url is None:
        return "REVIEW", "", "Mathematical result verified locally; independently locatable published witness not yet supplied. " + remaining
    return "ANSWERED", answer, remaining


def stage_checkpoint(
    handoff: str,
    *,
    question_id: str,
    question: str,
    source_board_root: str | Path,
    candidate_directory: str | Path,
    frozen_date: str,
    expected_question_id: str | None = None,
    witness_url: str | None = None,
    witness_label: str = "Cyclic Action witness",
    derived_from: tuple[str, ...] = (),
) -> BoardProposal:
    """Stage a new, board-readable checkpoint without updating its live source.

    The caller must separately review and publish its independently locatable
    witness. A supplied HTTPS URL is syntax-checked, not remotely audited.
    No old question's answer/status is inferred from the new mathematical data.
    """
    qid = _clean_id(question_id)
    if not isinstance(question, str) or not question.strip():
        raise ValueError("a written question is required")
    if not isinstance(frozen_date, str) or not re.fullmatch(r"\d{4}-\d\d-\d\d", frozen_date):
        raise ValueError("explicit ISO frozen date required")
    if witness_url is not None and not _valid_url(witness_url):
        raise ValueError("published witness locator must be HTTPS")
    if not isinstance(witness_label, str) or not witness_label.strip():
        raise ValueError("witness label is required")
    if any(not isinstance(x, str) or not x.strip() for x in derived_from):
        raise ValueError("invalid predecessor question ID")

    record = ContinuityEngine().verify(handoff, expected_question_id=expected_question_id)
    if record.area != "cyclic_action/B" or record.scope != "B_ONLY_ON_DECLARED_INVARIANT_CARRIER":
        raise ValueError("unsupported Continuity Engine relation")

    origin = Path(source_board_root).resolve()
    destination = Path(candidate_directory).resolve()
    if origin == destination or origin in destination.parents or destination in origin.parents:
        raise ValueError("staged output must be separate from the source board")
    live = load_research_board(root=origin)
    if not live["available"]:
        raise ValueError("existing research board is unavailable")
    if qid in {q["id"] for q in live["questions"]}:
        raise ValueError("new question ID already exists")
    if any(d not in {q["id"] for q in live["questions"]} for d in derived_from):
        raise ValueError("source question is not present in this checkpoint")
    index = json.loads((origin / "index.json").read_text(encoding="utf-8"))
    checked = {}
    for item in index["checkpoints"]:
        check = load_research_board(root=origin, checkpoint=item["id"])
        filename = item["file"]
        checked[filename] = (origin / filename).read_bytes()
        if not check["available"]:
            raise ValueError("registered source checkpoint is unavailable")

    mathematical = json.loads(record.snapshots[-1]["payload"])
    carrier_size = len(mathematical["question"]["carrier"])
    status, answer, boundary = _status_and_answer(record, witness_url)
    snapshot_digest = record.snapshots[-1]["sha256"]
    fingerprint = sha256(handoff.encode("utf-8")).hexdigest()[:12]
    checkpoint_id = "continuity-" + qid.lower() + "-" + fingerprint
    filename = checkpoint_id + ".json"
    existing_cp = {i["id"] for i in index["checkpoints"]}
    if checkpoint_id in existing_cp:
        raise ValueError("checkpoint already registered")
    row = {
        "id": qid,
        "question": question,
        "status": status,
        "answer": answer,
        "scope": f"Cyclic B-action on the declared {carrier_size}-state invariant carrier; A/B untested",
        "boundary": boundary,
        "witnesses": ([{"label": witness_label, "url": witness_url}] if witness_url else []),
        "derived_from": list(derived_from),
        "next_question_ids": [],
        "engine_area": record.area,
        "engine_question_id": record.question_id,
        "engine_status": record.status,
        "engine_snapshot_sha256": snapshot_digest,
        "engine_checkpoint_count": len(record.snapshots),
    }
    snapshot = {
        "schema_version": 1,
        "checkpoint_id": checkpoint_id,
        "frozen_date": frozen_date,
        "title": f"Continuity Engine — {qid}",
        "note": "Staged candidate only. Previous questions are unchanged; publication requires review of the linked mathematical witness.",
        "questions": deepcopy(live["questions"]) + [row],
    }
    index["checkpoints"].append({"id": checkpoint_id, "file": filename,
                                 "label": f"{frozen_date} · Continuity {qid}"})
    index["current"] = checkpoint_id
    destination.mkdir(parents=True, exist_ok=False)
    for name, blob in checked.items():
        (destination / name).write_bytes(blob)
    (destination / filename).write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (destination / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    admitted = load_research_board(root=destination)
    if admitted["checkpoint"]["id"] != checkpoint_id or admitted["questions"][-1] != row:
        raise AssertionError("candidate checkpoint failed board projection")
    return BoardProposal(checkpoint_id, destination, status, record.status, qid, record.question_id)
