"""SEC-CVE-METADATA-001: validate one public NVD record, without testing a target.

This checks record identity and metadata shape only. It does not test exploitability,
run a scanner, contact any target, or establish that a deployment is vulnerable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

CVE_ID = "CVE-2021-44228"
ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=" + CVE_ID
MAX_RESPONSE_BYTES = 2_000_000


def validate_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("response root must be an object")
    vulnerabilities = payload.get("vulnerabilities")
    if payload.get("totalResults") != 1 or not isinstance(vulnerabilities, list) or len(vulnerabilities) != 1:
        raise ValueError("expected exactly one result for the pinned CVE query")
    cve = vulnerabilities[0].get("cve") if isinstance(vulnerabilities[0], dict) else None
    if not isinstance(cve, dict) or cve.get("id") != CVE_ID:
        raise ValueError("returned CVE identity does not match the pinned identifier")
    published = cve.get("published")
    modified = cve.get("lastModified")
    descriptions = cve.get("descriptions")
    if not isinstance(published, str) or not isinstance(modified, str):
        raise ValueError("publication or modification timestamp missing")
    if not isinstance(descriptions, list) or not descriptions:
        raise ValueError("description metadata missing")
    metrics = cve.get("metrics") if isinstance(cve.get("metrics"), dict) else {}
    cwe_ids = sorted({
        item.get("value")
        for weakness in cve.get("weaknesses", [])
        if isinstance(weakness, dict)
        for item in weakness.get("description", [])
        if isinstance(item, dict) and isinstance(item.get("value"), str) and item["value"].startswith("CWE-")
    })
    return {
        "cve_id": cve["id"],
        "published": published,
        "last_modified": modified,
        "description_languages": sorted({
            item.get("lang") for item in descriptions
            if isinstance(item, dict) and isinstance(item.get("lang"), str)
        }),
        "cvss_metric_families": sorted(metrics.keys()),
        "cwe_ids": cwe_ids,
    }


def fetch_payload() -> tuple[dict, str]:
    request = Request(ENDPOINT, headers={"User-Agent": "bounded-research-witness/1.0"})
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"NVD returned HTTP {response.status}")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("response exceeded the configured byte cap")
    digest = hashlib.sha256(raw).hexdigest()
    return json.loads(raw.decode("utf-8")), digest


def build_receipt(payload: dict, raw_sha256: str) -> dict:
    record = validate_payload(payload)
    return {
        "schema_version": 1,
        "experiment_id": "SEC-CVE-METADATA-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RECORD_SHAPE_PASS",
        "source": {"name": "NIST National Vulnerability Database", "endpoint": ENDPOINT,
                   "http_response_sha256": raw_sha256, "max_response_bytes": MAX_RESPONSE_BYTES},
        "record": record,
        "limits": [
            "Metadata identity/shape only; no affected product or version was evaluated.",
            "A CVE record does not establish that any particular system is vulnerable.",
            "No exploit code, scanning, target access, or third-party testing is performed.",
            "NVD fields and scoring may change; this receipt is a dated snapshot, not a timeless verdict."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload, digest = fetch_payload()
    receipt = build_receipt(payload, digest)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
