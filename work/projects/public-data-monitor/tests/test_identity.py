from datetime import datetime, timezone

from app.identity import link_github_repo_to_package
from app.platform import SourceObservation


NOW = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)


def github(url="https://github.com/psf/requests"):
    return SourceObservation(
        source="github_api",
        source_id="1362490",
        observed_at=NOW,
        source_url=url,
        entity_type="repository",
        canonical_key="github_repo:1362490",
        payload={"full_name": "psf/requests"},
    )


def package(project_urls=None, name="requests"):
    return SourceObservation(
        source="pypi_api",
        source_id=name,
        observed_at=NOW,
        source_url=f"https://pypi.org/project/{name}/",
        entity_type="package",
        canonical_key=f"pypi_package:{name}",
        payload={
            "name": name,
            "home_page": None,
            "project_urls": project_urls or {},
        },
    )


def test_explicit_cross_system_project_url_is_strong_identity_evidence():
    decision = link_github_repo_to_package(
        github(),
        package({"Source": "https://github.com/psf/requests"}),
    )

    assert decision.matched is True
    assert decision.score == 120
    assert [item.kind for item in decision.evidence] == [
        "explicit_project_url",
        "normalized_name",
    ]


def test_name_alone_does_not_establish_cross_system_identity():
    decision = link_github_repo_to_package(github(), package())

    assert decision.score == 20
    assert decision.matched is False


def test_conflicting_repository_url_blocks_match_even_when_names_agree():
    decision = link_github_repo_to_package(
        github(),
        package({"Source": "https://github.com/someone-else/requests"}),
    )

    assert decision.score == 20
    assert decision.matched is False
