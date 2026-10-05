from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .history_models import ObservationRecord, ReconciliationRecord

router = APIRouter(prefix="/api", tags=["history"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/history/{canonical_key:path}")
def history(
    canonical_key: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = list(
        db.scalars(
            select(ObservationRecord)
            .where(ObservationRecord.canonical_key == canonical_key)
            .order_by(desc(ObservationRecord.observed_at), desc(ObservationRecord.id))
            .limit(limit)
        )
    )
    return [
        {
            "id": row.id,
            "source": row.source,
            "source_id": row.source_id,
            "canonical_key": row.canonical_key,
            "entity_type": row.entity_type,
            "observed_at": row.observed_at,
            "payload": row.payload,
            "change_kind": row.change_kind,
            "changed_fields": row.changed_fields,
        }
        for row in rows
    ]


@router.get("/reconciliations/{canonical_key:path}")
def reconciliations(
    canonical_key: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = list(
        db.scalars(
            select(ReconciliationRecord)
            .where(ReconciliationRecord.canonical_key == canonical_key)
            .order_by(desc(ReconciliationRecord.reconciled_at), desc(ReconciliationRecord.id))
            .limit(limit)
        )
    )
    return [
        {
            "id": row.id,
            "canonical_key": row.canonical_key,
            "reconciled_at": row.reconciled_at,
            "status": row.status,
            "sources": row.sources,
            "conflicting_fields": row.conflicting_fields,
            "selected_payload": row.selected_payload,
        }
        for row in rows
    ]
