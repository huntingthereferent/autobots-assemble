"""Carry two verified original registry-version observations across a bounded source clock.

Not a new general engine or a real-world clinical reasoner. The existing
original W13 temporal Python remains synthetic-only. This adapter separately
observes source-reported posting times, 2026 retrieval, and source-owner
attested archive collection. It does not infer a clinical validity time or
independently authenticated original-version first-public timestamp.

Input evidence is two already-successful original GitHub Actions artifacts,
verified byte-for-byte by SHA-256 before field inspection.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path

from . import nih_p2_source_reported_posting_gate as original

SCHEMA = "nih-p2-two-original-source-clocks-independent-archive-oracle/v1"
REGISTRY_JSON_SHA256 = "9adf3d0419b89a8c098b97b61bbfec874d5833b69bdf0fced213628188ad5540"
AACT_JSON_SHA256 = "549d7cc2343c49818f54eeba8ce5c4ee3a8b44f84cf796d6361702d2e6c81e2e"
AACT_RUN = 39424382213
AACT_ARTIFACT = 12265565989
AACT_ZIP_SHA256 = "cb992832cb89dde44f09f88ceeb985532ab2516458d016617a4429fc410ee1d9"
SOURCE_ID = "NCT00001756"
CUTOFFS = (
    "2022-10-26", "2022-10-27", "2022-11-04",
    "2022-11-06", "2022-11-07", "2022-11-09",
)
EXPECTED_VERSIONS = (259, 260)
EXPECTED_OWNERS = ("2022-11-04", "2022-11-09")


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _date(value: str) -> str:
    if type(value) is not str or len(value) != 10:
        raise ValueError("expected source date")
    if date.fromisoformat(value).isoformat() != value:
        raise ValueError("invalid source calendar date")
    return value


def admit(registry_raw: bytes, aact_raw: bytes) -> tuple[list[dict], dict]:
    if type(registry_raw) is not bytes or _sha(registry_raw) != REGISTRY_JSON_SHA256:
        raise ValueError("original V259/V260 source JSON not byte-authenticated")
    if type(aact_raw) is not bytes or _sha(aact_raw) != AACT_JSON_SHA256:
        raise ValueError("independent deposited AACT comparison JSON not byte-authenticated")
    registry = original.authenticate_receipt(registry_raw)
    report = json.loads(aact_raw)
    if (
        report.get("schema") != "nih-p2-adjacent-original-cross-archive-status-witness/v1"
        or report.get("study") != SOURCE_ID
        or report.get("archived_and_registry_status_correspondence") is not True
        or report.get("archival_status_values_differ") is not True
        or report.get("archive_collection_order_independently_timestamped") is not False
        or report.get("first_public_version_post_times_independently_witnessed") is not False
        or report.get("clinical_event_valid_at_authenticated") is not False
        or report.get("real_historical_W13_query_admitted") is not False
        or report.get("original_twelve_job_runtime_modified") is not False
        or report.get("nih_phase2_completed") is not False
        or report.get("third_party_archive_bodies_published") is not False
    ):
        raise ValueError("AACT report was improperly promoted beyond original evidence")
    sources = report.get("original_archive_sources")
    if type(sources) is not list or len(sources) != 2:
        raise ValueError("missing two external original source owners")
    if ([s.get("owner_attested_collection_date") for s in sources]
            != list(EXPECTED_OWNERS)):
        raise ValueError("external original source-owner collection claims changed")
    if ([s.get("whole_file_sha256") for s in sources]
            != [original_sha for original_sha in (
                "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49",
                "d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755"
            )]):
        raise ValueError("two externally authenticated whole-source identities changed")
    if any(s.get("owner_statement_independently_witnessed_collection_transaction")
           is not False for s in sources):
        raise ValueError("source owner claims promoted to independent 2022 transactions")
    paired = report.get("source_status_comparisons")
    archived = report.get("observed_original_archival_rows")
    if (type(paired) is not list or type(archived) is not list
            or len(paired) != 2 or len(archived) != 2):
        raise ValueError("missing exact two original archive-to-registry comparisons")
    for i, (reg, source_row, compare_row, owner_row) in enumerate(
        zip(registry, archived, paired, sources)
    ):
        version = EXPECTED_VERSIONS[i]
        status = reg["observed_overall_status"]
        posted = reg["observed_version_local_last_update_posted"]
        cutoff = owner_row["owner_attested_collection_date"]
        if (
            reg["version"] != version
            or source_row.get("nct_id") != SOURCE_ID
            or source_row.get("archive_owner_claimed_collection_date") != cutoff
            or source_row.get("overall_status") != status
            or source_row.get("last_update_posted_date") != posted
            or compare_row.get("original_registry_version") != version
            or compare_row.get("original_archive_status") != status
            or compare_row.get("original_registry_version_status") != status
            or compare_row.get("archive_recorded_last_update_posted") != posted
            or compare_row.get("registry_version_local_last_update_posted") != posted
            or compare_row.get("status_matches_original_registry_version") is not True
            or compare_row.get("update_posted_fields_match") is not True
            or compare_row.get("archive_snapshot_is_exact_registry_version") is not False
            or compare_row.get("archive_collection_date_is_registry_version_post_date") is not False
            or _date(posted) > _date(cutoff)
        ):
            raise ValueError("archived independent original study and registry disagree")
    if report.get("registry_version_source") != {
        "run_id": original.ORIGINAL_RUN,
        "artifact_id": original.ORIGINAL_ARTIFACT,
        "artifact_sha256": original.ORIGINAL_ZIP_SHA256,
        "minimal_receipt_sha256": original.PINNED_RECEIPT_SHA256,
    }:
        raise ValueError("prior registry original artifact lineage changed")
    return registry, report


def conditional_source_status(registry: list[dict], day: str) -> dict:
    """Only a source-reported posting-date ordering; NOT clinical as-of fact."""
    cutoff = _date(day)
    if [r.get("version") for r in registry] != list(EXPECTED_VERSIONS):
        raise ValueError("source version order not admitted")
    eligible = [
        r for r in registry
        if _date(r["observed_version_local_last_update_posted"]) <= cutoff
    ]
    chosen = eligible[-1] if eligible else None
    withheld = [r["version"] for r in registry if r not in eligible]
    return {
        "source_reported_cutoff": cutoff,
        "conditional_visible_registry_version": chosen["version"] if chosen else None,
        "conditional_recorded_status": chosen["observed_overall_status"] if chosen
                                       else "UNAVAILABLE",
        "source_versions_withheld_under_assumption": withheld,
        "static_union_contains_both_record_statuses": True,
        "static_latest_source_version": 260,
        "static_latest_record_status": registry[-1]["observed_overall_status"],
        "static_latest_leaks_future_source_version": 260 in withheld,
        "original_version_first_public_authentication": "UNAVAILABLE",
        "clinical_valid_at": "UNAVAILABLE",
    }


def observe(registry_raw: bytes, aact_raw: bytes) -> dict:
    original_versions, original_aact = admit(registry_raw, aact_raw)
    cases = [conditional_source_status(original_versions, d) for d in CUTOFFS]
    archive_rows = original_aact["observed_original_archival_rows"]
    # Independent source-family oracle: each exact archive row is from a
    # separate 525 MB, whole-byte-authenticated depositor original.
    # Its collection date remains owner-ATTESTED, not a verified public clock.
    controls = []
    for snapshot in archive_rows:
        at = snapshot["archive_owner_claimed_collection_date"]
        computed = next(c for c in cases if c["source_reported_cutoff"] == at)
        controls.append({
            "owner_attested_collection_day": at,
            "actual_original_deposited_archive_status": snapshot["overall_status"],
            "source_reported_clock_selected_status": computed["conditional_recorded_status"],
            "source_families_agree_on_recorded_status":
                snapshot["overall_status"] == computed["conditional_recorded_status"],
            "original_archive_is_time_authority": False,
        })
    # A mismatch is a result, not something to repair by modifying source.
    return {
        "schema": SCHEMA,
        "original_registry_artifact": {
            "run_id": original.ORIGINAL_RUN,
            "artifact_id": original.ORIGINAL_ARTIFACT,
            "json_sha256": REGISTRY_JSON_SHA256,
        },
        "independent_aact_artifact": {
            "run_id": AACT_RUN, "artifact_id": AACT_ARTIFACT,
            "zip_sha256": AACT_ZIP_SHA256, "json_sha256": AACT_JSON_SHA256,
        },
        "referent": "original-registry-record-status-source-clock-only",
        "original_source_version_observations": [
            {
                "source_version": r["version"],
                "source_reported_posted_date": r["observed_version_local_last_update_posted"],
                "observed_recorded_status": r["observed_overall_status"],
                "first_public_version_at": "UNAVAILABLE",
                "source_retrieved_utc": r["retrieved_utc"],
                "clinical_valid_at": "UNAVAILABLE",
                "original_version_source_url": r["source_url"],
            } for r in original_versions
        ],
        "conditional_registry_publication_queries": cases,
        "independent_aact_owner_attested_archive_checks": controls,
        "archive_controls_match_both_source_statuses":
            all(c["source_families_agree_on_recorded_status"] for c in controls),
        "conditional_assumption": "source-reported-last-update-posted-only",
        "real_as_known_at_independently_authenticated": False,
        "real_clinical_valid_at_known": False,
        "this_is_not_original_W13_temporal_python_execution": True,
        "historical_NIH_P2_benchmark_completed": False,
        "original_W13_journal_modified": False,
        "World48_required": False,
        "source_archive_bodies_redistributed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry-source", type=Path, required=True)
    p.add_argument("--aact-source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = observe(args.registry_source.read_bytes(),
                     args.aact_source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                           encoding="utf8")
    print(json.dumps({
        "source_controls_match": report["archive_controls_match_both_source_statuses"],
        "conditional_query_count": len(report["conditional_registry_publication_queries"]),
        "NIH_completed": False, "real_as_known_at_authenticated": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
