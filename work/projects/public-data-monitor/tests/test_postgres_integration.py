from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.db import Base, SessionLocal, engine
from app.ingest import persist_events
from app.main import app
from app.models import EarthquakeEvent
from app.schemas import EarthquakeIn


def event(source_id: str = "eq-1", magnitude: float = 2.5) -> EarthquakeIn:
    when = datetime(2026, 10, 5, 7, 0, tzinfo=timezone.utc)
    return EarthquakeIn(
        source_id=source_id,
        magnitude=magnitude,
        place="Test location",
        longitude=-94.5,
        latitude=39.1,
        depth_km=8.2,
        occurred_at=when,
        source_updated_at=when,
        source_url=f"https://example.test/{source_id}",
    )


def reset_database() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        session.execute(delete(EarthquakeEvent))
        session.commit()


def test_replay_is_idempotent_and_updates_existing_row():
    reset_database()

    first = persist_events([event()])
    second = persist_events([event(magnitude=3.1)])

    with SessionLocal() as session:
        count = session.scalar(select(func.count()).select_from(EarthquakeEvent))
        row = session.get(EarthquakeEvent, "eq-1")

    assert first["rows_before"] == 0
    assert first["rows_after"] == 1
    assert first["new_rows"] == 1
    assert second["rows_before"] == 1
    assert second["rows_after"] == 1
    assert second["new_rows"] == 0
    assert count == 1
    assert row is not None
    assert row.magnitude == 3.1


def test_api_returns_persisted_rows():
    reset_database()
    persist_events([event("eq-api", 4.2)])

    client = TestClient(app)
    response = client.get("/api/events?limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["source_id"] == "eq-api"
    assert payload[0]["magnitude"] == 4.2
