from sqlalchemy import desc, select

from .db import Base, SessionLocal, engine
from .history_models import ObservationRecord
from .platform import SourceObservation, classify_change


def persist_observation(observation: SourceObservation) -> ObservationRecord:
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        previous = session.scalar(
            select(ObservationRecord)
            .where(
                ObservationRecord.source == observation.source,
                ObservationRecord.source_id == observation.source_id,
            )
            .order_by(desc(ObservationRecord.observed_at), desc(ObservationRecord.id))
            .limit(1)
        )

        previous_observation = None
        if previous is not None:
            previous_observation = SourceObservation(
                source=previous.source,
                source_id=previous.source_id,
                observed_at=previous.observed_at,
                source_updated_at=previous.source_updated_at,
                source_url=previous.source_url,
                entity_type=previous.entity_type,
                canonical_key=previous.canonical_key,
                payload=previous.payload,
            )

        change = classify_change(previous_observation, observation)

        record = ObservationRecord(
            source=observation.source,
            source_id=observation.source_id,
            canonical_key=observation.canonical_key,
            entity_type=observation.entity_type,
            observed_at=observation.observed_at,
            source_updated_at=observation.source_updated_at,
            source_url=observation.source_url,
            payload=observation.payload,
            change_kind=change.kind.value,
            changed_fields=change.changed_fields,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
