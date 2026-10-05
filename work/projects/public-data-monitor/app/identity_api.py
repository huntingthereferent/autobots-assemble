from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .identity_models import IdentityDecisionRecord

router = APIRouter(prefix="/api/identity", tags=["identity"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/decisions")
def decisions(
    matched: bool | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(IdentityDecisionRecord)
    if matched is not None:
        stmt = stmt.where(IdentityDecisionRecord.matched == matched)

    rows = list(
        db.scalars(
            stmt.order_by(
                desc(IdentityDecisionRecord.decided_at),
                desc(IdentityDecisionRecord.id),
            ).limit(limit)
        )
    )

    return [
        {
            "id": row.id,
            "decided_at": row.decided_at,
            "left_key": row.left_key,
            "right_key": row.right_key,
            "score": row.score,
            "threshold": row.threshold,
            "matched": row.matched,
            "evidence": row.evidence,
        }
        for row in rows
    ]
