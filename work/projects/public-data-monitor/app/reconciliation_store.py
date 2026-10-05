from datetime import datetime, timezone

from sqlalchemy import desc, select

from .db import Base, SessionLocal, engine
from .history_models import ReconciliationRecord
from .platform import SourceObservation, reconcile


def persist_reconciliation(observations: list[SourceObservation]) -> ReconciliationRecord:
    Base.metadata.create_all(engine)
    result = reconcile(observations)

    with SessionLocal() as session:
        record = ReconciliationRecord(
            canonical_key=result.canonical_key,
            reconciled_at=datetime.now(timezone.utc),
            status=result.status.value,
            sources=result.sources,
            conflicting_fields=result.conflicting_fields,
            selected_payload=result.selected_payload,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def latest_reconciliation(canonical_key: str) -> ReconciliationRecord | None:
    with SessionLocal() as session:
        return session.scalar(
            select(ReconciliationRecord)
            .where(ReconciliationRecord.canonical_key == canonical_key)
            .order_by(desc(ReconciliationRecord.reconciled_at), desc(ReconciliationRecord.id))
            .limit(1)
        )
