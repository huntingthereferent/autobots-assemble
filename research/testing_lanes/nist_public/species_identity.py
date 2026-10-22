"""Observe one NIST Chemistry WebBook species identity, not reference tables.

Default offline. Explicit --live does one no-redirect fixed HTTPS GET and preserves
only a hash plus five public identity assertions; no compiled property tables,
spectra, or NIST data content is retained or licensed by the observation.
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
from urllib.request import HTTPRedirectHandler, Request, build_opener

URL = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Units=SI"
CAS = "7732-18-5"
NAME = "Water"
FORMULA = "H2O"
MOLECULAR_WEIGHT = "18.0153"
INCHI_KEY = "XLYOFNOQVPJJNP-UHFFFAOYSA-N"
MAX_BYTES = 400000


class IdentityMismatch(ValueError):
    """Only names of failed local identity predicates, never publisher text."""

    def __init__(self, missing):
        self.missing = sorted(missing)
        super().__init__("source species identity mismatch")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class VisibleHtml(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.headings = []
        self.omit = 0
        self.h1_parts = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.omit += 1
        if tag == "h1":
            self.h1_parts = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.omit:
            self.omit -= 1
        if tag == "h1" and self.h1_parts is not None:
            self.headings.append(" ".join(" ".join(self.h1_parts).split()))
            self.h1_parts = None

    def handle_data(self, text):
        if not self.omit:
            self.parts.append(text)
            if self.h1_parts is not None:
                self.h1_parts.append(text)


def classify(raw: bytes) -> dict:
    try:
        html = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("not UTF-8 source identity") from error
    parser = VisibleHtml()
    parser.feed(html)
    rendered = " ".join(" ".join(parser.parts).split())
    headings = parser.headings
    checks = {
        "publisher_webbook": "NIST Chemistry WebBook" in rendered,
        "species_name": NAME in headings,
        "cas_id": bool(re.search(r"\bCAS Registry Number\s*:\s*7732-18-5\b", rendered, re.I)),
        "formula": bool(re.search(r"\bFormula\s*:\s*H\s*2\s*O(?=\s*(?:Molecular weight|IUPAC Standard|CAS Registry Number|$))", rendered, re.I)),
        "inchi_key": INCHI_KEY in rendered,
    }
    if not all(checks.values()):
        raise IdentityMismatch([key for key, passed in checks.items() if not passed])
    # Molecular weight appears in the document, but isn't admitted as a
    # reference measurement or used as a pass criterion.
    return {
        "species": NAME,
        "cas_registry_number": CAS,
        "molecular_formula": FORMULA,
        "inchi_key": INCHI_KEY,
        "metadata_identity_checks": checks,
        "scientific_measurements_admitted": 0,
        "property_tables_copied": False,
        "source_reuse_rights_review": "REQUIRED_PER_RECORD",
    }


def observe(opener=None) -> dict:
    result = {
        "schema_version": 1,
        "provider": "NIST Chemistry WebBook SRD 69",
        "species_identity_url": URL,
        "state": "SOURCE_WALL",
        "scope": "one_public_species_identity_only",
        "scientific_status": "NOT_TESTED",
        "measurements_downloaded": False,
        "data_compilation_copied": False,
        "rights_review": "REQUIRED_PER_RECORD",
    }
    try:
        request = Request(URL, headers={
            "Accept": "text/html",
            "User-Agent": "Independent-source-identity-observer/1.0",
        })
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("publisher species page HTTP not 200")
            raw = response.read(MAX_BYTES + 1)
            observed = datetime.now(timezone.utc).isoformat()
        if len(raw) > MAX_BYTES:
            raise ValueError("publisher response over byte ceiling")
        identity = classify(raw)
        result.update({
            "state": "PUBLIC_SPECIES_METADATA_OBSERVED",
            "observed_at_utc": observed,
            "response_status": 200,
            "response_bytes": len(raw),
            "body_sha256": hashlib.sha256(raw).hexdigest(),
            "identity": identity,
        })
    except (HTTPError, URLError, ValueError, TimeoutError, UnicodeError, OSError) as error:
        result.update({"state": "SOURCE_WALL", "error_class": type(error).__name__})
        if isinstance(error, IdentityMismatch):
            result["failed_identity_checks"] = error.missing
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = observe() if args.live else {
        "schema_version": 1, "state": "UNOBSERVED",
        "scientific_status": "NOT_TESTED", "reason": "no live observation requested",
    }
    line = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(line, encoding="utf-8")
    print(line)
    return 0 if not args.live or result["state"] == "PUBLIC_SPECIES_METADATA_OBSERVED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
