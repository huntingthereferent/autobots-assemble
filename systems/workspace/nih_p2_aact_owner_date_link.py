"""Reproduce the ORIGINAL DEPOSITOR's file-linked AACT download-date claim.

This separately witnesses that the source owner wrote a date claim in a
pinned public Git blob beside executable loading of the exact archived
Zenodo URL. It is source-owner attestation only: neither a cryptographically
witnessed 2022 download event nor a per-study registry history.

No workstation job, original research code, or third-party file is changed.
"""
from __future__ import annotations

import argparse
from hashlib import sha1
import json
from pathlib import Path
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-2022-aact-owner-script-date-reference/v1"
ORIGINAL_REPO = "lalagkaspn/mendelian_comorbidity_therapeutics"
PATH = "drugs_investigated_indicated_diseases.R"
EARLIER_COMMIT = "96ccb828b5118e54c658fc1cd386173de67a4b4"
EARLIER_BLOB_SHA1 = "3a5781267f15fa69ae1779e47cdb0b4e1f1f0cb6"
LINKED_COMMIT = "675b7a4992d7e2469d368924f4c1f87d7ca162da"
LINKED_BLOB_SHA1 = "3e3f8714df2c037cce24961a57802546ce95f7b4"
DECLARED_DATE = "2022-11-04"
SCRIPT_DATE_CLAIM = "## data of download: November 4, 2022"
ORIGINAL_AACT_SOURCE = "https://aact.ctti-clinicaltrials.org/"
EXACT_ZENODO_URL = "https://zenodo.org/records/10058991/files/AACT_studies.txt?download=1"
ALREADY_VERIFIED_ZENODO_FILE_SHA256 = "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49"
EARLIER_LOAD = 'ct = fread("raw_data/AACT_studies.txt")'
LINKED_LOAD = f'ct = fread("{EXACT_ZENODO_URL}")'
MAX_SCRIPT_BYTES = 500_000


def github_blob_sha1(raw):
    if type(raw) is not bytes or len(raw) > MAX_SCRIPT_BYTES:
        raise ValueError("source Git blob missing or oversized")
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def witness_source(raw, *, expected_blob_sha, expected_load):
    """Require pinned blob identity AND exact adjacent original author claim."""
    if github_blob_sha1(raw) != expected_blob_sha:
        raise ValueError("source owner script does not match independently pinned Git blob")
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("original source script not valid UTF-8") from exc
    lines = [line.strip() for line in source.splitlines()]
    # Do not accept a random date anywhere in the source and a different
    # archive URL in an unrelated block. The source and load must be linked.
    indexes = [i for i, line in enumerate(lines) if line == SCRIPT_DATE_CLAIM]
    if len(indexes) != 1:
        raise ValueError("missing or ambiguous original AACT source-date attribution")
    i = indexes[0]
    if i < 1 or lines[i-1] != f"## downloaded from the AACT: {ORIGINAL_AACT_SOURCE}":
        raise ValueError("download date no longer attributed to the original AACT source")
    follow = lines[i+1:i+4]
    if expected_load not in follow:
        raise ValueError("download date is no longer directly linked to expected data file")
    if source.count(SCRIPT_DATE_CLAIM) != 1:
        raise ValueError("duplicated author date evidence")
    return {"git_blob_sha1": expected_blob_sha, "source_date_claim": DECLARED_DATE,
            "load_statement": expected_load, "line_of_date_claim": i+1}


def download_script(commit, *, opener=urlopen):
    if commit not in (EARLIER_COMMIT, LINKED_COMMIT):
        raise ValueError("may only retrieve pre-pinned source owner commits")
    url = f"https://raw.githubusercontent.com/{ORIGINAL_REPO}/{commit}/{PATH}"
    request = Request(url, headers={"User-Agent": "AB-Source-Provenance/1.0"})
    chunks, size = [], 0
    with opener(request, timeout=60) as response:
        while fragment := response.read(32768):
            if type(fragment) is not bytes:
                raise ValueError("GitHub source response is not raw bytes")
            size += len(fragment)
            if size > MAX_SCRIPT_BYTES:
                raise ValueError("original source script exceeds bounded intake")
            chunks.append(fragment)
    return b"".join(chunks)


def compare_source_owner_statements(earlier_raw, linked_raw):
    earlier = witness_source(
        earlier_raw, expected_blob_sha=EARLIER_BLOB_SHA1, expected_load=EARLIER_LOAD)
    linked = witness_source(
        linked_raw, expected_blob_sha=LINKED_BLOB_SHA1, expected_load=LINKED_LOAD)
    if earlier["source_date_claim"] != linked["source_date_claim"]:
        raise ValueError("original owner date attribution changes between cited commits")
    return {
        "schema": SCHEMA,
        "original_source_owner": ORIGINAL_REPO,
        "original_source_file": PATH,
        "original_source_2022_date_owner_attested": DECLARED_DATE,
        "earlier_author_commit": EARLIER_COMMIT,
        "earlier_author_commit_url":
            f"https://github.com/{ORIGINAL_REPO}/blob/{EARLIER_COMMIT}/{PATH}",
        "earlier_source_witness": earlier,
        "linked_author_commit": LINKED_COMMIT,
        "linked_author_commit_url":
            f"https://github.com/{ORIGINAL_REPO}/blob/{LINKED_COMMIT}/{PATH}",
        "linked_source_witness": linked,
        "linked_exact_depositor_zenodo_url": EXACT_ZENODO_URL,
        "external_zenodo_file_SHA256_verified_in_separate_original_archive_ci":
            ALREADY_VERIFIED_ZENODO_FILE_SHA256,
        "earlier_local_file_download_date_statement": True,
        "later_code_links_same_date_claim_to_exact_deposited_file_url": True,
        "owner_attested_source_date": True,
        "2022_download_transaction_independently_timestamped": False,
        "zenodo_file_SHA256_is_embedded_in_original_owner_script": False,
        "underlying_snapshot_date_cryptographically_verified": False,
        "owner_attested_date_precedes_other_owner_stated_2022_nov09_date": True,
        "all_original_per_study_versions_authenticated": False,
        "individual_registry_version_publication_instants_authenticated": False,
        "field_difference_is_clinical_change": False,
        "NIH_submission": False,
        "native_twelve_job_workstation_modified": False,
    }


def execute(*, output_dir, opener=urlopen):
    earlier = download_script(EARLIER_COMMIT, opener=opener)
    linked = download_script(LINKED_COMMIT, opener=opener)
    result = compare_source_owner_statements(earlier, linked)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output/"nih-p2-aact-owner-script-date-link.json").write_text(
        json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute(output_dir=args.output_dir)
    print(json.dumps({
        "schema": result["schema"], "owner_attested_date": DECLARED_DATE,
        "owner_file_url_witnessed": True,
        "original_download_instant_independently_authenticated": False,
        "individual_public_version_instants_authenticated": False,
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
