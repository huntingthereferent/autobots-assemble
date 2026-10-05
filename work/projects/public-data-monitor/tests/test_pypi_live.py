from app.github_source import fetch_repository
from app.identity import link_github_repo_to_package
from app.pypi_source import fetch_project


def test_live_pypi_and_github_identity_has_explicit_evidence():
    github = fetch_repository()[0]
    package = fetch_project()[0]

    decision = link_github_repo_to_package(github, package)

    assert package.payload["name"].lower() == "requests"
    assert decision.matched is True
    assert any(item.kind == "explicit_project_url" for item in decision.evidence)
