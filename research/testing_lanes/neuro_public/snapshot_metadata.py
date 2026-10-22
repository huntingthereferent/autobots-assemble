"""One frozen, metadata-only public OpenNeuro snapshot query.

No raw imaging, filenames, subjects, behavioral tables, downloads, search,
user-supplied GraphQL, or credentialed access. Default is offline UNKNOWN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT = "https://openneuro.org/crn/graphql"
DATASET = "ds000224"
SNAPSHOT = "1.0.1"
DOI = "10.18112/openneuro.ds000224.v1.0.1"
MAX_BYTES = 60000
QUERY = '''query PublicDatasetSnapshotMetadata {
  dataset(id: "ds000224") { id name }
  snapshot(datasetId: "ds000224", tag: "1.0.1") {
    id tag description { Name DatasetDOI }
  }
}'''


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def classify(raw: bytes) -> dict:
    """Confirm exact documented identity, never inspect individual subject data."""
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict) or data.get("errors"):
        raise ValueError("GraphQL error or unexpected envelope")
    outer = data.get("data")
    if not isinstance(outer, dict):
        raise ValueError("GraphQL data missing")
    dataset = outer.get("dataset")
    snap = outer.get("snapshot")
    if not isinstance(dataset, dict) or not isinstance(snap, dict):
        raise ValueError("dataset or snapshot unavailable")
    description = snap.get("description")
    if not isinstance(description, dict):
        raise ValueError("snapshot description missing")
    if (dataset.get("id") != DATASET
            or snap.get("id") != DATASET + ":" + SNAPSHOT
            or snap.get("tag") != SNAPSHOT
            or description.get("DatasetDOI") != DOI):
        raise ValueError("snapshot identity or DOI mismatch")
    if not isinstance(dataset.get("name"), str) or not dataset["name"].strip():
        raise ValueError("dataset name missing")
    # Metadata-only: do not return even free-text names from the source.
    return {
        "dataset_id": DATASET, "snapshot_tag": SNAPSHOT, "snapshot_id": snap["id"],
        "doi": DOI, "metadata_fields_confirmed": ["dataset.id", "dataset.name",
        "snapshot.id", "snapshot.tag", "snapshot.description.DatasetDOI"],
        "source_data_admitted": False, "scientific_results_tested": False,
    }


def probe(*, opener=None) -> dict:
    receipt = {
        "schema_version": 1, "provider": "OpenNeuro",
        "endpoint": ENDPOINT, "source_id": DATASET,
        "version": SNAPSHOT, "state": "SOURCE_WALL",
        "scientific_status": "NOT_TESTED",
        "human_imaging_fetched": False,
        "source_data_archived": False,
        "rights_review": "REQUIRED_PER_RECORD",
        "query_mode": "fixed_public_metadata_only",
    }
    try:
        data = json.dumps({"query": QUERY}, separators=(",", ":")).encode("utf-8")
        request = Request(
            ENDPOINT, data=data, method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "User-Agent": "Independent-research-metadata-intake/1.0"},
        )
        client = opener if opener is not None else build_opener(NoRedirect)
        with client.open(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("non-200 metadata response")
            raw = response.read(MAX_BYTES + 1)
            observed = datetime.now(timezone.utc).isoformat()
        if len(raw) > MAX_BYTES:
            raise ValueError("metadata byte ceiling exceeded")
        observed_metadata = classify(raw)
        receipt.update({
            "state": "PUBLIC_SNAPSHOT_METADATA_OBSERVED",
            "observed_at_utc": observed, "response_status": 200,
            "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
            "raw_response_bytes": len(raw), "identity": observed_metadata,
        })
    except (HTTPError, URLError, ValueError, TimeoutError, OSError, UnicodeError) as err:
        receipt.update({"state": "SOURCE_WALL", "error_class": type(err).__name__})
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Make exactly one source POST")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    r = probe() if args.live else {
        "schema_version": 1, "state": "UNOBSERVED",
        "reason": "fixed public metadata request not executed",
        "scientific_status": "NOT_TESTED", "rights_review": "REQUIRED_PER_RECORD",
    }
    line = json.dumps(r, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(line, encoding="utf-8")
    print(line)
    return 0 if not args.live or r["state"] == "PUBLIC_SNAPSHOT_METADATA_OBSERVED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
