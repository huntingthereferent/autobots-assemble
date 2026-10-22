"""Fixed, metadata-only OECD SDMX dataflow identity, with no statistical data."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree as ET

URL = "https://sdmx.oecd.org/public/rest/dataflow/OECD.SDD.TPS/DSD_BOP%40DF_TIS/1.0?references=none"
AGENCY = "OECD.SDD.TPS"
FLOW = "DSD_BOP@DF_TIS"
VERSION = "1.0"
ACCEPT = "application/vnd.sdmx.structure+xml;version=2.1"
MAX_BYTES = 180000

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class IdentityMismatch(ValueError):
    def __init__(self, fields):
        self.fields = sorted(fields)
        super().__init__("expected publisher dataflow not identified")

def name(elem):
    return elem.tag.split("}")[-1] if isinstance(elem.tag, str) else ""

def classify(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("Document type and entities disallowed")
    root = ET.fromstring(raw)
    containers = [e for e in root.iter() if name(e) == "Dataflows"]
    flows = [e for c in containers for e in c if name(e) == "Dataflow"]
    expected = [e for e in flows if (e.attrib.get("id"), e.attrib.get("agencyID"), e.attrib.get("version")) == (FLOW, AGENCY, VERSION)]
    labels = [e for e in expected[0] if name(e) == "Name"] if len(expected) == 1 else []
    checks = {
        "sdmx_structure_root": name(root) == "Structure",
        "single_publisher_flow": len(flows) == 1,
        "exact_identity": len(expected) == 1,
        "named_flow": any((e.text or "").strip() for e in labels),
        "no_statistical_data": not any(name(e) in ("DataSet", "Series", "Obs", "Observation") for e in root.iter()),
    }
    if not all(checks.values()):
        raise IdentityMismatch([k for k, ok in checks.items() if not ok])
    return {"agency": AGENCY, "dataflow": FLOW, "version": VERSION,
            "identity_checks": checks, "statistical_rows_read": 0,
            "country_values_fetched": False, "scientific_status": "NOT_TESTED"}

def observe(opener=None):
    r = {"schema_version": 1, "provider": "OECD SDMX Data Explorer",
         "source_url": URL, "state": "SOURCE_WALL",
         "scope": "one_public_sdmx_structure_only", "scientific_status": "NOT_TESTED",
         "data_rows_downloaded": 0, "raw_source_archived": False,
         "rights_review": "REQUIRED_PER_RECORD"}
    try:
        req = Request(URL, headers={"Accept": ACCEPT, "User-Agent": "Research-source-metadata/1.0"})
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(req, timeout=15) as response:
            if response.status != 200:
                raise ValueError("unexpected HTTP status")
            raw = response.read(MAX_BYTES + 1)
            observed_at = datetime.now(timezone.utc).isoformat()
        if len(raw) > MAX_BYTES:
            raise ValueError("response too long")
        identity = classify(raw)
        r.update({"state": "PUBLIC_DATAFLOW_METADATA_OBSERVED", "response_status": 200,
                  "observed_at_utc": observed_at, "response_bytes": len(raw),
                  "response_sha256": hashlib.sha256(raw).hexdigest(), "identity": identity})
    except (HTTPError, URLError, ET.ParseError, ValueError, TimeoutError, OSError, UnicodeError) as err:
        r.update({"state": "SOURCE_WALL", "error_class": type(err).__name__})
        if isinstance(err, IdentityMismatch):
            r["failed_identity_checks"] = err.fields
    return r

def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--live", action="store_true")
    arg.add_argument("--output", type=Path)
    opts = arg.parse_args()
    result = observe() if opts.live else {"schema_version": 1, "state": "UNOBSERVED", "scientific_status": "NOT_TESTED"}
    content = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if opts.output:
        opts.output.parent.mkdir(parents=True, exist_ok=True)
        opts.output.write_text(content, encoding="utf-8")
    print(content)
    return 0 if not opts.live or result["state"] == "PUBLIC_DATAFLOW_METADATA_OBSERVED" else 2

if __name__ == "__main__":
    raise SystemExit(main())
