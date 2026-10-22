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


def independently_replay_reported_clock(report):
    """Read-only source date ordering oracle; never authenticate first-public time."""
    from datetime import date
    if type(report) is not dict:
        raise ValueError("source clock report missing")
    rows=report.get("original_source_version_observations")
    tests=report.get("conditional_registry_publication_queries")
    if (type(rows) is not list or len(rows)!=2 or
        type(tests) is not list or len(tests)!=len(parent.CUTOFFS)):
        raise ValueError("original source cutoff series missing")
    if [r.get("source_version") for r in rows]!=list(ALLOWED_VERSIONS):
        raise ValueError("source version order changed")
    dates=[]
    for row in rows:
        raw=row.get("source_reported_posted_date")
        if not isinstance(raw,str) or date.fromisoformat(raw).isoformat()!=raw:
            raise ValueError("noncanonical source reported posting date")
        dates.append(raw)
        if not row.get("observed_recorded_status"):
            raise ValueError("missing original source version status")
    if dates!=sorted(dates):
        raise ValueError("source reported version dates reversed")
    for cutoff,case in zip(parent.CUTOFFS,tests):
        visible=[r for r in rows if r["source_reported_posted_date"]<=cutoff]
        chosen=visible[-1] if visible else None
        withheld=[r["source_version"] for r in rows if r not in visible]
        expected={
            "source_reported_cutoff":cutoff,
            "conditional_visible_registry_version":chosen["source_version"] if chosen else None,
            "conditional_recorded_status":chosen["observed_recorded_status"] if chosen else "UNAVAILABLE",
            "source_versions_withheld_under_assumption":withheld,
            "static_latest_source_version":260,
            "static_latest_record_status":rows[-1]["observed_recorded_status"],
            "static_latest_leaks_future_source_version":260 in withheld,
            "original_version_first_public_authentication":"UNAVAILABLE",
            "clinical_valid_at":"UNAVAILABLE",
        }
        if type(case) is not dict or any(case.get(key)!=value for key,value in expected.items()):
            raise ValueError("original reported clock query diverges from independent date oracle")
        if case.get("static_union_contains_both_record_statuses") is not True:
            raise ValueError("source static-version boundary altered")
    return {
        "independent_source_reported_clock_cutoffs_verified":len(tests),
        "source_reported_cutoff_mismatch_count":0,
        "first_public_transaction_independently_observed":False,
        "reported_clock_is_not_clinical_validity":True,
    }


def attested_archive_reported_post_date_gaps(report):
    """B3 conditional calendar offsets, NOT an independently witnessed public clock."""
    from datetime import date
    rows=report.get("original_source_version_observations")
    owners=report.get("independent_aact_owner_attested_archive_checks")
    if type(rows) is not list or type(owners) is not list or len(rows)!=2 or len(owners)!=2:
        raise ValueError("two original version/archive pairs required")
    comparisons=[]
    for record,archive in zip(rows,owners):
        posted=record.get("source_reported_posted_date")
        attested=archive.get("owner_attested_collection_day")
        if not isinstance(posted,str) or not isinstance(attested,str):
            raise ValueError("original reported/attested date pair missing")
        delta=(date.fromisoformat(attested)-date.fromisoformat(posted)).days
        if delta<0:
            raise ValueError("claimed archive collection precedes source-reported post")
        if archive.get("original_archive_is_time_authority") is not False:
            raise ValueError("unverified archive date promoted to temporal authority")
        comparisons.append({
            "registry_version":record["source_version"],
            "source_reported_posted_date":posted,
            "archive_owner_claimed_collection_day":attested,
            "claimed_archive_minus_reported_post_days":delta,
            "first_public_transaction_independently_verified":False,
        })
    return {
        "conditional_owner_claim_calendar_gaps":comparisons,
        "verified_first_public_date_window": "UNAVAILABLE",
        "owner_claim_lag_is_not_publication_delay":True,
        "clinical_valid_time_proven":False,
    }


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
    source_clock_check=independently_replay_reported_clock(report)
    claim_gaps=attested_archive_reported_post_date_gaps(report)
    return {
        **source_clock_check,
        **claim_gaps,
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
