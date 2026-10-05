from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import Base, SessionLocal, engine
from .models import EarthquakeEvent
from .usgs import fetch_events


def ingest() -> int:
    Base.metadata.create_all(engine)
    events = fetch_events()
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
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

    return len(events)


if __name__ == "__main__":
    count = ingest()
    print(f"ingested={count}")
