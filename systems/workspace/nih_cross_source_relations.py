"""Cross-source comparison without inventing temporal study revision evidence.

Live pathway independently verifies (1) the whole 2023 archived AACT table,
(2) a separate official current registry record, and (3) all four SHA-pinned
TrialTrace derived-history tables. A common study ID only licenses comparison
of *values*, never attribution of a dated AACT status to a particular
ClinicalTrials.gov version. Result records explicit support/ambiguity instead
of asserting a clinical change or time.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from . import nih_aact_archival_source as aact
from . import nih_derived_history_receipt as derived

SCHEMA = "nih-p2-three-source-observation-relations/v1"
STUDY = "NCT04153409"


def _bounded_status(value):
    if type(value) is not str or not 1 <= len(value) <= 80:
        raise ValueError("exact nonempty bounded source status required")
    return value


def _normal(value):
    # Equality of enumerated spellings only, not interpretation of meaning.
    return _bounded_status(value).strip().upper().replace(" ", "_")


def compare(aact_report, derived_report, *, target=STUDY):
    if target != STUDY:
        raise ValueError("only a predeclared overlapping source identity allowed")
    if (aact_report.get("schema") != aact.SCHEMA or
            aact_report.get("entire_archive_verified_md5") != aact.ARCHIVE_MD5 or
            aact_report.get("entire_archive_sha256") !=
            "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49" or
            aact_report.get("archive_published_on") != "2023-10-31" or
            aact_report.get("case_count") != 2 or
            aact_report.get("exact_per_study_version_number_proven") is not False or
            aact_report.get("original_workstation_modified") is not False):
        raise ValueError("the exact independently witnessed archival source is missing")
    if (derived_report.get("schema") != derived.SCHEMA or
            derived_report.get("upstream_commit") != derived.UPSTREAM_COMMIT or
            derived_report.get("source_sha256") != derived.EXPECTED_SHA256 or
            derived_report.get("original_historical_payloads_available") is not False or
            derived_report.get("individual_public_posting_dates_established") is not False or
            derived_report.get("derived_corpus_is_second_archival_snapshot") is not False or
            derived_report.get("original_twelve_job_workstation_modified") is not False or
            derived_report.get("nct_id") != target):
        raise ValueError("independent derived-source boundary not established")
    if type(aact_report.get("cases")) is not list or len(aact_report["cases"]) != 2:
        raise ValueError("archival study rows are absent")
    selected = [v for v in aact_report["cases"] if v.get("nct_id") == target]
    if len(selected) != 1:
        raise ValueError("historical study ID is missing or duplicated")
    archived = selected[0]
    archive_status = _bounded_status(archived.get("archive_2023_overall_status"))
    observed_now = _bounded_status(archived.get("current_observed_overall_status"))
    if (archived.get("status_values_differ") is not (archive_status != observed_now)
            or not isinstance(archived.get("official_current_response_sha256"), str)
            or len(archived["official_current_response_sha256"]) != 64):
        raise ValueError("current official study observation receipt inconsistent")
    history = derived_report.get("derived_transitions")
    if type(history) is not list or len(history) != derived_report.get("derived_transition_count"):
        raise ValueError("upstream history transitions malformed")
    if len(history) == 0 or len(history) > 100:
        raise ValueError("bounded source history required")
    if len({v.get("version") for v in history}) != len(history):
        raise ValueError("duplicate source history version")
    if any(type(v.get("version")) is not int for v in history):
        raise ValueError("source version identifier missing")
    occurrences = []
    for row in history:
        for position in ("before", "after"):
            value = row.get(position + "_overall_status_as_derived")
            if value is None:
                continue
            value = _bounded_status(value)
            occurrences.append({
                "version_claimed_by_upstream": row["version"],
                "position": position,
                "status_value_as_derived": value,
                "matches_2023_snapshot_spelling": _normal(value) == _normal(archive_status),
                "matches_current_official_spelling": _normal(value) == _normal(observed_now),
                "version_date_as_derived": row.get("version_date_as_derived"),
                "public_posting_of_this_version_independently_verified": False,
            })
    if not occurrences:
        raise ValueError("derived history has no status observations")
    matches_2023 = [x for x in occurrences if x["matches_2023_snapshot_spelling"]]
    matches_current = [x for x in occurrences if x["matches_current_official_spelling"]]
    return {
        "schema": SCHEMA,
        "nct_id": target,
        "observations": [
            {
                "source": "published-third-party-2023-aact-table",
                "value": archive_status,
                "release_date_bound": aact_report["archive_published_on"],
                "underlying_collection_date": None,
                "original_study_version": None,
            },
            {
                "source": "official-current-registry-api-v2",
                "value": observed_now,
                "retrieved_at_utc": aact_report["retrieved_at_utc"],
                "exact_response_sha256": archived["official_current_response_sha256"],
                "original_study_version": None,
            },
        ],
        "derived_history_status_occurrences": occurrences,
        "spelling_matches": {
            "historical_2023_to_derived_count": len(matches_2023),
            "current_to_derived_count": len(matches_current),
        },
        "current_status_differs_from_archived": archive_status != observed_now,
        "historical_status_corresponds_to_unique_version": False,
        "source_identity_equivalence_only": True,
        "historical_record_contents_independently_authenticated": False,
        "public_posting_time_of_change_known": False,
        "clinical_event_time_known": False,
        "two_independent_original_historical_snapshots_available": False,
        "source_archival_sha256": aact_report["entire_archive_sha256"],
        "derived_source_file_sha256": derived_report["source_sha256"],
        "upstream_derived_corpus_author": derived_report["upstream_author"],
        "upstream_derived_data_license": derived_report["upstream_data_license"],
        "original_twelve_job_workstation_modified": False,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
    }


def execute(*, output_dir, aact_runner=aact.execute, derived_runner=derived.execute,
            now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset().total_seconds() != 0:
        raise ValueError("UTC observation required")
    output_dir = Path(output_dir)
    aact_result = aact_runner(output_dir=output_dir / "aact", now=now)
    derived_result = derived_runner(output_dir=output_dir / "derived", now=now)
    report = compare(aact_result, derived_result)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "nih-p2-cross-source-relations.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    opts = p.parse_args(argv)
    result = execute(output_dir=opts.output_dir)
    print(json.dumps({
        "schema": result["schema"], "nct_id": result["nct_id"],
        "derived_status_occurrences": len(result["derived_history_status_occurrences"]),
        "spelling_matches": result["spelling_matches"],
        "independent_historical_version_time_proven": False,
        "clinical_verdict": "NOT_EVALUATED",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
