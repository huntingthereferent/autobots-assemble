from datetime import datetime, timezone

from sqlalchemy import desc, select

from .db import Base, SessionLocal, engine
from .identity import IdentityDecision
from .identity_models import IdentityDecisionRecord
from .metrics import IDENTITY_DECISIONS


def persist_identity_decision(
    decision: IdentityDecision,
    *,
    threshold: int,
) -> IdentityDecisionRecord:
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        record = IdentityDecisionRecord(
            decided_at=datetime.now(timezone.utc),
            left_key=decision.left_key,
            right_key=decision.right_key,
            score=decision.score,
            threshold=threshold,
            matched=decision.matched,
            evidence=[
                {
                    "kind": item.kind,
                    "value": item.value,
                    "weight": item.weight,
                }
                for item in decision.evidence
            ],
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        IDENTITY_DECISIONS.labels(matched=str(decision.matched).lower()).inc()
        return record


def latest_identity_decisions(limit: int = 100) -> list[IdentityDecisionRecord]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(IdentityDecisionRecord)
                .order_by(
                    desc(IdentityDecisionRecord.decided_at),
                    desc(IdentityDecisionRecord.id),
                )
                .limit(limit)
            )
        )
