"""Bounded public-registry intake for NIH P2 temporal *source evidence*.

Reads only posting metadata from ClinicalTrials.gov's documented API v2,
preserves exact retrieval provenance and digests, and derives publication-event
availability cutoffs. It deliberately does NOT reconstruct historical versions,
test trial outcomes, use patient data, or claim a biomedical benchmark.

Separate exploratory source intake; NOT a thirteenth native workstation job.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import argparse
import json
import re

SCHEMA = "nih-p2-public-registry-posting-intake/v1"
BASE = "https://clinicaltrials.gov/api/v2/studies/"
FIELDS = "NCTId,StudyFirstPostDate,LastUpdatePostDate,ResultsFirstPostDate"
IDS = ("NCT04852770", "NCT04072276", "NCT02502409")
_ID = re.compile(r"NCT[0-9]{8}\Z")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
LIMIT = 65536
FIELDS_BY_EVENT = (
    ("first_posted", "studyFirstPostDateStruct"),
    ("last_update_posted", "lastUpdatePostDateStruct"),
    ("results_first_posted", "resultsFirstPostDateStruct"),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(value):
    return sha256(value).hexdigest()


def day(value):
    if type(value) is not str or not _DATE.fullmatch(value):
        raise ValueError("full, exact ISO posting date required")
    try:
        x = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("invalid public posting date") from error
    if x.isoformat() != value:
        raise ValueError("noncanonical posting date")
    return value


def source_url(nct_id):
    if type(nct_id) is not str or not _ID.fullmatch(nct_id):
        raise ValueError("exact public trial registration ID required")
    return BASE + nct_id + "?fields=" + FIELDS


def fetch_official(url):
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != "clinicaltrials.gov"
            or parts.port is not None or parts.username is not None
            or parts.password is not None or parts.fragment
            or not parts.path.startswith("/api/v2/studies/")):
        raise ValueError("no untrusted or non-official registry source")
    request = Request(url, headers={
        "User-Agent": "Original-Workstation-Research-Source-Witness/1.0",
        "Accept": "application/json",
    })
    with urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise ValueError("official registry did not return a successful record")
        if urlsplit(response.geturl()).hostname != "clinicaltrials.gov":
            raise ValueError("registry redirect left official source")
        raw = response.read(LIMIT + 1)
    if not raw or len(raw) > LIMIT:
        raise ValueError("official public metadata response exceeded safe intake limit")
    return raw


def extract(nct_id, raw, *, retrieved_at):
    """Return posting facts only, NOT historical recruitment status or clinical data."""
    source = source_url(nct_id)
    if type(raw) is not bytes or not 0 < len(raw) <= LIMIT:
        raise ValueError("bounded exact registry response bytes required")
    if type(retrieved_at) is not str or not retrieved_at.endswith("Z"):
        raise ValueError("UTC retrieval timestamp required")
    try:
        instant = datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid receipt timestamp") from e
    if instant.tzinfo is None or instant.utcoffset().total_seconds() != 0:
        raise ValueError("retrieval timestamp must be UTC")
    try:
        payload = json.loads(raw)
        protocol = payload["protocolSection"]
        identity = protocol["identificationModule"]["nctId"]
        status = protocol["statusModule"]
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise ValueError("official source lacks exact public status module") from e
    if identity != nct_id or type(status) is not dict:
        raise ValueError("requested registry ID does not match public content")

    events = []
    for name, field in FIELDS_BY_EVENT:
        entry = status.get(field)
        if entry is None:
            if name == "results_first_posted":
                continue  # Optional: missing means *no posted date claimed here*.
            raise ValueError("registry did not provide mandatory posting date")
        if type(entry) is not dict:
            raise ValueError("malformed public posting date")
        posted = day(entry.get("date"))
        events.append({
            "kind": name, "posted_on": posted, "nct_id": nct_id,
            "source_url": source, "source_path": "protocolSection.statusModule." + field + ".date",
        })

    mapping = {e["kind"]: e["posted_on"] for e in events}
    first = mapping["first_posted"]
    last = mapping["last_update_posted"]
    if last < first or ("results_first_posted" in mapping and
                        not first <= mapping["results_first_posted"] <= last):
        raise ValueError("contradictory posting-date order; evidence cannot be admitted")
    events.sort(key=lambda e: (e["posted_on"], e["kind"]))
    return {
        "nct_id": nct_id,
        "source_url": source,
        "retrieved_at_utc": retrieved_at,
        "raw_source_sha256": sha(raw),
        "posting_events": events,
        "record_kind": "current-registry-publication-metadata-only",
        "historical_content_available": False,
        "patient_data_ingested": False,
    }


def events_as_posted_as_of(records, cutoff):
    """No backdating any posting event; NOT a reconstruction of prior record text."""
    cutoff = day(cutoff)
    return sorted(
        ({"nct_id": r["nct_id"], "event": e["kind"], "posted_on": e["posted_on"]}
         for r in records for e in r["posting_events"] if e["posted_on"] <= cutoff),
        key=lambda x: (x["posted_on"], x["nct_id"], x["event"]),
    )


def execute(*, output_dir, fetch=fetch_official, ids=IDS, now=None):
    if type(ids) not in (list, tuple) or not 1 <= len(ids) <= 8 or len(set(ids)) != len(ids):
        raise ValueError("bounded distinct official study IDs required")
    observed = now or datetime.now(timezone.utc)
    if observed.tzinfo is None or observed.utcoffset().total_seconds() != 0:
        raise ValueError("source retrieval must be UTC")
    retrieved_at = observed.isoformat(timespec="seconds").replace("+00:00", "Z")
    records = []
    for nct_id in ids:
        url = source_url(nct_id)
        raw = fetch(url)
        records.append(extract(nct_id, raw, retrieved_at=retrieved_at))
    cutoffs = sorted({event["posted_on"] for rec in records for event in rec["posting_events"]})
    if len(cutoffs) < 2:
        raise ValueError("public registry sample lacks multiple observable publication dates")
    cutoffs = sorted(set(cutoffs + ["2000-01-01", observed.date().isoformat()]))
    frontiers = [{"as_of": cutoff,
                  "posting_events_visible": events_as_posted_as_of(records, cutoff)}
                 for cutoff in cutoffs]
    if any(not set((e["nct_id"], e["event"]) for e in a["posting_events_visible"])
           <= set((e["nct_id"], e["event"]) for e in b["posting_events_visible"])
           for a, b in zip(frontiers, frontiers[1:])):
        raise ValueError("publication events must not vanish at later cutoffs")
    report = {
        "schema": SCHEMA, "retrieved_at_utc": retrieved_at,
        "source": "ClinicalTrials.gov documented REST API v2",
        "official_api_base": BASE, "fields": FIELDS,
        "record_count": len(records), "records": records,
        "cutoff_frontiers": frontiers,
        "raw_public_responses_not_archived": True,
        "does_not_reconstruct_historical_version_contents": True,
        "known_at_interpretation": "registry-posted-event-date-only",
        "patient_data_ingested": False, "synthetic_observations": False,
        "external_source_intake_only": True, "biomedical_benchmark_complete": False,
        "clinical_verdict": "NOT_EVALUATED", "official_NIH_submission": False,
        "original_workstation_modified": False,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "nih-p2-public-registry-intake.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args(argv)
    result = execute(output_dir=args.output_dir)
    print(canonical({
        "schema": result["schema"], "record_count": result["record_count"],
        "retrieved_at_utc": result["retrieved_at_utc"],
        "observation_events": sum(len(x["posting_events"]) for x in result["records"]),
        "evidence_path": str(args.output_dir / "nih-p2-public-registry-intake.json"),
        "external_source_intake_only": True,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
