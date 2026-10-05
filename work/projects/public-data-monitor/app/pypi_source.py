from datetime import datetime, timezone

import httpx

from .platform import SourceObservation

PYPI_PROJECT = "requests"
PYPI_API = f"https://pypi.org/pypi/{PYPI_PROJECT}/json"


def fetch_project(client: httpx.Client | None = None) -> list[SourceObservation]:
    owns_client = client is None
    client = client or httpx.Client(timeout=15, follow_redirects=True)
    observed_at = datetime.now(timezone.utc)

    try:
        response = client.get(
            PYPI_API,
            headers={"User-Agent": "state-reconciliation-platform/0.3"},
        )
        response.raise_for_status()
        payload = response.json()
        info = payload["info"]

        project_urls = info.get("project_urls") or {}
        return [
            SourceObservation(
                source="pypi_api",
                source_id=info["name"].lower(),
                observed_at=observed_at,
                source_url=f"https://pypi.org/project/{info['name']}/",
                entity_type="package",
                canonical_key=f"pypi_package:{info['name'].lower()}",
                payload={
                    "name": info["name"],
                    "version": info["version"],
                    "summary": info.get("summary"),
                    "home_page": info.get("home_page"),
                    "project_urls": project_urls,
                    "requires_python": info.get("requires_python"),
                },
            )
        ]
    finally:
        if owns_client:
            client.close()
