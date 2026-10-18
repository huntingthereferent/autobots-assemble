"""Independently verify and compare TWO original historical AACT snapshots.

Full whole-file checksums required on both independent Zenodo deposits.
No inferred per-study version, first-public-posting time, or clinical event.
Preserve differing original study metadata; matching status does not imply
absence of intervening revisions or events.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from . import nih_aact_second_2022_archive as old
from . import nih_aact_archival_source as recent

SCHEMA = "nih-p2-authenticated-aact-2022-2023-paired-observations/v1"
OLD_SHA = "d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755"
NEW_SHA = "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49"
IDS = tuple(sorted(set(old.TARGET_IDS) & set(recent.IDS)))


def compare(old_report, new_source):
    """Cross-check original source owners and exact identities before joining."""
    if (type(old_report) is not dict or
            old_report.get("schema") != old.SCHEMA or
            old_report.get("entire_archive_md5") != old.PUBLISHED_MD5 or
            old_report.get("entire_archive_sha256") != OLD_SHA or
            old_report.get("entire_archive_bytes") != old.EXPECTED_BYTES or
            old_report.get("upstream_stated_dataset_date") != "2022-11-09" or
            old_report.get("deposit_publication_date") != "2023-11-09" or
            old_report.get("deposit_doi") != old.DEPOSIT_DOI or
            old_report.get("archive_member_layout") != "direct-studies-table" or
            old_report.get("direct_studies_table_member") != "AACT-2022-11-09/studies.txt" or
            old_report.get("study_rows_examined", 0) < 1000 or
            old_report.get("per_version_original_public_posting_date_proven") is not False or
            old_report.get("original_twelve_job_workstation_modified") is not False):
        raise ValueError("first archive requires source-authenticated 2022 studies table")
    if (type(new_source) is not dict or
            new_source.get("dataset_md5") != recent.ARCHIVE_MD5 or
            new_source.get("dataset_sha256") != NEW_SHA or
            new_source.get("dataset_size_bytes") != 289643332 or
            new_source.get("scanned_physical_csv_rows", 0) < 1000):
        raise ValueError("second archive requires source-authenticated 2023 studies table")
    rows_old = old_report.get("selected_study_records")
    rows_new = new_source.get("observed_source_rows")
    if type(rows_old) is not dict or type(rows_new) is not dict:
        raise ValueError("the exact two archived study sets must be present")
    if set(rows_old) != set(IDS) or set(rows_new) != set(IDS):
        raise ValueError("missing, extra or duplicated cross-snapshot study IDs")
    observations = []
    for nct in IDS:
        a, b = rows_old[nct], rows_new[nct]
        if a.get("nct_id") != nct or b.get("nct_id") != nct:
            raise ValueError("case source identity cross-wired")
        val_2022 = old_report["selected_study_records"][nct].get("overall_status_2022")
        val_2023 = b.get("overall_status")
        if (type(val_2022) is not str or not val_2022.strip() or
                type(val_2023) is not str or not val_2023.strip()):
            raise ValueError("empty archived status source value")
        d22 = a.get("study_last_update_posted_date_2022")
        d23 = b.get("last_update_posted_date")
        for d in (d22, d23):
            if d is not None and (type(d) is not str or len(d) > 80):
                raise ValueError("posting metadata malformed")
        observations.append({
            "nct_id": nct,
            "status_as_recorded_in_2022_export": val_2022,
            "status_as_recorded_in_2023_export": val_2023,
            "status_spelling_equal": val_2022 == val_2023,
            "study_last_update_posted_as_recorded_2022": d22,
            "study_last_update_posted_as_recorded_2023": d23,
            "recorded_last_update_posted_value_equal": d22 == d23,
            "status_value_difference_between_exports": val_2022 != val_2023,
            "any_intervening_status_revisions_excluded": False,
            "exact_date_of_intervening_change_proven": False,
            "actual_clinical_event_time_proven": False,
        })
    return {
        "schema": SCHEMA,
        "sources": [
            {"archive": "2022-dated independent AACT Zenodo deposit",
             "record": old.DEPOSIT, "doi": old.DEPOSIT_DOI,
             "depositor_creators": old.DEPOSIT_CREATORS,
             "upstream_stated_dataset_date": "2022-11-09",
             "upstream_stated_retrieval_date": "2022-11-27",
             "deposit_publication_date": "2023-11-09",
             "whole_archive_md5": old_report["entire_archive_md5"],
             "whole_archive_sha256": old_report["entire_archive_sha256"]},
            {"archive": "2023-dated independent AACT Zenodo studies export",
             "record": recent.ARCHIVE_RECORD,
             "deposit_publication_date": recent.ARCHIVE_PUBLISHED_ON,
             "whole_archive_md5": new_source["dataset_md5"],
             "whole_archive_sha256": new_source["dataset_sha256"]},
        ],
        "observations": observations,
        "cross_source_nct_count": len(observations),
        "same_recorded_status_count": sum(x["status_spelling_equal"] for x in observations),
        "different_recorded_status_count": sum(not x["status_spelling_equal"] for x in observations),
        "historical_per_study_source_version_contents_authenticated": False,
        "historical_per_study_first_publication_time_authenticated": False,
        "paired_dataset_dates_are_individual_version_post_dates": False,
        "missing_intervening_record_changes_ruled_out": False,
        "official_NIH_submission": False,
        "clinical_verdict": "NOT_EVALUATED",
        "original_twelve_job_workstation_modified": False,
    }


def execute(*, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="nih-p2-two-dated-archives-") as td:
        root = Path(td)
        zip22 = root / "AACT-2022-11-09.zip"
        flat23 = root / "AACT_studies_2023.txt"
        source22 = old.verify_download(output=zip22)
        report22 = old.inspect_verified_archive(zip22, source22)
        recent.download_archive(flat23)
        report23 = recent.verify_extract_archive(flat23, target_ids=IDS)
        report = compare(report22, report23)
    (output / "nih-p2-2022-2023-paired-observations.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    report = execute(output_dir=args.output_dir)
    print(json.dumps({
        "schema": report["schema"],
        "total": report["cross_source_nct_count"],
        "same_status": report["same_recorded_status_count"],
        "different_status": report["different_recorded_status_count"],
        "source_sha256": [x["whole_archive_sha256"] for x in report["sources"]],
        "exact_individual_status_change_time_proven": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
