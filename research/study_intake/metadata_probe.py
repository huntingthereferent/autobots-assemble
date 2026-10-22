"""Bounded two-source bibliographic identity witness, NOT a scientific replication.

Default command is offline. Explicit --live enables at most one GET each to
Crossref and OpenAlex, no external links, pages, downloads, or arbitrary URLs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "studies" / "OSC-2015.json"
DOI_PATTERN = re.compile(r"10\.[0-9]{4,9}/[A-Za-z0-9._;()/:\-]+", re.ASCII)
MAX_RESPONSE_BYTES = 2_000_000
ENDPOINT_HOSTS = {"crossref": "api.crossref.org", "openalex": "api.openalex.org"}
USER_AGENT = "AEREN-research-metadata-probe/1.0 (https://github.com/huntingthereferent/autobots-assemble)"


def read_study(path: Path = STUDY) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    doi = record.get("doi", "")
    if (record.get("schema_version") != 1 or
            not isinstance(doi, str) or not DOI_PATTERN.fullmatch(doi) or
            not isinstance(record.get("year"), int) or
            not isinstance(record.get("title"), str) or not record["title"].strip()):
        raise ValueError("invalid frozen study record")
    return record


def canonical_doi(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    return text if DOI_PATTERN.fullmatch(text) else None


def normalized_title(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    result = " ".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return result or None


def source_url(source: str, doi: str) -> str:
    if source not in ENDPOINT_HOSTS or not DOI_PATTERN.fullmatch(doi):
        raise ValueError("unregistered source or invalid DOI")
    if source == "crossref":
        return "https://api.crossref.org/works/" + quote(doi, safe="/")
    return "https://api.openalex.org/works/https://doi.org/" + quote(doi, safe="/")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_one(source: str, study: dict, *, opener=None) -> dict:
    """Fetch exactly one source response. Return bounded provenance plus fields."""
    url = source_url(source, study["doi"])
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != ENDPOINT_HOSTS[source]:
        raise ValueError("unexpected metadata host")
    req = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    client = opener if opener is not None else build_opener(NoRedirect)
    with client.open(req, timeout=15) as response:
        if response.status != 200:
            raise ValueError("unexpected response status")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("metadata response above bound")
        observed = datetime.now(timezone.utc).isoformat()
    payload = json.loads(raw.decode("utf-8"))
    normalized = parse_metadata(source, payload)
    return {
        "source": source,
        "url": url,
        "observed_at_utc": observed,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "response_bytes": len(raw),
        "metadata": normalized,
        "raw_body_archived": False,
    }


def parse_metadata(source: str, payload: dict) -> dict:
    """Whitelist only bibliographic identity fields, never copyright abstracts."""
    if not isinstance(payload, dict):
        raise ValueError("source payload must be an object")
    if source == "crossref":
        work = payload.get("message")
        if not isinstance(work, dict):
            raise ValueError("Crossref message missing")
        title = work.get("title")
        title = title[0] if isinstance(title, list) and title else None
        dates = work.get("published") or work.get("issued") or {}
        parts = dates.get("date-parts") if isinstance(dates, dict) else None
        year = parts[0][0] if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0] else None
        return {
            "doi": canonical_doi(work.get("DOI")),
            "title": title,
            "year": year,
            "source_updated": (work.get("deposited") or {}).get("date-time"),
        }
    if source == "openalex":
        return {
            "doi": canonical_doi(payload.get("doi")),
            "title": payload.get("title") or payload.get("display_name"),
            "year": payload.get("publication_year"),
            "source_updated": payload.get("updated_date"),
        }
    raise ValueError("unregistered metadata type")


def reconcile(study: dict, records: list[dict]) -> dict:
    """Identity comparison only. UNKNOWN if either source absent or invalid."""
    expected = {
        "doi": canonical_doi(study["doi"]),
        "title": normalized_title(study["title"]),
        "year": study["year"],
    }
    if len(records) != 2 or {x.get("source") for x in records} != set(ENDPOINT_HOSTS):
        return {"state": "UNKNOWN", "reason": "both independent sources required", "comparisons": []}
    comparisons = []
    for source_record in records:
        m = source_record["metadata"]
        observed = {
            "doi": canonical_doi(m.get("doi")),
            "title": normalized_title(m.get("title")),
            "year": m.get("year"),
        }
        fields = {name: observed[name] == target and observed[name] is not None
                  for name, target in expected.items()}
        comparisons.append({"source": source_record["source"], "fields_equal_to_frozen_record": fields})
    fully_matched = all(all(c["fields_equal_to_frozen_record"].values()) for c in comparisons)
    return {
        "state": "MATCH" if fully_matched else "MISMATCH",
        "reason": "bibliographic identifiers and fields, not study outcomes",
        "comparisons": sorted(comparisons, key=lambda x: x["source"]),
    }


def probe(study: dict, *, live: bool = False, opener=None) -> dict:
    receipt = {
        "schema_version": 1,
        "study_id": study["id"],
        "doi": study["doi"],
        "scientific_evidence_status": "NOT_REPRODUCED",
        "source_receipts": [],
        "errors": [],
    }
    if not live:
        receipt["identity_comparison"] = {"state": "UNOBSERVED", "reason": "live fetch disabled"}
        return receipt
    for source in ("crossref", "openalex"):
        try:
            receipt["source_receipts"].append(fetch_one(source, study, opener=opener))
        except (HTTPError, URLError, ValueError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            receipt["errors"].append({"source": source, "error_type": type(exc).__name__})
    receipt["identity_comparison"] = reconcile(study, receipt["source_receipts"])
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly enable two bounded source GETs")
    parser.add_argument("--output", type=Path, help="Optional JSON receipt output path")
    args = parser.parse_args()
    receipt = probe(read_study(), live=args.live)
    output = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    if args.live and receipt["identity_comparison"]["state"] != "MATCH":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
