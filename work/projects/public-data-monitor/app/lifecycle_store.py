from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .history_models import LifecycleRecord, ObservationRecord
from .observation_store import _build_record
from .platform import SourceObservation


def _latest_states(session: Session, source: str) -> dict[str, LifecycleRecord]:
    rows = list(
        session.scalars(
            select(LifecycleRecord)
            .where(LifecycleRecord.source == source)
            .order_by(
                LifecycleRecord.source_id,
                desc(LifecycleRecord.recorded_at),
                desc(LifecycleRecord.id),
            )
        )
    )

    latest: dict[str, LifecycleRecord] = {}
    for row in rows:
        latest.setdefault(row.source_id, row)
    return latest


def persist_complete_snapshot(
    source: str,
    observations: list[SourceObservation],
    *,
    recorded_at: datetime | None = None,
) -> list[LifecycleRecord]:
    """Atomically persist one complete source snapshot and lifecycle changes."""
    if any(observation.source != source for observation in observations):
        raise ValueError("all observations must match the snapshot source")

    source_ids = [observation.source_id for observation in observations]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("complete snapshots cannot contain duplicate source identities")

    Base.metadata.create_all(engine)
    now = recorded_at or datetime.now(timezone.utc)

    with SessionLocal() as session:
        try:
            previous = _latest_states(session, source)

            observation_records: list[ObservationRecord] = []
            for observation in observations:
                record = _build_record(session, observation)
                session.add(record)
                observation_records.append(record)

            # Allocate observation IDs before lifecycle rows reference them.
            session.flush()

            current_by_id = {
                observation.source_id: observation for observation in observations
            }
            persisted_by_source_id = {
                record.source_id: record for record in observation_records
            }
            transitions: list[LifecycleRecord] = []

            for source_id, observation in current_by_id.items():
                prior = previous.get(source_id)
                if prior is None:
                    transition = "new"
                elif prior.state == "disappeared":
                    transition = "reappeared"
                else:
                    continue

                transitions.append(
                    LifecycleRecord(
                        source=source,
                        source_id=source_id,
                        canonical_key=observation.canonical_key,
                        entity_type=observation.entity_type,
                        recorded_at=now,
                        state="present",
                        transition=transition,
                        observation_id=persisted_by_source_id[source_id].id,
                    )
                )

            for source_id, prior in previous.items():
                if prior.state != "present" or source_id in current_by_id:
                    continue

                transitions.append(
                    LifecycleRecord(
                        source=source,
                        source_id=source_id,
                        canonical_key=prior.canonical_key,
                        entity_type=prior.entity_type,
                        recorded_at=now,
                        state="disappeared",
                        transition="disappeared",
                        observation_id=None,
                    )
                )

            session.add_all(transitions)
            session.commit()
        except Exception:
            session.rollback()
            raise

        for record in transitions:
            session.refresh(record)
        return transitions


def current_lifecycle(source: str | None = None) -> list[LifecycleRecord]:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        stmt = select(LifecycleRecord)
        if source is not None:
            stmt = stmt.where(LifecycleRecord.source == source)

        rows = list(
            session.scalars(
                stmt.order_by(
                    LifecycleRecord.source,
                    LifecycleRecord.source_id,
                    desc(LifecycleRecord.recorded_at),
                    desc(LifecycleRecord.id),
                )
            )
        )

    latest: dict[tuple[str, str], LifecycleRecord] = {}
    for row in rows:
        latest.setdefault((row.source, row.source_id), row)
    return list(latest.values())
