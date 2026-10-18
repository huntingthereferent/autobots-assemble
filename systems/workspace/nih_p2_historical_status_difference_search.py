"""Find actual status-field differences across TWO authentic dated AACT exports.

Whole original files are re-downloaded and verified against the independent
depositors' published MD5s and previously witnessed SHA-256s before any
comparison. The selection rule is frozen in code before the actual scan:
choose lexicographically smallest eight NCT IDs with case-insensitively
different nonempty overall_status values in BOTH source exports.

This witnesses differing historical *exported source fields*, not the exact
public posting moment of any individual registry revision, and does not
prove any clinical state change. The original twelve-job W13 workstation,
native game, Phase 1 draft and NIH submissions are never altered.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from . import nih_aact_second_2022_archive as old
from . import nih_aact_archival_source as recent

SCHEMA = "nih-p2-original-aact-two-snapshot-status-difference-search/v1"
OLD_SHA = "d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755"
NEW_SHA = "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49"
OLD_STUDIES = "AACT-2022-11-09/studies.txt"
ID_PREFIX = "NCT"
ANCHOR_COUNT = 8
ROW_LIMIT = 1_000_000
MIN_SOURCE_ROWS = 100_000
REQUIRED = ("nct_id", "overall_status", "last_update_posted_date")


def normalize_status(value):
    """Only case/outer whitespace normalize; never collapse distinct statuses."""
    if not isinstance(value, str) or not 1 <= len(value) <= 80:
        raise ValueError("empty or oversize archived status")
    cleaned = value.strip()
    if not cleaned or any(ord(c) < 32 for c in cleaned):
        raise ValueError("invalid archived status field")
    return cleaned.casefold()


def _stream_rows(stream, *, source):
    reader = csv.reader(stream, delimiter="|")
    fields = next(reader, None)
    if (not isinstance(fields, list) or len(fields) != len(set(fields))
            or not set(REQUIRED) <= set(fields)):
        raise ValueError("source table has no unambiguous required AACT columns")
    idx = {field: fields.index(field) for field in REQUIRED}
    count = 0
    for values in reader:
        count += 1
        if count > ROW_LIMIT:
            raise ValueError("source row count exceeds stated finite research scope")
        if len(values) != len(fields):
            raise ValueError(f"{source} row has wrong number of source fields")
        nct = values[idx["nct_id"]]
        if (len(nct) != 11 or not nct.startswith(ID_PREFIX)
                or not nct[3:].isdigit()):
            raise ValueError("invalid original NCT identity")
        status = values[idx["overall_status"]]
        norm = normalize_status(status)
        last = values[idx["last_update_posted_date"]]
        if len(last) > 40:
            raise ValueError("unexpected historical update field")
        yield nct, (status, norm, last)


def scan_verified_tables(old_zip, new_flat, *, max_anchors=ANCHOR_COUNT):
    if type(max_anchors) is not int or not 1 <= max_anchors <= 12:
        raise ValueError("predeclared small anchor limit required")
    old_rows = {}
    with ZipFile(old_zip) as zipped:
        members = [x.filename for x in zipped.infolist() if x.filename == OLD_STUDIES]
        if members != [OLD_STUDIES]:
            raise ValueError("actual 2022 original studies.txt ZIP member not found once")
        with zipped.open(OLD_STUDIES) as raw:
            with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
                for nct, item in _stream_rows(stream, source="2022"):
                    if nct in old_rows:
                        raise ValueError("duplicate NCT in historical 2022 source")
                    old_rows[nct] = item
    if len(old_rows) < MIN_SOURCE_ROWS:
        raise ValueError("incomplete original 2022 snapshot")
    old_count = len(old_rows)
    new_count = 0
    common = 0
    changed = []
    same_norm = 0
    only_case_or_spacing = 0
    groups = Counter()
    with Path(new_flat).open(encoding="utf-8-sig", newline="") as stream:
        seen_new = set()
        for nct, item23 in _stream_rows(stream, source="2023"):
            if nct in seen_new:
                raise ValueError("duplicate NCT in historical 2023 source")
            seen_new.add(nct)
            new_count += 1
            original = old_rows.pop(nct, None)
            if original is None:
                continue
            common += 1
            status22, norm22, update22 = original
            status23, norm23, update23 = item23
            if norm22 == norm23:
                same_norm += 1
                if status22 != status23:
                    only_case_or_spacing += 1
                continue
            groups[(norm22, norm23)] += 1
            changed.append({
                "nct_id": nct,
                "overall_status_export_2022": status22,
                "overall_status_export_2023": status23,
                "last_update_posted_field_export_2022": update22,
                "last_update_posted_field_export_2023": update23,
                "status_values_differ_after_case_normalization": True,
                "exact_original_registry_version_post_time_proven": False,
                "actual_clinical_event_time_proven": False,
                "intervening_revisions_excluded": False,
            })
    if not common or common + len(old_rows) != old_count:
        raise ValueError("two source tables have no valid consistent join")
    if new_count < MIN_SOURCE_ROWS or common < MIN_SOURCE_ROWS:
        raise ValueError("paired real datasets do not overlap sufficiently")
    changed.sort(key=lambda row: row["nct_id"])
    selected = changed[:max_anchors]
    return {
        "rows_export_2022": old_count,
        "rows_export_2023": new_count,
        "common_nct_ids": common,
        "ids_only_2022": old_count - common,
        "ids_only_2023": new_count - common,
        "same_normalized_status_count": same_norm,
        "spelling_only_difference_count": only_case_or_spacing,
        "different_normalized_status_count": len(changed),
        "status_change_field_groups": [
            {"status_2022": a, "status_2023": b, "observed_paired_rows": n}
            for (a, b), n in sorted(groups.items())
        ],
        "predeclared_anchor_rule": "lexicographically first NCT IDs with differing casefolded archived overall_status in two verified exports",
        "selected_status_difference_anchors": selected,
        "new_source_versions_proven": False,
        "actual_original_per_version_public_posting_times_proven": False,
        "a_status_difference_witnesses_a_specific_intermediate_clinical_event": False,
    }


def execute(*, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="nih-two-original-aact-") as td:
        folder = Path(td)
        zip22, flat23 = folder / "source2022.zip", folder / "source2023.txt"
        receipt22 = old.verify_download(output=zip22)
        if receipt22["entire_archive_sha256"] != OLD_SHA:
            raise ValueError("2022 archived source SHA changed")
        inventory22 = old.inspect_verified_archive(zip22, receipt22)
        if (inventory22["direct_studies_table_member"] != OLD_STUDIES or
                inventory22["archive_member_layout"] != "direct-studies-table"):
            raise ValueError("2022 source member inventory was not independently verified")
        recent.download_archive(flat23)
        receipt23 = recent.verify_extract_archive(flat23)
        if (receipt23["dataset_sha256"] != NEW_SHA or
                receipt23["dataset_md5"] != recent.ARCHIVE_MD5):
            raise ValueError("2023 archived source digest mismatch")
        actual = scan_verified_tables(zip22, flat23)
    report = {
        "schema": SCHEMA,
        "source_2022": {
            "url": old.DEPOSIT, "doi": old.DEPOSIT_DOI,
            "creators": old.DEPOSIT_CREATORS,
            "source_owner_stated_dataset_date": "2022-11-09",
            "source_owner_stated_retrieval_date": "2022-11-27",
            "depositor_publication_date": "2023-11-09",
            "whole_archive_md5": receipt22["entire_archive_md5"],
            "whole_archive_sha256": receipt22["entire_archive_sha256"],
            "source_table_member": OLD_STUDIES,
        },
        "source_2023": {
            "url": recent.ARCHIVE_RECORD,
            "depositor_publication_date": recent.ARCHIVE_PUBLISHED_ON,
            "whole_archive_md5": receipt23["dataset_md5"],
            "whole_archive_sha256": receipt23["dataset_sha256"],
            "source_table_filename": "AACT_studies.txt",
        },
        **actual,
        "raw_original_source_archives_persisted": False,
        "original_twelve_native_jobs_modified": False,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
    }
    (output / "nih-p2-original-aact-status-differences.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args(argv)
    result = execute(output_dir=args.output_dir)
    print(json.dumps({
        "schema": SCHEMA, "shared_ids": result["common_nct_ids"],
        "observed_changed_status_fields": result["different_normalized_status_count"],
        "selected_anchor_ids": [
            row["nct_id"] for row in result["selected_status_difference_anchors"]],
        "exact_per_study_version_posting_established": False,
        "nih_submission": False,
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
