from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .run_models import SourceRun

router = APIRouter(prefix="/api/ops", tags=["operations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/source-runs")
def source_runs(
    source: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(SourceRun)
    if source is not None:
        stmt = stmt.where(SourceRun.source == source)

    rows = list(
        db.scalars(
            stmt.order_by(desc(SourceRun.started_at), desc(SourceRun.id)).limit(limit)
        )
    )

    return [
        {
            "id": row.id,
            "source": row.source,
            "task_id": row.task_id,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
            "status": row.status,
            "items_seen": row.items_seen,
            "error_type": row.error_type,
            "error_message": row.error_message,
        }
        for row in rows
    ]
