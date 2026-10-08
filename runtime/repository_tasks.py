"""Source-linked bridge from the repository's *active* work ledger.

The Markdown ledger is already an explicit work record. This adapter admits
only active MOVE rows as durable handoffs, never pinned/frozen/evidence rows.
It does not execute them, complete them, or redefine A/B.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from .engine import HandoffRuntime
from .handoff import Handoff


WORK_LINK = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)$")
SAFE_ID = re.compile(r"^[a-zA-Z0-9_.\-/]+(?:#[a-zA-Z0-9_.\-]+)?$")


@dataclass(frozen=True)
class RepositoryWork:
    title: str
    lane: str
    state: str
    next_movement: str
    link: str
    row_number: int
    source_id: str


def read_active_work(file_path: str | Path) -> tuple[RepositoryWork, ...]:
    """Read only the active work table, retaining row-level provenance."""
    source = Path(file_path)
    rows: list[RepositoryWork] = []
    inside = False
    seen: set[str] = set()
    for number, raw in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line == "## Active ALL WORK":
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if not inside or not line.startswith("|"):
            continue
        cells = [part.strip() for part in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"Work", "---"}:
            continue
        # Explicit recorded movement only; archive, pins and static evidence
        # are not obligations and are not admitted into an agent's task queue.
        linked = WORK_LINK.fullmatch(cells[0])
        if not linked or not cells[2].startswith("MOVE"):
            continue
        title, link = linked.groups()
        if (not SAFE_ID.fullmatch(link) or link.startswith("/")
                or ".." in Path(link.split("#", 1)[0]).parts):
            raise ValueError(f"unsafe repository link at {source.name}:{number}")
        if not title.strip() or not cells[3].strip():
            raise ValueError(f"incomplete active work at {source.name}:{number}")
        key = f"{title.strip()}|{link}"
        source_id = sha256(key.encode("utf-8")).hexdigest()[:20]
        if source_id in seen:
            continue
        seen.add(source_id)
        rows.append(RepositoryWork(title.strip(), cells[1], cells[2],
                                   cells[3], link, number, source_id))
    return tuple(rows)


def admit_active_work(runtime: HandoffRuntime, file_path: str | Path,
                      *, actor_id: str = "james") -> tuple[str, ...]:
    """Idempotent source admission; no local task model or work fabrication."""
    if not actor_id.strip():
        raise ValueError("actor_id is required")
    file_path = Path(file_path)
    source = read_active_work(file_path)  # Parse/validate before any mutation.
    births: list[str] = []
    current = runtime.snapshot()
    for row in source:
        handoff_id = "repo-work-" + row.source_id
        if handoff_id in current:
            existing = runtime.get(handoff_id)
            if existing.metadata.get("repository_work_id") != row.source_id:
                raise ValueError("repository handoff ID collision")
            continue
        runtime.submit(Handoff(
            handoff_id=handoff_id,
            referent=row.title,
            from_actor="github-work-ledger",
            to_actor=actor_id.strip().casefold(),
            required_relation="Follow recorded repository work",
            inputs={"lane": row.lane, "recorded_state": row.state,
                    "next_movement": row.next_movement,
                    "source_link": row.link,
                    "source": file_path.name,
                    "row_number": row.row_number},
            expected_output={"movement": "witnessed status or supported next step"},
            required_witnesses=("work disposition reported",),
            admissible_evidence={"work disposition reported": ("human_report", "source")},
            boundaries=("Active work is not completed work.",
                        "Do not replace the source record or infer task completion.",
                        "A/B result and human task disposition require separate witnesses."),
            provenance=(f"repository:{file_path.name}:{row.row_number}",
                        f"repository-work:{row.source_id}",
                        f"repository-link:{row.link}"),
            metadata={"title": row.title, "source_system": "repository",
                      "repository_work_id": row.source_id,
                      "repository_source": file_path.name},
        ))
        births.append(handoff_id)
    return tuple(births)
