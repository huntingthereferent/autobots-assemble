"""Separate first-public witness admission audit for original NIH P2 registry versions.

No original historical exact-version first-public transaction is authenticated
by the known sources. This finite read-only gate refuses to replace missing
evidence with Last Update Posted, owner-attested archive dates or 2026 reads.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import json

from . import nih_p2_two_original_source_clocks as parent

SCHEMA = "nih-p2-original-historical-version-publication-admission-v1"
ALLOWED_VERSIONS = (259, 260)


def inspect_source_clock(report, *, independent_release_evidence=None):
    if type(report) is not dict or report.get("schema") != parent.SCHEMA:
        raise ValueError("only exact independently source-authenticated predecessor")
    if independent_release_evidence is not None:
        # An arbitrary JSON claim is not an authentic independent observation.
        # A future separate owner-native verifier would have to admit original
        # version-specific release evidence, with byte hashes and provenance.
        raise ValueError("no independent exact-version first-public verifier admitted")
    if any(report.get(k) is not False for k in (
        "real_as_known_at_independently_authenticated",
        "real_clinical_valid_at_known",
        "historical_NIH_P2_benchmark_completed",
        "original_W13_journal_modified",
    )):
        raise ValueError("conditional original-source clock promoted to unsupported proof")
    rows = report.get("original_source_version_observations")
    if (type(rows) is not list or len(rows) != 2 or
            tuple(r.get("source_version") for r in rows) != ALLOWED_VERSIONS):
        raise ValueError("source versions missing/altered")
    for r in rows:
        if (r.get("first_public_version_at") != "UNAVAILABLE" or
                r.get("clinical_valid_at") != "UNAVAILABLE" or
                not r.get("source_reported_posted_date") or
                not r.get("original_version_source_url") or
                not r.get("source_retrieved_utc")):
            raise ValueError("missing original-source evidence or falsified availability")
    if report.get("conditional_assumption") != "source-reported-last-update-posted-only":
        raise ValueError("original conditional publication semantics changed")
    controls = report.get("independent_aact_owner_attested_archive_checks")
    if (type(controls) is not list or len(controls) != 2 or
            any(c.get("original_archive_is_time_authority") is not False
                for c in controls)):
        raise ValueError("archive extraction date promoted to independent first-public evidence")
    return {
        "schema": SCHEMA,
        "source_predecessor_schema": parent.SCHEMA,
        "original_record_versions": [r["source_version"] for r in rows],
        "source_reported_posted_dates": [r["source_reported_posted_date"] for r in rows],
        "source_owner_collection_date_is_first_public_witness": False,
        "source_reported_posted_is_independent_first_public_witness": False,
        "2026_retrieval_is_original_2022_first_public_witness": False,
        "actual_clinical_valid_at": "UNAVAILABLE",
        "independent_exact_version_first_public_at": "UNAVAILABLE",
        "real_historical_as_known_at_admission": "REFUSED_MISSING_INDEPENDENT_WITNESS",
        "registry_observation_only": True,
        "conditional_source_clock_query_count": len(
            report.get("conditional_registry_publication_queries", ())),
        "independent_source_owners_verified_by_parent": True,
        "original_W13_modified": False,
        "official_NIH_benchmark": False,
    }


def execute(registry_raw, aact_raw):
    # Source admission executes the original pinned-byte verifier again here,
    # not an unauthenticated JSON handoff or a fabricated 2022 source event.
    actual = parent.observe(registry_raw, aact_raw)
    return inspect_source_clock(actual)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",required=True,type=Path)
    p.add_argument("--aact",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    x=p.parse_args()
    result=execute(x.registry.read_bytes(),x.aact.read_bytes())
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "record_versions":result["original_record_versions"],
        "actual_first_public":result["independent_exact_version_first_public_at"],
        "admission":result["real_historical_as_known_at_admission"],
        "NIH_complete":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
