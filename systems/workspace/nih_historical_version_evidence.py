"""Fail-closed external historical *content* evidence intake for ClinicalTrials.gov.

This uses the site's internal history endpoints independently documented in
the ctrdata R source. Unlike the public API v2 current-record response,
each accepted response must identify an actual requested historical version.
These internal routes are NOT a stable documented public API: unavailable or
changed responses are recorded as UNAVAILABLE, never fabricated.

Publication/availability times are NOT derivable from version submission dates.
No clinical validity or NIH award/checkpoint is asserted.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.error import HTTPError
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SCHEMA = "nih-p2-clinicaltrials-exact-version-evidence/v1"
TRIAL_ID = "NCT03280849"
BASE = "https://www.clinicaltrials.gov/api/int/studies/"
ID = re.compile(r"NCT[0-9]{8}\Z")
ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
OVERVIEW_MAX = 256 * 1024
VERSION_MAX = 1024 * 1024


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), allow_nan=False)


def full_date(v):
    if type(v) is not str or not ISO.fullmatch(v):
        raise ValueError("version submission date is not exact ISO date")
    try:
        value = date.fromisoformat(v)
    except ValueError as exc:
        raise ValueError("invalid version submission date") from exc
    if value.isoformat() != v:
        raise ValueError("non-canonical version submission date")
    return v


def endpoint(nct_id, version=None):
    if type(nct_id) is not str or not ID.fullmatch(nct_id):
        raise ValueError("invalid registry study ID")
    root = BASE + nct_id
    if version is None:
        return root + "?history=true"
    if type(version) is not int or not 0 <= version <= 100000:
        raise ValueError("invalid historical version index")
    return root + "/history/" + str(version)


def http_fetch(url):
    # Called only with URLs constructed by endpoint(), never user-provided.
    u = urlsplit(url)
    if (u.scheme != "https" or u.hostname != "www.clinicaltrials.gov"
            or u.port is not None or not u.path.startswith("/api/int/studies/")
            or u.fragment or u.username or u.password):
        raise ValueError("outside exact official history origin")
    max_bytes = OVERVIEW_MAX if u.query == "history=true" else VERSION_MAX
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "ProcessWorkstation-Historical-Source-Evidence/1.0",
    })
    with urlopen(req, timeout=15) as result:
        if (result.status != 200
                or urlsplit(result.geturl()).hostname not in
                ("www.clinicaltrials.gov", "clinicaltrials.gov")):
            raise ValueError("history endpoint unavailable or redirected")
        data = result.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise ValueError("history source response absent or oversize")
    return data


def overview(nct_id, raw):
    endpoint(nct_id)
    if type(raw) is not bytes or not 0 < len(raw) <= OVERVIEW_MAX:
        raise ValueError("invalid bounded history index response")
    try:
        history = json.loads(raw)["history"]["changes"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("history index has no version change evidence") from exc
    if type(history) is not list or not 2 <= len(history) <= 10000:
        raise ValueError("at least two real source versions are required")
    changes = []
    for item in history:
        if type(item) is not dict:
            raise ValueError("invalid history change row")
        version = item.get("version")
        if type(version) is not int or not 0 <= version <= 100000:
            raise ValueError("history version index is missing")
        changes.append({"version": version, "submitted_on": full_date(item.get("date"))})
    if len({x["version"] for x in changes}) != len(changes):
        raise ValueError("duplicate source version")
    changes.sort(key=lambda x: x["version"])
    if any(a["submitted_on"] > b["submitted_on"] for a, b in zip(changes, changes[1:])):
        raise ValueError("impossible backward submission sequence")
    return changes


def historical_content(nct_id, version, submitted_on, raw, retrieved_at):
    url = endpoint(nct_id, version)
    full_date(submitted_on)
    if type(raw) is not bytes or not 0 < len(raw) <= VERSION_MAX:
        raise ValueError("version response missing or oversize")
    try:
        result = json.loads(raw)
        actual_version = result["studyVersion"]
        study = result["study"]
        study_id = study["protocolSection"]["identificationModule"]["nctId"]
        # A real content field from this exact historical version, NOT
        # rehydrated from the v2 current study endpoint.
        status = study["protocolSection"]["statusModule"]["overallStatus"]
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("requested version content not returned") from exc
    if (actual_version != version or type(actual_version) is not int
            or study_id != nct_id or type(status) is not str
            or not 1 <= len(status) <= 80):
        raise ValueError("historical version identity or selected field mismatch")
    return {
        "nct_id": nct_id,
        "source_version_index": version,
        "version_submitted_on": submitted_on,
        "source_url": url,
        "raw_source_sha256": sha256(raw).hexdigest(),
        "source_field": "study.protocolSection.statusModule.overallStatus",
        "selected_historical_field_value": status,
        "retrieved_at_utc": retrieved_at,
        "posted_on": None,  # submission date is NOT proof of publication.
        "historically_public_as_of_submission": "NOT_ESTABLISHED",
        "source_kind": "undocumented-site-internal-history-version",
    }


def execute(*, output_dir, fetch=http_fetch, nct_id=TRIAL_ID, now=None):
    """Store evidence only when two exact source versions can be authenticated."""
    start = now or datetime.now(timezone.utc)
    if start.tzinfo is None or start.utcoffset().total_seconds() != 0:
        raise ValueError("source read requires UTC observation time")
    retrieved_at = start.isoformat(timespec="seconds").replace("+00:00", "Z")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    index_url = endpoint(nct_id)
    raw_index = fetch(index_url)
    history = overview(nct_id, raw_index)
    requested = [history[0], history[-1]]
    receipts = []
    for entry in requested:
        raw_version = fetch(endpoint(nct_id, entry["version"]))
        receipts.append(historical_content(
            nct_id, entry["version"], entry["submitted_on"],
            raw_version, retrieved_at,
        ))
    if receipts[0]["raw_source_sha256"] == receipts[1]["raw_source_sha256"]:
        raise ValueError("different requested versions produced identical source bytes")
    result = {
        "schema": SCHEMA,
        "source_registry": "ClinicalTrials.gov",
        "internal_endpoints_not_stable_public_api": True,
        "index_url": index_url,
        "index_raw_sha256": sha256(raw_index).hexdigest(),
        "retrieved_at_utc": retrieved_at,
        "available_version_count_in_index": len(history),
        "two_exact_version_contents_retrieved": True,
        "historical_version_receipts": receipts,
        "raw_study_content_not_archived": True,
        "current_record_not_used_as_historical_version": True,
        "per_version_publication_date_proven": False,
        "historical_point_in_time_public_visibility_proven": False,
        "clinical_verdict": "NOT_EVALUATED",
        "official_NIH_submission": False,
        "additional_native_workstation_job": False,
        "workstation_journal_modified": False,
    }
    (out / "nih-p2-historical-version-receipts.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = execute(output_dir=args.output_dir)
    except HTTPError as error:
        # Fail the CI gate, but preserve the rejected source boundary as evidence.
        # A 403 is NOT a valid historical version response and cannot be used.
        receipt = {
            "schema": SCHEMA,
            "admission_status": "UNAVAILABLE",
            "source_url": endpoint(TRIAL_ID),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "http_status": error.code,
            "historical_version_contents_admitted": 0,
            "historical_point_in_time_public_visibility_proven": False,
            "no_substitute_current_record": True,
            "additional_native_workstation_job": False,
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "nih-p2-historical-source-unavailable.json").write_text(
            json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf8")
        raise SystemExit(f"UNAVAILABLE: exact historical source HTTP {error.code}; no version evidence admitted") from error
    print(canonical({
        "schema": SCHEMA,
        "source_version_count": len(result["historical_version_receipts"]),
        "historical_content_verified": True,
        "historical_publication_dates_verified": False,
        "output": str(args.output_dir / "nih-p2-historical-version-receipts.json"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
