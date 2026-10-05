from datetime import datetime, timezone

import pytest

from app.platform import (
    ChangeKind,
    ReconciliationStatus,
    SourceObservation,
    classify_change,
    reconcile,
)


NOW = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)


def obs(source: str, payload: dict, key: str = "entity:1") -> SourceObservation:
    return SourceObservation(
        source=source,
        source_id=f"{source}-1",
        observed_at=NOW,
        entity_type="example",
        canonical_key=key,
        payload=payload,
    )


def test_change_classification_covers_new_unchanged_changed_and_disappeared():
    current = obs("a", {"value": 1, "name": "x"})

    assert classify_change(None, current).kind == ChangeKind.NEW
    assert classify_change(current, current).kind == ChangeKind.UNCHANGED

    changed = classify_change(current, obs("a", {"value": 2, "name": "x"}))
    assert changed.kind == ChangeKind.CHANGED
    assert changed.changed_fields == ["value"]

    assert classify_change(current, None).kind == ChangeKind.DISAPPEARED


def test_reconciliation_distinguishes_agreement_from_conflict():
    a = obs("api", {"value": 10, "status": "open"})
    b = obs("html", {"value": 10, "status": "open"})

    agreed = reconcile([a, b])
    assert agreed.status == ReconciliationStatus.AGREEMENT
    assert agreed.selected_payload == a.payload

    conflict = reconcile([a, obs("html", {"value": 11, "status": "open"})])
    assert conflict.status == ReconciliationStatus.CONFLICT
    assert conflict.conflicting_fields == ["value"]
    assert conflict.selected_payload is None


def test_reconciliation_rejects_mixed_identity():
    with pytest.raises(ValueError):
        reconcile([
            obs("api", {"value": 1}, key="entity:1"),
            obs("html", {"value": 1}, key="entity:2"),
        ])
