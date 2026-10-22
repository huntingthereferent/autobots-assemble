"""NEURO source gate: exact PUBLIC OpenNeuro snapshot metadata only.

No file download, image/subject metadata, private dataset, authenticated query,
GraphQL mutation, participant measurement, or scientific effect claim.
The existing per-dataset rights/ethics gate remains required for experiment use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT = "https://openneuro.org/crn/graphql"
DATASET = "ds000224"
SNAPSHOT = "1.0.1"
REQUIRED_ID = "ds000224:1.0.1"
REQUIRED_DOI = "10.18112/openneuro.ds000224.v1.0.1"
QUERY = """query SnapshotMetadataOnly {
  snapshot(datasetId: "ds000224", tag: "1.0.1") {
    id
    tag
    description {
      Name
      DatasetDOI
    }
  }
}"""
MAX_BYTES = 16000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_metadata(opener=None) -> bytes:
    url = urlsplit(ENDPOINT)
    if (url.scheme != "https" or url.hostname != "openneuro.org" or
            url.path != "/crn/graphql" or url.username or url.password):
        raise ValueError("unexpected source domain")
    payload = json.dumps({"query": QUERY}, separators=(",", ":")).encode("utf-8")
    client = opener if opener is not None else build_opener(NoRedirect)
    request = Request(ENDPOINT, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "HuntingReferentResearch/1.0 snapshot-metadata-only",
    })
    with client.open(request, timeout=20) as response:
        if response.status != 200 or response.geturl() != ENDPOINT:
            raise ValueError("source did not return exact HTTPS response")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("source metadata exceeds bounded limit")
    return raw


def parse_metadata(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict) or data.get("errors"):
        raise ValueError("GraphQL source errors or missing response")
    root = data.get("data") or {}
    snapshot = root.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("public snapshot not found")
    if snapshot.get("id") != REQUIRED_ID or snapshot.get("tag") != SNAPSHOT:
        raise ValueError("wrong dataset snapshot version")
    description = snapshot.get("description")
    if not isinstance(description, dict):
        raise ValueError("public snapshot missing DOI description")
    if description.get("DatasetDOI") != REQUIRED_DOI:
        raise ValueError("source DOI mismatch")
    title = description.get("Name")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("missing official dataset name")
    return {"dataset_id": DATASET, "snapshot": SNAPSHOT, "doi": REQUIRED_DOI,
            "name": title.strip()}


def live():
    raw = request_metadata()
    source = parse_metadata(raw)
    return {
        "schema_version": 1,
        "lane_id": "NEURO",
        "source_family": "openneuro",
        "state": "PUBLIC_SNAPSHOT_METADATA_OBSERVED",
        "source_url": ENDPOINT,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "query_sha256": hashlib.sha256(QUERY.encode()).hexdigest(),
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "metadata": source,
        "scientific_experiments_run": 0,
        "downloaded_dataset_files": 0,
        "rights_privacy_review_status": "REQUIRED_BEFORE_DATASET_ADMISSION",
        "next_gate": (
            "Review snapshot-specific license/BIDS content, de-identification, "
            "population, analytic design, processing, sample rules and approval "
            "before fetching any participant-level data."
        ),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live", action="store_true")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = {"schema_version": 1, "lane_id": "NEURO",
              "state": "UNOBSERVED", "scientific_experiments_run": 0}
    if a.live:
        try:
            result = live()
        except (HTTPError, URLError, OSError, ValueError, UnicodeError,
                TimeoutError, json.JSONDecodeError) as exc:
            result = {"schema_version": 1, "lane_id": "NEURO", "state": "SOURCE_WALL",
                      "source_url": ENDPOINT, "scientific_experiments_run": 0,
                      "error_class": type(exc).__name__, "error": str(exc)[:180]}
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(output, encoding="utf-8")
    print(output)
    return 2 if result["state"] == "SOURCE_WALL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
