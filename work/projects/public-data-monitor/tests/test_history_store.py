from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.history_models import ObservationRecord, ReconciliationRecord
from app.observation_store import persist_observation
from app.platform import SourceObservation
from app.reconciliation_store import persist_reconciliation


NOW = datetime(2026, 10, 5, 10, 0, tzinfo=timezone.utc)


def make_observation(source: str, source_id: str, value: int, minute: int = 0):
    return SourceObservation(
        source=source,
        source_id=source_id,
        observed_at=NOW + timedelta(minutes=minute),
        entity_type="story",
        canonical_key=f"story:{source_id}",
        source_url=f"https://example.test/{source_id}",
        payload={"title": "same", "value": value},
    )


def test_append_only_observation_rows():
    Base.metadata.create_all(engine)
    source_id = "history-case-001"

    first = persist_observation(make_observation("api", source_id, 1))
    second = persist_observation(make_observation("api", source_id, 2, minute=1))

    with SessionLocal() as session:
        rows = list(
            session.scalars(
                select(ObservationRecord)
                .where(ObservationRecord.source_id == source_id)
                .order_by(ObservationRecord.id)
            )
        )

    assert first.change_kind == "new"
    assert second.change_kind == "changed"
    assert second.changed_fields == ["value"]
    assert len(rows) == 2
    assert rows[0].payload["value"] == 1
    assert rows[1].payload["value"] == 2


def test_persisted_reconciliation_conflict():
    Base.metadata.create_all(engine)
    source_id = "reconciliation-case-001"

    record = persist_reconciliation([
        make_observation("api", source_id, 1),
        make_observation("html", source_id, 2),
    ])

    with SessionLocal() as session:
        stored = session.get(ReconciliationRecord, record.id)

    assert stored is not None
    assert stored.status == "conflict"
    assert stored.sources == ["api", "html"]
    assert stored.conflicting_fields == ["value"]
    assert stored.selected_payload is None
