from datetime import datetime, timezone

import httpx

from .platform import SourceObservation

GITHUB_REPO = "psf/requests"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"


def fetch_repository(client: httpx.Client | None = None) -> list[SourceObservation]:
    owns_client = client is None
    client = client or httpx.Client(timeout=15, follow_redirects=True)
    observed_at = datetime.now(timezone.utc)

    try:
        response = client.get(
            GITHUB_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "state-reconciliation-platform/0.2",
            },
        )
        response.raise_for_status()
        repo = response.json()

        return [
            SourceObservation(
                source="github_api",
                source_id=str(repo["id"]),
                observed_at=observed_at,
                source_updated_at=datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00")),
                source_url=repo["html_url"],
                entity_type="repository",
                canonical_key=f"github_repo:{repo['id']}",
                payload={
                    "full_name": repo["full_name"],
                    "default_branch": repo["default_branch"],
                    "stargazers_count": repo["stargazers_count"],
                    "forks_count": repo["forks_count"],
                    "open_issues_count": repo["open_issues_count"],
                    "pushed_at": repo["pushed_at"],
                    "archived": repo["archived"],
                },
            )
        ]
    finally:
        if owns_client:
            client.close()
