"""Original AACT source corroboration for exact NCT00001756 historical status.

Re-download both original independent deposited whole files, verify their
published MD5 and earlier independently observed SHA-256, then inspect only
the exact public study row. The owner-attested November 4 and November 9,
2022 archive collection dates are NOT independently timestamped registry
releases, first-public version dates, or clinical validity times.

No clinical data bodies are retained, and no W13/World48 runtime is changed.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from hashlib import sha256
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from . import nih_aact_archival_source as owner04
from . import nih_aact_second_2022_archive as owner09
from . import nih_p2_source_reported_posting_gate as official

SCHEMA = "nih-p2-adjacent-original-cross-archive-status-witness/v1"
STUDY = "NCT00001756"
NOV04_SHA = "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49"
NOV09_SHA = "d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755"
STUDIES = "AACT-2022-11-09/studies.txt"
LIMIT = 1_000_000
MIN_COUNT = 100_000
FIELDS = ("nct_id", "overall_status", "last_update_posted_date")
VERSIONS = (259, 260)


def extract_nov09(path: Path, verified: dict) -> dict:
    """Read the original source row only after entire ZIP checksum validation."""
    if (verified.get("entire_archive_sha256") != NOV09_SHA or
        verified.get("entire_archive_md5") != owner09.PUBLISHED_MD5 or
        verified.get("entire_archive_bytes") != owner09.EXPECTED_BYTES):
        raise ValueError("original Nov 9 archive did not authenticate")
    inventory, member = owner09.zip_member_inventory(path)
    if member != STUDIES or sum(r["name"] == STUDIES for r in inventory) != 1:
        raise ValueError("expected original Nov 9 studies.txt unavailable")
    matched = None
    seen_ids = set()
    rows = 0
    with ZipFile(path) as archive, archive.open(member) as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as handle:
            parser = csv.reader(handle, delimiter="|")
            header = next(parser, None)
            if (type(header) is not list or len(header) != len(set(header))
                    or not set(FIELDS) <= set(header)):
                raise ValueError("archived study source columns ambiguous")
            index = {f: header.index(f) for f in FIELDS}
            for row in parser:
                rows += 1
                if rows > LIMIT or len(row) != len(header):
                    raise ValueError("malformed or unbounded original Nov 9 source")
                nct = row[index["nct_id"]]
                if nct == STUDY:
                    if matched is not None:
                        raise ValueError("duplicate exact study identity")
                    status, updated = (row[index[k]] for k in FIELDS[1:])
                    if not status or len(status) > 80:
                        raise ValueError("empty or unbounded archive status")
                    matched = {
                        "nct_id": nct,
                        "overall_status": status,
                        "last_update_posted_date": updated,
                    }
    if rows < MIN_COUNT or matched is None:
        raise ValueError("missing original study row or incomplete archive")
    return {"row": matched, "full_table_rows_scanned": rows}


def audit_source_pair(nov04: dict, nov09: dict, official_pair: list[dict]) -> dict:
    """Compare three different original-source representations, without fusing clocks."""
    if (nov04.get("dataset_sha256") != NOV04_SHA or
        nov04.get("dataset_md5") != owner04.ARCHIVE_MD5 or
        nov04.get("dataset_size_bytes", 0) < 200_000_000 or
        nov09.get("entire_archive_sha256") != NOV09_SHA or
        nov09.get("entire_archive_md5") != owner09.PUBLISHED_MD5 or
        nov09.get("entire_archive_bytes") != owner09.EXPECTED_BYTES):
        raise ValueError("original complete-archive evidence missing")
    rows04 = nov04.get("observed_source_rows")
    rows09 = nov09.get("source_study_rows")
    if type(rows04) is not dict or set(rows04) != {STUDY} or (
        type(rows09) is not dict or set(rows09) != {STUDY}
    ):
        raise ValueError("wrong exact study joined to independently sourced files")
    first, second = rows04[STUDY], rows09[STUDY]
    for row in (first, second):
        if row.get("nct_id") != STUDY or (
            type(row.get("overall_status")) is not str or
            not 1 <= len(row["overall_status"]) <= 80
        ):
            raise ValueError("invalid original study status row")
        updated = row.get("last_update_posted_date")
        if type(updated) is not str or len(updated) != 10:
            raise ValueError("original archive update posting date unavailable")
        if date.fromisoformat(updated).isoformat() != updated:
            raise ValueError("noncanonical original archive update date")
    if [z.get("version") for z in official_pair] != [259, 260]:
        raise ValueError("wrong original registry-version pair")
    if [z.get("observed_overall_status") for z in official_pair] != [
        "Recruiting", "Completed"
    ] or any(z.get("first_public_version_timestamp_independently_authenticated")
             is not False for z in official_pair):
        raise ValueError("previous official version evidence mutated")
    comparisons = []
    for row, owner_claim, version in (
        (first, "2022-11-04", 259),
        (second, "2022-11-09", 260),
    ):
        original = official_pair[VERSIONS.index(version)]
        comparison = {
            "archive_owner_attested_collection_date": owner_claim,
            "original_registry_version": version,
            "original_archive_status": row["overall_status"],
            "original_registry_version_status": original["observed_overall_status"],
            "status_matches_original_registry_version":
                row["overall_status"].casefold() == original["observed_overall_status"].casefold(),
            "archive_recorded_last_update_posted":
                row["last_update_posted_date"],
            "registry_version_local_last_update_posted":
                original["observed_version_local_last_update_posted"],
            "update_posted_fields_match":
                row["last_update_posted_date"] == original["observed_version_local_last_update_posted"],
            "archive_snapshot_is_exact_registry_version": False,
            "archive_collection_date_is_registry_version_post_date": False,
        }
        comparisons.append(comparison)
    status_changed = first["overall_status"].casefold() != second["overall_status"].casefold()
    return {
        "schema": SCHEMA,
        "study": STUDY,
        "original_archive_sources": [
            {"original_owner": "Lalagkas AACT Zenodo", "source_url": owner04.ARCHIVE_RECORD,
             "whole_file_sha256": NOV04_SHA, "original_depositor_md5": owner04.ARCHIVE_MD5,
             "owner_attested_collection_date": "2022-11-04",
             "owner_statement_independently_witnessed_collection_transaction": False},
            {"original_owner": "Axfors Nilsonne AACT Zenodo", "source_url": owner09.DEPOSIT,
             "whole_file_sha256": NOV09_SHA, "original_depositor_md5": owner09.PUBLISHED_MD5,
             "owner_attested_collection_date": "2022-11-09",
             "owner_statement_independently_witnessed_collection_transaction": False},
        ],
        "registry_version_source": {
            "run_id": official.ORIGINAL_RUN,
            "artifact_id": official.ORIGINAL_ARTIFACT,
            "artifact_sha256": official.ORIGINAL_ZIP_SHA256,
            "minimal_receipt_sha256": official.PINNED_RECEIPT_SHA256,
        },
        "observed_original_archival_rows": [
            {"archive_owner_claimed_collection_date": "2022-11-04",
             "nct_id": STUDY, "overall_status": first["overall_status"],
             "last_update_posted_date": first["last_update_posted_date"]},
            {"archive_owner_claimed_collection_date": "2022-11-09",
             "nct_id": STUDY, "overall_status": second["overall_status"],
             "last_update_posted_date": second["last_update_posted_date"]},
        ],
        "source_status_comparisons": comparisons,
        "archival_status_values_differ": status_changed,
        "archived_and_registry_status_correspondence":
            all(z["status_matches_original_registry_version"] for z in comparisons),
        "archive_collection_order_independently_timestamped": False,
        "first_public_version_post_times_independently_witnessed": False,
        "original_version_status_as_of_independent_archive_collection_claims": "SOURCE_OWNER_ATTESTED_ONLY",
        "clinical_event_valid_at_authenticated": False,
        "real_historical_W13_query_admitted": False,
        "nih_phase2_completed": False,
        "original_twelve_job_runtime_modified": False,
        "third_party_archive_bodies_published": False,
    }


def execute(*, output_dir: Path) -> dict:
    authenticated = official.authenticate_receipt(official.EVIDENCE.read_bytes())
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="nih-p2-independent-cross-archive-") as td:
        temp = Path(td)
        file04, file09 = temp / "owner-nov04.txt", temp / "owner-nov09.zip"
        owner04.download_archive(file04)
        extract04 = owner04.verify_extract_archive(file04, target_ids=(STUDY,))
        if extract04["dataset_sha256"] != NOV04_SHA:
            raise ValueError("original owner November 4 whole source SHA differs")
        verified09 = owner09.verify_download(output=file09)
        if verified09["entire_archive_sha256"] != NOV09_SHA:
            raise ValueError("original owner November 9 whole source SHA differs")
        selected09 = extract_nov09(file09, verified09)
        merged09 = {
            **verified09, "source_study_rows": {STUDY: selected09["row"]}
        }
        result = audit_source_pair(extract04, merged09, authenticated)
        result["original_nov04_source_rows_scanned"] = extract04["scanned_physical_csv_rows"]
        result["original_nov09_source_rows_scanned"] = selected09["full_table_rows_scanned"]
    (output_dir / "independent-aact-original-version-corroboration.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    opt = parser.parse_args()
    r = execute(output_dir=opt.output_dir)
    print(json.dumps({
        "schema": r["schema"],
        "archived_status_difference": r["archival_status_values_differ"],
        "archive_to_original_version_correspondence":
            r["archived_and_registry_status_correspondence"],
        "archive_records": r["observed_original_archival_rows"],
        "historical_W13_admitted": r["real_historical_W13_query_admitted"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
