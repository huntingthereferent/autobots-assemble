"""Bounded PhysioNet MIT-BIH public catalog identity probe; no ECG file access.

Only GET the exact public dataset description page. This is not waveform intake,
clinical research authorization, or a scientific test. Default mode is offline.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener

PAGE = "https://physionet.org/content/mitdb/1.0.0/"
SLUG = "mitdb"
VERSION = "1.0.0"
DOI = "10.13026/C2F305"
LICENSE = "Open Data Commons Attribution License v1.0"
MAX_BYTES = 600000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.ignored += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.ignored:
            self.ignored -= 1

    def handle_data(self, s):
        if not self.ignored:
            self.parts.append(s)


def classify(raw: bytes) -> dict:
    try:
        src = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("Non-UTF8 catalog response") from error
    h = TextOnly()
    h.feed(src)
    rendered = " ".join(" ".join(h.parts).split())
    checks = {
        "canonical_title": bool(re.search(r"\bMIT-BIH Arrhythmia Database\b", rendered)),
        "version": bool(re.search(r"\bVersion\s+1\.0\.0\b", rendered, re.I)),
        "version_doi": DOI.lower() in rendered.lower(),
        "public_access_class": "Database Open Access" in rendered,
        "publisher_license_label": LICENSE in rendered,
    }
    if not all(checks.values()):
        raise ValueError("Catalog identity, access policy or license not observed")
    return {
        "project_slug": SLUG,
        "version": VERSION,
        "version_doi": DOI,
        "published_access_label": "Database Open Access",
        "published_license_label": LICENSE,
        "checks": checks,
        "recording_files_read": False,
        "license_compliance_review_completed": False,
        "scientific_experiment_completed": False,
    }


def observe(opener=None) -> dict:
    receipt = {
        "schema_version": 1,
        "provider": "PhysioNet",
        "public_catalog_url": PAGE,
        "source_id": SLUG,
        "version": VERSION,
        "state": "SOURCE_WALL",
        "source_scope": "public_dataset_landing_page_metadata_only",
        "scientific_status": "NOT_TESTED",
        "clinical_data_access": "NOT_REQUESTED",
        "recordings_fetched": False,
        "source_body_archived": False,
        "rights_review": "REQUIRED_BEFORE_DATA_USE",
    }
    try:
        request = Request(PAGE, headers={
            "Accept": "text/html",
            "User-Agent": "Source-provenance-metadata/1.0 (huntingthereferent/autobots-assemble)",
        })
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("Catalog returned non-200 HTTP status")
            raw = response.read(MAX_BYTES + 1)
            observed = datetime.now(timezone.utc).isoformat()
        if len(raw) > MAX_BYTES:
            raise ValueError("Catalog response exceeds 600 kB limit")
        identity = classify(raw)
        receipt.update({
            "state": "PUBLIC_CATALOG_METADATA_OBSERVED",
            "observed_at_utc": observed,
            "response_status": 200,
            "body_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw),
            "identity": identity,
        })
    except (HTTPError, URLError, ValueError, TimeoutError, UnicodeError, OSError) as error:
        receipt.update({"state": "SOURCE_WALL", "error_class": type(error).__name__})
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Perform exactly one bounded public catalog GET")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = observe() if args.live else {
        "schema_version": 1, "state": "UNOBSERVED", "scientific_status": "NOT_TESTED",
        "reason": "Explicit --live was not requested",
    }
    result = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result)
    return 0 if not args.live or receipt["state"] == "PUBLIC_CATALOG_METADATA_OBSERVED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
