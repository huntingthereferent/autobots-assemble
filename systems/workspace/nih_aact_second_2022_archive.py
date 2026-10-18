"""Authenticate a second, independently dated historical AACT deposit.

This is an archival SOURCE-OWNER experiment for NIH issue #106, not a new
workstation job or replacement for ClinicalTrials.gov historical versions.

Axfors & Nilsonne (Zenodo DOI 10.5281/zenodo.10091147) say the AACT
dataset reflects 2022-11-09 and was downloaded 2022-11-27; the deposit
was published 2023-11-09. The published file MD5 is pinned here.
Complete-source bytes and zip member inventory must be observed before
we claim the second historical status contents can be compared.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile

SCHEMA = "nih-p2-second-aact-2022-archive-inspection/v1"
SOURCE = "https://zenodo.org/records/10091147/files/AACT-2022-11-09.zip?download=1"
DEPOSIT = "https://zenodo.org/records/10091147"
DEPOSIT_DOI = "10.5281/zenodo.10091147"
DEPOSIT_CREATORS = ["Cathrine Axfors", "Gustav Nilsonne"]
PUBLISHED_MD5 = "1d4e6d141f40d300186fdd3d0a5980b1"
EXPECTED_BYTES = 236_218_508
MAX_SOURCE_BYTES = 260_000_000
TARGET_IDS = ("NCT04153409", "NCT03280849")
MAX_ROWS = 2_000_000
MAX_MEMBERS = 1000


def verify_download(*, opener=urlopen, output):
    """Hash entire archived source before considering any contents evidence."""
    dest = Path(output)
    md5, sha = hashlib.md5(), hashlib.sha256()
    read = 0
    request = Request(SOURCE, headers={"User-Agent": "AB-Bounded-Research/1.0"})
    with opener(request, timeout=180) as response, dest.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            if type(chunk) is not bytes:
                raise ValueError("nonbyte source response")
            read += len(chunk)
            if read > MAX_SOURCE_BYTES:
                raise ValueError("source exceeded bounded size before checksum completion")
            md5.update(chunk)
            sha.update(chunk)
            out.write(chunk)
    if read != EXPECTED_BYTES or md5.hexdigest() != PUBLISHED_MD5:
        dest.unlink(missing_ok=True)
        raise ValueError("2022 historical source does not match Zenodo deposited whole-file MD5/size")
    return {"entire_archive_bytes": read, "entire_archive_md5": md5.hexdigest(),
            "entire_archive_sha256": sha.hexdigest()}


def zip_member_inventory(archive_path):
    """Bound path/size and record source layout; never extract zip contents."""
    with ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if not infos or len(infos) > MAX_MEMBERS:
            raise ValueError("unexpected empty or oversize historical zip inventory")
        items = []
        for info in infos:
            name = info.filename
            p = PurePosixPath(name)
            if (not name or name.startswith("/") or "\\" in name or
                    p.is_absolute() or ".." in p.parts or info.file_size > 9_000_000_000):
                raise ValueError("unsafe nested archived file or excessive uncompressed size")
            items.append({"name": name, "size": info.file_size,
                          "crc32": f"{info.CRC:08x}", "compressed_size": info.compress_size})
        direct = [info for info in infos if (
            PurePosixPath(info.filename).name.casefold() == "studies.txt"
            and not info.is_dir())]
        # Absence is an important, bounded research finding, not an invitation
        # to silently parse a different table/file name.
        if len(direct) > 1:
            raise ValueError("ambiguous multiple studies.txt historical tables")
        return items, direct[0].filename if direct else None


def extract_selected_studies(archive_path, filename):
    """Read at most 2M pipe-delimited rows from archived studies.txt.

    If the source archive uses some other dump representation, the caller
    records unknown study-level comparability instead of inventing rows.
    """
    selected = {}
    with ZipFile(archive_path) as archive, archive.open(filename) as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="|")
            fields = reader.fieldnames or []
            required = ("nct_id", "overall_status")
            if any(k not in fields for k in required):
                raise ValueError("historical studies.txt lacks actual required fields")
            if len(fields) != len(set(fields)):
                raise ValueError("duplicate archive table columns")
            observed = 0
            for row in reader:
                observed += 1
                if observed > MAX_ROWS:
                    raise ValueError("unbounded archived study rows")
                study = row["nct_id"]
                if study in TARGET_IDS:
                    if study in selected:
                        raise ValueError("same historical study appears twice")
                    selected[study] = {
                        "nct_id": study,
                        "overall_status_2022": row["overall_status"],
                        "study_first_posted_date_2022": row.get("study_first_posted_date"),
                        "study_last_update_posted_date_2022": row.get("last_update_posted_date"),
                    }
            if observed < 1000 or any(not row["overall_status_2022"] for row in selected.values()):
                raise ValueError("archive study table content did not meet bounded plausibility")
    return selected, observed


def inspect_verified_archive(archive_path, digest_receipt):
    if (digest_receipt.get("entire_archive_md5") != PUBLISHED_MD5 or
            digest_receipt.get("entire_archive_bytes") != EXPECTED_BYTES or
            len(digest_receipt.get("entire_archive_sha256", "")) != 64):
        raise ValueError("unverified whole historical archive cannot be inspected")
    items, studies_file = zip_member_inventory(archive_path)
    report = {
        "schema": SCHEMA,
        "deposit": DEPOSIT,
        "deposit_doi": DEPOSIT_DOI,
        "deposit_creators": DEPOSIT_CREATORS,
        "upstream_stated_dataset_date": "2022-11-09",
        "upstream_stated_retrieval_date": "2022-11-27",
        "deposit_publication_date": "2023-11-09",
        **digest_receipt,
        "archive_files": items,
        "direct_studies_table_found": studies_file is not None,
        "direct_studies_table_member": studies_file,
        "selected_study_records": {},
        "study_rows_examined": 0,
        "pairwise_2022_2023_status_comparison_proven": False,
        "original_clinicaltrials_per_study_versions_proven": False,
        "per_version_original_public_posting_date_proven": False,
        "study_event_time_proven": False,
        "archive_member_layout": "unclassified",
        "source_license_review_required": True,
        "original_twelve_job_workstation_modified": False,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
    }
    lower = [i["name"].lower() for i in items]
    if studies_file:
        records, examined = extract_selected_studies(archive_path, studies_file)
        report["selected_study_records"] = records
        report["study_rows_examined"] = examined
        report["archive_member_layout"] = "direct-studies-table"
        report["pairwise_2022_2023_status_comparison_proven"] = False  # second archive not joined yet
    elif any(x.endswith(".dmp") for x in lower):
        report["archive_member_layout"] = "postgres-dump-awaiting-reproducible-extraction"
    elif any(x.endswith(".sql") for x in lower):
        report["archive_member_layout"] = "sql-dump-awaiting-reproducible-extraction"
    else:
        report["archive_member_layout"] = "other-archive-layout-requires-owner-inspection"
    return report


def execute(*, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="verified-aact-2022-") as td:
        raw = Path(td) / "AACT-2022-11-09.zip"
        receipt = verify_download(output=raw)
        report = inspect_verified_archive(raw, receipt)
    (output_dir / "nih-p2-aact-2022-archive-inspection.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args(argv)
    report = execute(output_dir=args.output_dir)
    print(json.dumps({
        "schema": report["schema"], "source_md5_verified": True,
        "source_sha256": report["entire_archive_sha256"],
        "member_layout": report["archive_member_layout"],
        "member_count": len(report["archive_files"]),
        "direct_studies_table_found": report["direct_studies_table_found"],
        "selected_studies": sorted(report["selected_study_records"]),
        "original_per_study_version_time_proven": False,
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
