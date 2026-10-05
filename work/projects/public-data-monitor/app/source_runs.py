from datetime import datetime, timezone

from sqlalchemy import desc, select

from .db import Base, SessionLocal, engine
from .run_models import SourceRun


def start_source_run(source: str) -> int:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        record = SourceRun(
            source=source,
            started_at=datetime.now(timezone.utc),
            finished_at=None,
            status="running",
            items_seen=0,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.id


def finish_source_run(run_id: int, *, items_seen: int) -> None:
    with SessionLocal() as session:
        record = session.get(SourceRun, run_id)
        if record is None:
            raise ValueError(f"unknown source run {run_id}")
        record.finished_at = datetime.now(timezone.utc)
        record.status = "success"
        record.items_seen = items_seen
        session.commit()


def fail_source_run(run_id: int, error: Exception) -> None:
    with SessionLocal() as session:
        record = session.get(SourceRun, run_id)
        if record is None:
            raise ValueError(f"unknown source run {run_id}")
        record.finished_at = datetime.now(timezone.utc)
        record.status = "failed"
        record.error_type = type(error).__name__
        record.error_message = str(error)
        session.commit()


def latest_source_run(source: str) -> SourceRun | None:
    with SessionLocal() as session:
        return session.scalar(
            select(SourceRun)
            .where(SourceRun.source == source)
            .order_by(desc(SourceRun.started_at), desc(SourceRun.id))
            .limit(1)
        )
