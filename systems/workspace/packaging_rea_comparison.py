"""Compare real source-owned release requirements with general packaging relations.

This adapter inspects the existing A/B release contract; it does not claim
that an REA release has been run in this branch.
"""
from __future__ import annotations

from pathlib import Path
from .packaging_harness import PackagingReferent, PackagingPlan, admit


REA_RELEASE_RELATIONS = (
    "original source identity preserved",
    "source code rights separated from product rights",
    "native execution evidence bound to original logs",
    "package members and digests declared",
    "destination distribution is independently readable",
)

REA_NATIVE_WITNESSES = (
    "source-stage-receipt",
    "native-rea-tests",
    "rea-typecheck",
    "source-diff-check",
    "paired-reference-comparison",
    "release-archive-inspection",
)


def inspect_rea_release_source(source: str | Path) -> dict:
    """Observe actual release.py text, without executing it or inventing PASS."""
    path = Path(source)
    text = path.read_text(encoding="utf-8")
    requirements = {
        "source pin": 'upstream_commit") != PIN',
        "source native": 'NATIVE_LOGS',
        "rights": '_archive_license',
        "reference comparison": 'validate_reference_comparison',
        "member digests": '"sha256": _hash(src)',
        "release manifest": '"release-manifest.json"',
    }
    missing = tuple(name for name, marker in requirements.items() if marker not in text)
    return {
        "representation": "REA release source and evidence relations",
        "operations": ("validate source receipts", "assemble release", "inspect archive"),
        "outputs": ("A/B release candidate",),
        "witnesses": REA_NATIVE_WITNESSES,
        "unresolved": missing + (
            "execute native REA source and record fresh receipts",
            "independently inspect actual release archive",
        ),
    }


def plan_rea_comparison(source: str | Path) -> PackagingPlan:
    referent = PackagingReferent(
        "A/B REA source release",
        (str(source),),
        REA_RELEASE_RELATIONS,
        ("do not redistribute upstream source", "preserve independent licensing"),
    )
    return admit(referent, inspect=lambda _: inspect_rea_release_source(source))
