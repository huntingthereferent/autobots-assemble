from fastapi import APIRouter, Query

from .lifecycle_store import current_lifecycle

router = APIRouter(prefix="/api/lifecycle", tags=["lifecycle"])


@router.get("")
def lifecycle(
    source: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = sorted(
        current_lifecycle(source),
        key=lambda row: (row.recorded_at, row.id),
        reverse=True,
    )[:limit]

    return [
        {
            "id": row.id,
            "source": row.source,
            "source_id": row.source_id,
            "canonical_key": row.canonical_key,
            "entity_type": row.entity_type,
            "recorded_at": row.recorded_at,
            "state": row.state,
            "transition": row.transition,
            "observation_id": row.observation_id,
        }
        for row in rows
    ]
