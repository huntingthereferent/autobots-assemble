from app.github_source import fetch_repository


def test_live_github_repository_source():
    rows = fetch_repository()

    assert len(rows) == 1
    row = rows[0]
    assert row.source == "github_api"
    assert row.payload["full_name"] == "psf/requests"
    assert row.source_url == "https://github.com/psf/requests"
    assert row.payload["stargazers_count"] >= 1
