from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.history_models import ObservationRecord
from app.main import app
from app.orchestrator import run_source_persisted
from app.platform import SourceObservation
from app.run_models import SourceRun


NOW = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
SOURCE = "failure_recovery_fixture"
SOURCE_ID = "stable-1"
CANONICAL_KEY = "fixture:stable-1"


def observation(value: int, minute: int) -> SourceObservation:
    return SourceObservation(
        source=SOURCE,
        source_id=SOURCE_ID,
        observed_at=NOW + timedelta(minutes=minute),
        entity_type="fixture",
        canonical_key=CANONICAL_KEY,
        source_url="https://example.test/stable-1",
        payload={"value": value},
    )


def history_rows() -> list[ObservationRecord]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(ObservationRecord)
                .where(
                    ObservationRecord.source == SOURCE,
                    ObservationRecord.source_id == SOURCE_ID,
                )
                .order_by(ObservationRecord.id)
            )
        )


def source_runs() -> list[SourceRun]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(SourceRun)
                .where(SourceRun.source == SOURCE)
                .order_by(SourceRun.id)
            )
        )


def test_failure_preserves_last_valid_state_and_recovery_appends_cleanly():
    Base.metadata.create_all(engine)

    run_source_persisted(SOURCE, lambda: [observation(1, 0)])
    before_failure = history_rows()
    assert len(before_failure) == 1
    assert before_failure[-1].payload == {"value": 1}
    assert before_failure[-1].change_kind == "new"

    def broken_fetch():
        raise RuntimeError("injected upstream outage")

    with pytest.raises(RuntimeError, match="injected upstream outage"):
        run_source_persisted(SOURCE, broken_fetch)

    after_failure = history_rows()
    assert len(after_failure) == 1
    assert after_failure[-1].payload == {"value": 1}

    runs_after_failure = source_runs()
    assert [row.status for row in runs_after_failure[-2:]] == ["success", "failed"]
    assert runs_after_failure[-1].error_type == "RuntimeError"
    assert "injected upstream outage" in runs_after_failure[-1].error_message

    client = TestClient(app)
    ops = client.get(f"/api/ops/source-runs?source={SOURCE}&limit=2")
    assert ops.status_code == 200
    assert ops.json()[0]["status"] == "failed"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert f'source="{SOURCE}",status="failed"' in metrics.text

    history = client.get(f"/api/history/{CANONICAL_KEY}")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["payload"] == {"value": 1}

    run_source_persisted(SOURCE, lambda: [observation(2, 2)])

    recovered_history = history_rows()
    assert len(recovered_history) == 2
    assert recovered_history[-1].payload == {"value": 2}
    assert recovered_history[-1].change_kind == "changed"
    assert recovered_history[-1].changed_fields == ["value"]

    recovered_runs = source_runs()
    assert [row.status for row in recovered_runs[-3:]] == [
        "success",
        "failed",
        "success",
    ]

    latest_ops = client.get(f"/api/ops/source-runs?source={SOURCE}&limit=1")
    assert latest_ops.status_code == 200
    assert latest_ops.json()[0]["status"] == "success"


def test_commit_failure_marks_run_failed_without_mutating_history():
    Base.metadata.create_all(engine)
    source = "commit_failure_fixture"

    good = SourceObservation(
        source=source,
        source_id="stable",
        observed_at=NOW,
        entity_type="fixture",
        canonical_key="fixture:commit-failure",
        payload={"value": "stable"},
    )
    run_source_persisted(source, lambda: [good])

    with SessionLocal() as session:
        before = list(
            session.scalars(
                select(ObservationRecord).where(ObservationRecord.source == source)
            )
        )
    assert len(before) == 1

    from app.orchestrator import run_source

    def rejected_commit(_observations):
        raise RuntimeError("injected durable commit failure")

    with pytest.raises(RuntimeError, match="injected durable commit failure"):
        run_source(
            source,
            lambda: [
                SourceObservation(
                    source=source,
                    source_id="new",
                    observed_at=NOW + timedelta(minutes=1),
                    entity_type="fixture",
                    canonical_key="fixture:commit-failure-new",
                    payload={"value": "must-not-persist"},
                )
            ],
            commit=rejected_commit,
        )

    with SessionLocal() as session:
        after = list(
            session.scalars(
                select(ObservationRecord).where(ObservationRecord.source == source)
            )
        )
        latest_run = session.scalar(
            select(SourceRun)
            .where(SourceRun.source == source)
            .order_by(SourceRun.id.desc())
            .limit(1)
        )

    assert len(after) == 1
    assert after[0].payload == {"value": "stable"}
    assert latest_run is not None
    assert latest_run.status == "failed"
    assert latest_run.error_type == "RuntimeError"
