from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.identity import link_github_repo_to_package
from app.identity_models import IdentityDecisionRecord
from app.identity_store import persist_identity_decision
from app.main import app
from app.platform import SourceObservation


NOW = datetime(2026, 10, 5, 13, 0, tzinfo=timezone.utc)


def test_identity_decision_persists_evidence_and_is_queryable():
    Base.metadata.create_all(engine)

    github = SourceObservation(
        source="github_api",
        source_id="1362490",
        observed_at=NOW,
        source_url="https://github.com/psf/requests",
        entity_type="repository",
        canonical_key="github_repo:1362490",
        payload={"full_name": "psf/requests"},
    )
    package = SourceObservation(
        source="pypi_api",
        source_id="requests",
        observed_at=NOW,
        source_url="https://pypi.org/project/requests/",
        entity_type="package",
        canonical_key="pypi_package:requests",
        payload={
            "name": "requests",
            "project_urls": {"Source": "https://github.com/psf/requests"},
        },
    )

    decision = link_github_repo_to_package(github, package)
    record = persist_identity_decision(decision, threshold=100)

    with SessionLocal() as session:
        stored = session.get(IdentityDecisionRecord, record.id)

    assert stored is not None
    assert stored.matched is True
    assert stored.score == 120
    assert [item["kind"] for item in stored.evidence] == [
        "explicit_project_url",
        "normalized_name",
    ]

    client = TestClient(app)
    response = client.get("/api/identity/decisions?matched=true&limit=10")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["id"] == record.id for item in payload)
