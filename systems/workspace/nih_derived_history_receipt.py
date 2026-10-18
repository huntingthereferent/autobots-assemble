"""Independently verify a frozen, third-party *derived* study-history corpus.

TrialTrace's author-created CSVs describe reconstructed ClinicalTrials.gov
history. The *raw historical study responses are not distributed*. This lane
does not authenticate original historical content or public posting time.
It records hashes, counts, identity matches and bounded derived transitions,
without creating a thirteenth native workstation job.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-independent-derived-history/v1"
UPSTREAM = "Byungwoong Yoo, TrialTrace"
UPSTREAM_COMMIT = "65a61a680eaffa8ccd6c9eeae11f1079c8d0e22e"
REPO = "https://github.com/ByungwoongYoo/trialtrace"
DATA_LICENSE = "https://creativecommons.org/licenses/by/4.0/"
RAW_ROOT = ("https://raw.githubusercontent.com/ByungwoongYoo/trialtrace/"
            + UPSTREAM_COMMIT + "/src/trialtrace/data/")
EXPECTED_SHA256 = {
    "raw_event_ledger.csv": "192f580c472c52159cb63e777521d362bd33fcfce321d87e3ae824907cd51ea8",
    "raw_trial_anchors.csv": "17494820e7389eca8cb135e64288c9b8516f10b388874829591ad78712250b53",
    "provenance/retrieval_manifest_reduced.csv": "14c61e0652d0f86b692ac925c7a374807f8dae39a25fc7fb02b5f2386a6b8825",
    "provenance/version_counts.csv": "cc21442d90ec9d70cfb880da9779a7b17700428b95bffae84fb346402e251d47",
}
LIMITS = {
    "raw_event_ledger.csv": 11_000_000,
    "raw_trial_anchors.csv": 250_000,
    "provenance/retrieval_manifest_reduced.csv": 2_000_000,
    "provenance/version_counts.csv": 40_000,
}
EXPECTED_COUNTS = {
    "trials": 400, "transitions": 5629,
    "history_versions": 6029, "history_indexes": 400,
}
TARGET = "NCT04153409"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def source_url(name):
    if name not in EXPECTED_SHA256:
        raise ValueError("only the four pinned upstream source files may be fetched")
    return RAW_ROOT + name


def fetch_source(name):
    url = source_url(name)
    u = urlsplit(url)
    if u.scheme != "https" or u.hostname != "raw.githubusercontent.com":
        raise ValueError("source origin not permitted")
    request = Request(url, headers={
        "Accept": "text/plain,application/octet-stream",
        "User-Agent": "Workstation-Frozen-Source-Research/1.0",
    })
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError("source file unavailable")
        dst = urlsplit(response.geturl())
        if dst.scheme != "https" or dst.hostname != "raw.githubusercontent.com":
            raise ValueError("source redirected outside the pinned origin")
        raw = response.read(LIMITS[name] + 1)
    if not raw or len(raw) > LIMITS[name]:
        raise ValueError("upstream source file exceeds bounded download")
    return raw


def verify_source(name, raw, expected=None):
    source_url(name)
    digest = sha256(raw).hexdigest()
    if (type(raw) is not bytes or not raw or len(raw) > LIMITS[name]
            or digest != (expected or EXPECTED_SHA256[name])):
        raise ValueError("upstream published SHA-256 evidence mismatch")
    return digest


def parse_rows(raw, required):
    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(text.splitlines())
        if (not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames)
                or not set(required) <= set(reader.fieldnames)):
            raise ValueError("derived source CSV schema mismatch")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError("malformed derived row")
        return rows
    except UnicodeError as error:
        raise ValueError("unreadable source CSV") from error


def verify_corpus(files, *, expected_hashes=None, target=TARGET):
    if type(files) is not dict or set(files) != set(EXPECTED_SHA256):
        raise ValueError("all four pinned source files required")
    if type(target) is not str or not re.fullmatch(r"NCT[0-9]{8}", target):
        raise ValueError("exact public study identifier required")
    hashes = {
        name: verify_source(name, data, (expected_hashes or {}).get(name))
        for name, data in files.items()
    }
    ledger = parse_rows(files["raw_event_ledger.csv"], {
        "nct_id", "version", "history_version_date", "is_posted_state_transition",
        "before_overall_status", "after_overall_status",
    })
    anchors = parse_rows(files["raw_trial_anchors.csv"], {
        "nct_id", "history_versions", "first_results_posted_version",
    })
    manifest = parse_rows(files["provenance/retrieval_manifest_reduced.csv"], {
        "kind", "nct_id", "version", "retrieved_at_utc", "canonical_json_sha256", "source_url",
    })
    version_counts = parse_rows(files["provenance/version_counts.csv"], {"nct_id", "versions"})
    counts = {
        "trials": len(anchors),
        "transitions": len(ledger),
        "history_versions": sum(r["kind"] == "version" for r in manifest),
        "history_indexes": sum(r["kind"] == "history_index" for r in manifest),
    }
    if counts != EXPECTED_COUNTS:
        raise ValueError("corpus source counts have changed")
    anchor_ids = {r["nct_id"] for r in anchors}
    if (len(anchor_ids) != len(anchors) or
            anchor_ids != {r["nct_id"] for r in ledger} or
            anchor_ids != {r["nct_id"] for r in manifest} or
            anchor_ids != {r["nct_id"] for r in version_counts} or
            len(version_counts) != len(anchors)):
        raise ValueError("derived corpus identity sets disagree")
    versions = {r["nct_id"]: int(r["versions"]) for r in version_counts}
    if sum(versions.values()) != EXPECTED_COUNTS["history_versions"]:
        raise ValueError("version counts do not reconcile")
    if target not in anchor_ids:
        raise ValueError("selected study absent from frozen version corpus")
    target_anchor = next(r for r in anchors if r["nct_id"] == target)
    manifest_versions = [r for r in manifest if r["nct_id"] == target and r["kind"] == "version"]
    if len(manifest_versions) != versions[target] or int(target_anchor["history_versions"]) != versions[target]:
        raise ValueError("historical study's recorded version counts disagree")
    if any(not re.fullmatch(r"[0-9a-f]{64}", r["canonical_json_sha256"]) for r in manifest_versions):
        raise ValueError("missing claimed canonical historical-payload digest")
    if any(r["source_url"] != f"https://clinicaltrials.gov/study/{target}?tab=history"
           for r in manifest_versions):
        raise ValueError("version provenance links to an unexpected source")
    transitions = []
    for r in ledger:
        if r["nct_id"] != target:
            continue
        v = int(r["version"])
        if not 0 <= v < versions[target]:
            raise ValueError("version lies outside source index")
        transitions.append({
            "version": v,
            "version_date_as_derived": r["history_version_date"],
            "upstream_posted_flag_as_derived": r["is_posted_state_transition"],
            "before_overall_status_as_derived": r["before_overall_status"] or None,
            "after_overall_status_as_derived": r["after_overall_status"] or None,
        })
    if len({r["version"] for r in transitions}) != len(transitions):
        raise ValueError("duplicate reconstructed transition")
    if not transitions:
        raise ValueError("selected historical study lacks derived transitions")
    transitions.sort(key=lambda r: r["version"])
    return {
        "source_sha256": hashes,
        "corpus_counts": counts,
        "nct_id": target,
        "declared_history_version_count": versions[target],
        "derived_transition_count": len(transitions),
        "derived_transitions": transitions,
        "canonical_payload_hashes_from_upstream_only": [
            {"version": r["version"], "canonical_json_sha256": r["canonical_json_sha256"],
             "original_raw_version_bytes_available": False}
            for r in manifest_versions
        ],
    }


def execute(*, output_dir, fetch=fetch_source, target=TARGET, now=None):
    observed = now or datetime.now(timezone.utc)
    if observed.tzinfo is None or observed.utcoffset().total_seconds() != 0:
        raise ValueError("exact UTC observation time required")
    sources = {name: fetch(name) for name in EXPECTED_SHA256}
    result = verify_corpus(sources, target=target)
    record = {
        "schema": SCHEMA,
        "observed_at_utc": observed.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "upstream_author": UPSTREAM,
        "upstream_repository": REPO,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_data_license": "CC BY 4.0",
        "attribution_license_url": DATA_LICENSE,
        "source_urls": {name: source_url(name) for name in EXPECTED_SHA256},
        **result,
        "original_historical_payloads_available": False,
        "derived_corpus_is_second_archival_snapshot": False,
        "independent_historical_contents_authenticated": False,
        "individual_public_posting_dates_established": False,
        "historical_clinical_verdict": "NOT_EVALUATED",
        "original_twelve_job_workstation_modified": False,
        "official_NIH_submission": False,
        "raw_third_party_tables_archived": False,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "nih-p2-independent-derived-history.json").write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    r = execute(output_dir=args.output_dir)
    print(canonical({
        "schema": r["schema"], "source_count": len(r["source_sha256"]),
        "nct_id": r["nct_id"], "derived_transition_count": r["derived_transition_count"],
        "exact_historical_contents_authenticated": False,
        "second_archival_snapshot_verified": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
