import httpx

from app.github_source import fetch_repository


def test_github_repository_adapter_emits_canonical_observation():
    payload = {
        "id": 1362490,
        "full_name": "psf/requests",
        "default_branch": "main",
        "stargazers_count": 53000,
        "forks_count": 9500,
        "open_issues_count": 400,
        "updated_at": "2026-10-05T12:00:00Z",
        "pushed_at": "2026-10-05T11:00:00Z",
        "html_url": "https://github.com/psf/requests",
        "archived": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = fetch_repository(client)

    assert len(rows) == 1
    row = rows[0]
    assert row.source == "github_api"
    assert row.source_id == "1362490"
    assert row.canonical_key == "github_repo:1362490"
    assert row.payload["full_name"] == "psf/requests"
    assert row.payload["default_branch"] == "main"
