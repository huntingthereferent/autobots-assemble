"""Verify a real dated, third-party archived AACT study-status source.

Downloads a specific Zenodo-published 2023 AACT studies table, checks the
*entire file* against the depositor's MD5, hashes its bytes with SHA-256,
and selects strictly named public study IDs. It independently observes current
official registry status for those IDs and records only differences and
bounded source metadata.

An archived 2023 row is a historical *snapshot* observed no later than
the published release; this does NOT prove an individual registry revision
was posted on the archive date or when a clinical state actually changed.
This is NOT an NIH submission, clinical verdict, or an extra native job.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from hashlib import md5, sha256
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-real-aact-archived-source-v1"
ARCHIVE_RECORD = "https://zenodo.org/records/10058991"
ARCHIVE_FILE = ARCHIVE_RECORD + "/files/AACT_studies.txt?download=1"
ARCHIVE_MD5 = "d043fb7704bcff8cfb5be95d4f5ced85"
ARCHIVE_PUBLISHED_ON = "2023-10-31"
REGISTRY_ROOT = "https://clinicaltrials.gov/api/v2/studies/"
IDS = ("NCT03280849", "NCT04153409")
MAX_BYTES = 370_000_000
REQUIRED = ("nct_id", "overall_status", "study_first_posted_date",
            "last_update_posted_date")


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def identity(nct):
    if type(nct) is not str or not re.fullmatch(r"NCT\d{8}", nct):
        raise ValueError("exact NCT study ID required")
    return nct


def current_url(nct):
    return (REGISTRY_ROOT + identity(nct)
            + "?fields=NCTId,OverallStatus,StudyFirstPostDate,LastUpdatePostDate")


def validate_status(v):
    if type(v) is not str or not 1 <= len(v) <= 80 or any(ord(c) < 32 for c in v):
        raise ValueError("status is not an exact bounded public registry value")
    return v


def verify_extract_archive(path, *, target_ids=IDS, expected_md5=ARCHIVE_MD5):
    if type(target_ids) not in (tuple, list) or not 1 <= len(target_ids) <= 8:
        raise ValueError("bounded target set required")
    if len(set(target_ids)) != len(target_ids):
        raise ValueError("duplicate trial ID requested")
    ids = {identity(x) for x in target_ids}
    if not re.fullmatch(r"[0-9a-f]{32}", expected_md5):
        raise ValueError("invalid published archive checksum")
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("archived dataset file missing")
    md5sum, sha256sum = md5(), sha256()
    seen_bytes = 0
    with path.open("rb") as data:
        while chunk := data.read(1024 * 1024):
            seen_bytes += len(chunk)
            if seen_bytes > MAX_BYTES:
                raise ValueError("large unbounded source file")
            md5sum.update(chunk)
            sha256sum.update(chunk)
    if md5sum.hexdigest() != expected_md5:
        raise ValueError("whole archive source checksum disagrees with pinned deposit")

    rows, count = {}, 0
    with path.open(encoding="utf-8-sig", errors="strict", newline="") as data:
        reader = csv.reader(data, delimiter="|")
        header = next(reader)
        if len(header) != len(set(header)) or not set(REQUIRED) <= set(header):
            raise ValueError("archived AACT studies schema not recognized")
        fields = {key: header.index(key) for key in REQUIRED}
        for raw in reader:
            count += 1
            if not raw or raw[0] not in ids:
                continue
            if len(raw) != len(header):
                raise ValueError("selected historical study row malformed")
            nct_id = raw[fields["nct_id"]]
            if nct_id in rows:
                raise ValueError("duplicate archived study identity")
            value = validate_status(raw[fields["overall_status"]])
            rows[nct_id] = {
                "nct_id": nct_id, "overall_status": value,
                "study_first_posted_date": raw[fields["study_first_posted_date"]],
                "last_update_posted_date": raw[fields["last_update_posted_date"]],
                "source_column": "overall_status",
            }
    if set(rows) != ids:
        raise ValueError("selected historical study missing from verified snapshot")
    return {
        "dataset_sha256": sha256sum.hexdigest(),
        "dataset_md5": md5sum.hexdigest(),
        "dataset_size_bytes": seen_bytes,
        "observed_source_rows": rows,
        "scanned_physical_csv_rows": count,
    }


def download_archive(path):
    # A fixed dataset URL, never user-controlled. The full pinned checksum is
    # required after download regardless of the redirect storage host.
    url = urlsplit(ARCHIVE_FILE)
    if url.scheme != "https" or url.hostname != "zenodo.org":
        raise ValueError("untrusted archive origin")
    req = Request(ARCHIVE_FILE, headers={
        "Accept": "text/plain,application/octet-stream",
        "User-Agent": "Original-Workstation-Research-Verification/1.0",
    })
    with urlopen(req, timeout=70) as response, Path(path).open("wb") as target:
        if response.status != 200 or urlsplit(response.geturl()).scheme != "https":
            raise ValueError("official deposit download unavailable")
        n = 0
        while chunk := response.read(1024 * 1024):
            n += len(chunk)
            if n > MAX_BYTES:
                raise ValueError("published archive exceeds bounded download limit")
            target.write(chunk)
        if n < 1_000_000:
            raise ValueError("historical data file is implausibly small")


def parse_current(nct, raw):
    if type(raw) is not bytes or not 0 < len(raw) <= 100_000:
        raise ValueError("current registry source boundedness failed")
    try:
        value = json.loads(raw)
        module = value["protocolSection"]
        if module["identificationModule"]["nctId"] != nct:
            raise ValueError("current source NCT identity disagreement")
        status = validate_status(module["statusModule"]["overallStatus"])
    except (ValueError, TypeError, KeyError) as e:
        raise ValueError("current official response invalid") from e
    return {"nct_id": nct, "overall_status": status,
            "raw_source_sha256": sha256(raw).hexdigest(),
            "source_url": current_url(nct)}


def official_current_fetch(nct):
    with urlopen(Request(current_url(nct), headers={"Accept": "application/json",
                   "User-Agent": "Original-Workstation-Research-Verification/1.0"}), timeout=15) as response:
        if response.status != 200 or urlsplit(response.geturl()).hostname != "clinicaltrials.gov":
            raise ValueError("official current registry unavailable")
        raw = response.read(100_001)
    return parse_current(nct, raw)


def assemble(archive, current, *, retrieved_at):
    if type(retrieved_at) is not str or not retrieved_at.endswith("Z"):
        raise ValueError("UTC source observation timestamp required")
    try:
        instant = datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
        if instant.utcoffset().total_seconds() != 0:
            raise ValueError("UTC offset required")
    except (ValueError, AttributeError) as e:
        raise ValueError("invalid UTC observation timestamp") from e
    if set(archive["observed_source_rows"]) != set(current):
        raise ValueError("archive-current study identity sets disagree")
    cases = []
    for nct in sorted(current):
        old, present = archive["observed_source_rows"][nct], current[nct]
        if old["nct_id"] != nct or present["nct_id"] != nct:
            raise ValueError("source identifier disagreement")
        cases.append({
            "nct_id": nct,
            "archive_2023_overall_status": old["overall_status"],
            "current_observed_overall_status": present["overall_status"],
            "status_values_differ": old["overall_status"] != present["overall_status"],
            "archive_source_column": old["source_column"],
            "official_current_source_url": present["source_url"],
            "official_current_response_sha256": present["raw_source_sha256"],
        })
    return {
        "schema": SCHEMA,
        "archival_deposit_url": ARCHIVE_RECORD,
        "archival_file_url": ARCHIVE_FILE,
        "archive_published_on": ARCHIVE_PUBLISHED_ON,
        "original_depositor_checksum_md5": ARCHIVE_MD5,
        "entire_archive_verified_md5": archive["dataset_md5"],
        "entire_archive_sha256": archive["dataset_sha256"],
        "archive_file_size_bytes": archive["dataset_size_bytes"],
        "retrieved_at_utc": retrieved_at,
        "case_count": len(cases),
        "cases": cases,
        "external_archival_status_observations_only": True,
        "exact_per_study_version_number_proven": False,
        "archive_date_is_individual_study_post_date": False,
        "earliest_public_knowledge_from_archive_bounded_by_release_date_only": True,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
        "additional_native_workstation_job": False,
        "original_workstation_modified": False,
    }


def execute(*, output_dir, archive_fetch=download_archive,
            official_fetch=official_current_fetch, target_ids=IDS,
            now=None, expected_md5=ARCHIVE_MD5):
    start = now or datetime.now(timezone.utc)
    if start.tzinfo is None or start.utcoffset().total_seconds() != 0:
        raise ValueError("UTC observation required")
    retrieved_at = start.isoformat(timespec="seconds").replace("+00:00", "Z")
    with TemporaryDirectory() as td:
        file = Path(td) / "AACT_studies.txt"
        archive_fetch(file)
        verified = verify_extract_archive(
            file, target_ids=target_ids, expected_md5=expected_md5)
    current = {nct: official_fetch(nct) for nct in target_ids}
    report = assemble(verified, current, retrieved_at=retrieved_at)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "nih-p2-archived-aact-source-receipt.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    a = parser.parse_args(argv)
    report = execute(output_dir=a.output_dir)
    print(canonical({
        "schema": SCHEMA, "study_count": report["case_count"],
        "source_sha256": report["entire_archive_sha256"],
        "archive_published_on": report["archive_published_on"],
        "historical_version_number_established": False,
        "historical_snapshot_verified": True,
        "clinical_verdict": "NOT_EVALUATED",
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
