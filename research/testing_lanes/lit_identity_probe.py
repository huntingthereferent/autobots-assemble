"""One fixed cross-index DOI identity check for the LIT lane.

Default is offline. --live queries one Crossref DOI, one OpenAlex DOI record,
and one PubMed PMID. It stores bounded metadata receipts and hashes only;
it does not retrieve full text or evaluate the paper's scientific claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DOI = "10.1126/science.aac4716"
PMID = "26315443"
ENDPOINTS = {
    "crossref": f"https://api.crossref.org/works/{DOI}",
    "openalex": f"https://api.openalex.org/works/https://doi.org/{DOI}",
    "pubmed": f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={PMID}&retmode=xml",
}
MAX_BYTES = 250_000
TIMEOUT = 15


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return "".join(ch for ch in value if ch.isalnum())


def parse_crossref(raw: bytes) -> dict:
    payload = json.loads(raw.decode("utf-8-sig"))
    message = payload.get("message") if isinstance(payload, dict) else None
    if not isinstance(message, dict):
        raise ValueError("Crossref message missing")
    doi = str(message.get("DOI", "")).lower()
    title = message.get("title")
    if doi != DOI or not isinstance(title, list) or not title or not isinstance(title[0], str):
        raise ValueError("Crossref DOI/title did not match pinned record")
    return {"doi": doi, "title": title[0], "comparison_title": title[0]}


def parse_openalex(raw: bytes) -> dict:
    payload = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("OpenAlex work missing")
    doi = str(payload.get("doi", "")).lower().replace("https://doi.org/", "")
    title = payload.get("title")
    if doi != DOI or not isinstance(title, str) or not title.strip():
        raise ValueError("OpenAlex DOI/title did not match pinned record")
    return {"doi": doi, "title": title, "comparison_title": title}


def parse_pubmed(raw: bytes) -> dict:
    root = ET.fromstring(raw)
    records = root.findall(".//PubmedArticle")
    if len(records) != 1:
        raise ValueError("PubMed did not return exactly one article")
    record = records[0]
    pmid = (record.findtext(".//PMID") or "").strip()
    title_node = record.find(".//ArticleTitle")
    if pmid != PMID or title_node is None:
        raise ValueError("PubMed PMID/title did not match pinned record")
    title = "".join(title_node.itertext()).strip()
    doi = ""
    for node in record.findall(".//ArticleId"):
        if node.attrib.get("IdType", "").lower() == "doi":
            doi = (node.text or "").strip().lower()
            break
    if doi != DOI or not title:
        raise ValueError("PubMed DOI/title did not match pinned record")
    # PubMed may prefix an article with a section label, e.g. "PSYCHOLOGY."
    # Preserve the original title but remove that label only for cross-index comparison.
    comparison_title = title
    if "." in title:
        prefix, remainder = title.split(".", 1)
        letters = [ch for ch in prefix if ch.isalpha()]
        if letters and len(prefix) <= 40 and all(ch.isupper() for ch in letters) and remainder.strip():
            comparison_title = remainder.strip()
    return {"pmid": pmid, "doi": doi, "title": title, "comparison_title": comparison_title}


PARSERS = {"crossref": parse_crossref, "openalex": parse_openalex, "pubmed": parse_pubmed}


def inspect_payloads(payloads: dict[str, bytes]) -> dict:
    """Pure evaluator used by offline tests; preserve per-source walls."""
    receipt = {
        "schema_version": 1,
        "lane_id": "LIT",
        "experiment_id": "LIT-DOI-001",
        "scope": "One frozen scholarly record identity across Crossref, OpenAlex and PubMed; metadata only.",
        "pinned_doi": DOI,
        "pinned_pmid": PMID,
        "scientific_claim_tested": False,
        "full_text_fetched": False,
        "source_data_archived": False,
        "state": "SOURCE_WALL",
        "sources": {},
    }
    parsed = {}
    for source_id in PARSERS:
        raw = payloads.get(source_id)
        if raw is None:
            receipt["sources"][source_id] = {"state": "MISSING_INPUT"}
            continue
        try:
            data = PARSERS[source_id](raw)
            parsed[source_id] = data
            receipt["sources"][source_id] = {
                "state": "IDENTITY_OBSERVED",
                "response_bytes": len(raw),
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "doi": data["doi"],
                "title": data["title"],
                "normalized_title": normalize_title(data.get("comparison_title", data["title"])),
                **({"pmid": data["pmid"]} if "pmid" in data else {}),
            }
        except (ValueError, KeyError, TypeError, ET.ParseError, UnicodeError, json.JSONDecodeError) as exc:
            receipt["sources"][source_id] = {
                "state": "IDENTITY_WALL",
                "response_bytes": len(raw),
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "error_class": type(exc).__name__,
            }
    if len(parsed) != len(PARSERS):
        receipt["state"] = "SOURCE_WALL"
        return receipt
    titles = {normalize_title(item.get("comparison_title", item["title"])) for item in parsed.values()}
    dois = {item["doi"].lower() for item in parsed.values()}
    if len(titles) != 1 or dois != {DOI}:
        receipt["state"] = "IDENTITY_CONFLICT"
        return receipt
    receipt["state"] = "IDENTITY_MATCH"
    receipt["matched_fields"] = ["DOI", "normalized title"]
    return receipt


def live_probe(opener=None) -> dict:
    payloads = {}
    fetches = {}
    client = opener if opener is not None else build_opener(NoRedirect)
    for source_id, url in ENDPOINTS.items():
        try:
            request = Request(url, headers={
                "Accept": "application/json, application/xml;q=0.9",
                "User-Agent": "Aeren-LIT-identity-probe/1.0",
            })
            with client.open(request, timeout=TIMEOUT) as response:
                if response.status != 200:
                    raise ValueError("non-200 response")
                raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("response byte ceiling exceeded")
            payloads[source_id] = raw
            fetches[source_id] = {"endpoint": url, "http_status": 200}
        except (HTTPError, URLError, ValueError, TimeoutError, OSError) as exc:
            fetches[source_id] = {
                "endpoint": url, "state": "SOURCE_WALL", "error_class": type(exc).__name__
            }
    receipt = inspect_payloads(payloads)
    receipt.update({
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "fetches": fetches,
        "retrieval_policy": {"max_bytes_per_source": MAX_BYTES, "timeout_seconds": TIMEOUT, "redirects": "denied"},
    })
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Make three fixed public metadata requests")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.live:
        receipt = live_probe()
    else:
        receipt = {
            "schema_version": 1, "lane_id": "LIT", "experiment_id": "LIT-DOI-001",
            "state": "UNOBSERVED", "pinned_doi": DOI, "pinned_pmid": PMID,
            "scientific_claim_tested": False, "reason": "offline default; pass --live to query metadata",
        }
    output = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 0 if receipt["state"] in {"UNOBSERVED", "IDENTITY_MATCH"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
