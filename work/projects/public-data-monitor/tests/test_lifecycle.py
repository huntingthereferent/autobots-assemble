from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.history_models import LifecycleRecord, ObservationRecord
from app.lifecycle_store import current_lifecycle, persist_complete_snapshot
from app.main import app
from app.platform import SourceObservation


NOW = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)
SOURCE = "lifecycle_fixture"


def observation(source_id: str, value: int, minute: int) -> SourceObservation:
    return SourceObservation(
        source=SOURCE,
        source_id=source_id,
        observed_at=NOW + timedelta(minutes=minute),
        entity_type="fixture",
        canonical_key=f"fixture:{source_id}",
        payload={"value": value},
    )


def lifecycle_rows(source_id: str) -> list[LifecycleRecord]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(LifecycleRecord)
                .where(
                    LifecycleRecord.source == SOURCE,
                    LifecycleRecord.source_id == source_id,
                )
                .order_by(LifecycleRecord.id)
            )
        )


def test_disappearance_preserves_history_and_reappearance_is_explicit():
    Base.metadata.create_all(engine)
    source_id = "entity-1"

    first = persist_complete_snapshot(
        SOURCE,
        [observation(source_id, 1, 0)],
        recorded_at=NOW,
    )
    assert [row.transition for row in first] == ["new"]

    missing = persist_complete_snapshot(
        SOURCE,
        [],
        recorded_at=NOW + timedelta(minutes=1),
    )
    assert [row.transition for row in missing] == ["disappeared"]

    with SessionLocal() as session:
        observations_after_missing = list(
            session.scalars(
                select(ObservationRecord)
                .where(
                    ObservationRecord.source == SOURCE,
                    ObservationRecord.source_id == source_id,
                )
                .order_by(ObservationRecord.id)
            )
        )

    assert len(observations_after_missing) == 1
    assert observations_after_missing[0].payload == {"value": 1}

    state_while_missing = current_lifecycle(SOURCE)
    entity_state = next(row for row in state_while_missing if row.source_id == source_id)
    assert entity_state.state == "disappeared"
    assert entity_state.transition == "disappeared"
    assert entity_state.observation_id is None

    repeated_missing = persist_complete_snapshot(
        SOURCE,
        [],
        recorded_at=NOW + timedelta(minutes=2),
    )
    assert repeated_missing == []

    reappeared = persist_complete_snapshot(
        SOURCE,
        [observation(source_id, 2, 3)],
        recorded_at=NOW + timedelta(minutes=3),
    )
    assert [row.transition for row in reappeared] == ["reappeared"]

    rows = lifecycle_rows(source_id)
    assert [row.transition for row in rows] == [
        "new",
        "disappeared",
        "reappeared",
    ]

    with SessionLocal() as session:
        history = list(
            session.scalars(
                select(ObservationRecord)
                .where(
                    ObservationRecord.source == SOURCE,
                    ObservationRecord.source_id == source_id,
                )
                .order_by(ObservationRecord.id)
            )
        )

    assert len(history) == 2
    assert [row.payload["value"] for row in history] == [1, 2]
    assert history[-1].change_kind == "changed"

    current = current_lifecycle(SOURCE)
    entity_state = next(row for row in current if row.source_id == source_id)
    assert entity_state.state == "present"
    assert entity_state.transition == "reappeared"


def test_lifecycle_api_exposes_current_state():
    source_id = "api-entity"
    persist_complete_snapshot(
        SOURCE,
        [observation(source_id, 10, 10)],
        recorded_at=NOW + timedelta(minutes=10),
    )
    persist_complete_snapshot(
        SOURCE,
        [],
        recorded_at=NOW + timedelta(minutes=11),
    )

    client = TestClient(app)
    response = client.get(f"/api/lifecycle?source={SOURCE}")

    assert response.status_code == 200
    payload = response.json()
    row = next(item for item in payload if item["source_id"] == source_id)
    assert row["state"] == "disappeared"
    assert row["transition"] == "disappeared"
    assert row["observation_id"] is None


def test_snapshot_rejects_duplicate_source_identity_before_writing():
    source_id = "duplicate-identity"
    before = lifecycle_rows(source_id)

    try:
        persist_complete_snapshot(
            SOURCE,
            [
                observation(source_id, 1, 20),
                observation(source_id, 2, 20),
            ],
            recorded_at=NOW + timedelta(minutes=20),
        )
    except ValueError as exc:
        assert "duplicate source identities" in str(exc)
    else:
        raise AssertionError("duplicate source identity should fail")

    assert lifecycle_rows(source_id) == before
