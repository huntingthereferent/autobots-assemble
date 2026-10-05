from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from .platform import SourceObservation


@dataclass(frozen=True)
class IdentityEvidence:
    kind: str
    value: str
    weight: int


@dataclass(frozen=True)
class IdentityDecision:
    left_key: str
    right_key: str
    score: int
    matched: bool
    evidence: tuple[IdentityEvidence, ...]


def _normalize_github_repo_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value.strip())
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0].lower(), parts[1].lower()
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"github.com/{owner}/{repo}"


def _urls_from_package(observation: SourceObservation) -> set[str]:
    values: list[str | None] = [observation.payload.get("home_page")]
    project_urls = observation.payload.get("project_urls") or {}
    if isinstance(project_urls, dict):
        values.extend(project_urls.values())
    return {
        normalized
        for value in values
        if isinstance(value, str)
        if (normalized := _normalize_github_repo_url(value)) is not None
    }


def link_github_repo_to_package(
    github: SourceObservation,
    package: SourceObservation,
    *,
    threshold: int = 100,
) -> IdentityDecision:
    evidence: list[IdentityEvidence] = []

    github_url = _normalize_github_repo_url(github.source_url)
    package_urls = _urls_from_package(package)

    if github_url and github_url in package_urls:
        evidence.append(
            IdentityEvidence(
                kind="explicit_project_url",
                value=github_url,
                weight=100,
            )
        )

    repo_name = str(github.payload.get("full_name", "")).split("/")[-1].lower()
    package_name = str(package.payload.get("name", "")).lower()
    if repo_name and package_name and repo_name == package_name:
        evidence.append(
            IdentityEvidence(
                kind="normalized_name",
                value=repo_name,
                weight=20,
            )
        )

    score = sum(item.weight for item in evidence)
    return IdentityDecision(
        left_key=github.canonical_key,
        right_key=package.canonical_key,
        score=score,
        matched=score >= threshold,
        evidence=tuple(evidence),
    )
