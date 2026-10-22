"""Public NOAA/NCEI SSOD Version 2 dataset metadata only. No weather rows.

Fixed source page, one GET, no redirect, response body discarded after
five independent publisher metadata predicates. No CDO key and no observations.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener

URL = "https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C01690/html"
TITLE = "Synoptic Summary of the Day (SSOD), Version 2"
ID = "gov.noaa.ncdc:C01690"
DSI = "NCEI DSI 2076_02"
LIMIT = 500000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class VisibleHtml(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.visible = []
        self.headings = []
        self.heading = None
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.hidden += 1
        if tag == "h1":
            self.heading = []

    def handle_endtag(self, tag):
        if tag == "h1" and self.heading is not None:
            self.headings.append(" ".join(" ".join(self.heading).split()))
            self.heading = None
        if tag in ("script", "style", "noscript") and self.hidden:
            self.hidden -= 1

    def handle_data(self, text):
        if not self.hidden:
            self.visible.append(text)
            if self.heading is not None:
                self.heading.append(text)


class IdentityMismatch(ValueError):
    def __init__(self, failed):
        self.failed = sorted(failed)
        super().__init__("publisher metadata mismatch")


def classify(raw: bytes) -> dict:
    try:
        html = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("NCEI catalog is not UTF-8") from exc
    h = VisibleHtml()
    h.feed(html)
    text = " ".join(" ".join(h.visible).split())
    checks = {
        "canonical_dataset_title": TITLE in h.headings,
        "dataset_catalog_id": ID in text,
        "dataset_series_id": DSI in text,
        "publisher_identity": "NOAA National Centers for Environmental Information" in text,
        "successor_lineage": "successor dataset to the Global Summary of the Day" in text,
        "current_version_label": "SSODv2" in text,
    }
    if not all(checks.values()):
        raise IdentityMismatch([k for k, accepted in checks.items() if not accepted])
    return {
        "dataset_id": ID, "edition": "Version 2", "dataset_title": TITLE,
        "identity_checks": checks, "observation_rows_read": 0,
        "station_records_downloaded": 0, "raw_data_licensed": False,
        "rights_and_attribution_review": "REQUIRED_FOR_ACTUAL_DATA",
        "scientific_results_tested": False,
    }


def observe(opener=None) -> dict:
    result = {
        "schema_version": 1, "provider": "NOAA NCEI Geoportal",
        "source_url": URL, "state": "SOURCE_WALL",
        "scientific_status": "NOT_TESTED", "source_kind": "dataset_catalog_metadata",
        "observations_downloaded": False, "station_files_downloaded": False,
        "raw_html_archived": False, "rights_review": "REQUIRED_PER_RECORD",
    }
    try:
        request = Request(URL, headers={"Accept": "text/html",
                           "User-Agent": "Independent-source-identity-observer/1.0"})
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("publisher metadata status not 200")
            raw = response.read(LIMIT + 1)
            observed = datetime.now(timezone.utc).isoformat()
        if len(raw) > LIMIT:
            raise ValueError("catalog exceeds metadata response limit")
        identity = classify(raw)
        result.update({
            "state": "PUBLIC_DATASET_METADATA_OBSERVED",
            "observed_at_utc": observed, "response_status": 200,
            "response_bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "identity": identity,
        })
    except (HTTPError, URLError, ValueError, TimeoutError, UnicodeError, OSError) as exc:
        result.update({"state": "SOURCE_WALL", "error_class": type(exc).__name__})
        if isinstance(exc, IdentityMismatch):
            result["failed_identity_checks"] = exc.failed
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = observe() if args.live else {
        "schema_version": 1, "state": "UNOBSERVED",
        "scientific_status": "NOT_TESTED", "reason": "no live probe requested",
    }
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 0 if not args.live or result["state"] == "PUBLIC_DATASET_METADATA_OBSERVED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
