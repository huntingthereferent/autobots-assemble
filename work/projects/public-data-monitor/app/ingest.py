from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import Base, SessionLocal, engine
from .models import EarthquakeEvent
from .schemas import EarthquakeIn
from .usgs import fetch_events


def persist_events(events: list[EarthquakeIn]) -> dict[str, int]:
    Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        before = session.scalar(select(func.count()).select_from(EarthquakeEvent)) or 0

        for event in events:
            values = {**event.model_dump(), "ingested_at": now}
            if engine.dialect.name == "postgresql":
                stmt = pg_insert(EarthquakeEvent).values(**values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[EarthquakeEvent.source_id],
                    set_={
                        "magnitude": stmt.excluded.magnitude,
                        "place": stmt.excluded.place,
                        "longitude": stmt.excluded.longitude,
                        "latitude": stmt.excluded.latitude,
                        "depth_km": stmt.excluded.depth_km,
                        "occurred_at": stmt.excluded.occurred_at,
                        "source_updated_at": stmt.excluded.source_updated_at,
                        "source_url": stmt.excluded.source_url,
                        "ingested_at": stmt.excluded.ingested_at,
                    },
                )
                session.execute(stmt)
            else:
                current = session.get(EarthquakeEvent, event.source_id)
                if current is None:
                    session.add(EarthquakeEvent(**values))
                else:
                    for key, value in values.items():
                        setattr(current, key, value)

        session.commit()
        after = session.scalar(select(func.count()).select_from(EarthquakeEvent)) or 0

    return {
        "fetched": len(events),
        "rows_before": before,
        "rows_after": after,
        "new_rows": after - before,
    }


def ingest() -> dict[str, int]:
    return persist_events(fetch_events())


if __name__ == "__main__":
    result = ingest()
    print(" ".join(f"{key}={value}" for key, value in result.items()))
