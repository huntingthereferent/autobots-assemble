from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.orchestrator import run_source
from app.platform import SourceObservation
from app.run_models import SourceRun


def test_successful_source_run_is_persisted():
    Base.metadata.create_all(engine)

    def fetch():
        return [
            SourceObservation(
                source="fixture_success",
                source_id="1",
                observed_at="2026-10-05T10:00:00Z",
                entity_type="example",
                canonical_key="example:1",
                payload={"value": 1},
            )
        ]

    rows = run_source("fixture_success", fetch)
    assert len(rows) == 1

    with SessionLocal() as session:
        record = session.scalar(
            select(SourceRun)
            .where(SourceRun.source == "fixture_success")
            .order_by(SourceRun.id.desc())
            .limit(1)
        )

    assert record is not None
    assert record.status == "success"
    assert record.items_seen == 1
    assert record.finished_at is not None


def test_failed_source_run_preserves_error():
    Base.metadata.create_all(engine)

    def fetch():
        raise RuntimeError("fixture failure")

    try:
        run_source("fixture_failure", fetch)
    except RuntimeError:
        pass

    with SessionLocal() as session:
        record = session.scalar(
            select(SourceRun)
            .where(SourceRun.source == "fixture_failure")
            .order_by(SourceRun.id.desc())
            .limit(1)
        )

    assert record is not None
    assert record.status == "failed"
    assert record.error_type == "RuntimeError"
    assert "fixture failure" in record.error_message
