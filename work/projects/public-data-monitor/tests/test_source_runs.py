from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.main import app
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


def test_source_run_health_is_queryable_through_api():
    def fetch():
        return []

    run_source("fixture_ops_api", fetch)

    client = TestClient(app)
    response = client.get("/api/ops/source-runs?source=fixture_ops_api&limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["source"] == "fixture_ops_api"
    assert payload[0]["status"] == "success"
    assert payload[0]["items_seen"] == 0


def test_task_id_is_persisted_for_source_run():
    from app.source_runs import start_source_run, finish_source_run

    run_id = start_source_run("fixture_task_correlation", task_id="task-123")
    finish_source_run(run_id, items_seen=2)

    with SessionLocal() as session:
        record = session.get(SourceRun, run_id)

    assert record is not None
    assert record.task_id == "task-123"
    assert record.status == "success"
    assert record.items_seen == 2
