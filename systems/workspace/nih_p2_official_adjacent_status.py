"""Adjacent original-source observation: NCT00001756 historical V259 and V260.

A public Chromium source observation, not a new W13 worker or a model for
NIH effectiveness. Exact original version identity is required before any
comparison. Historical Last Update Posted labels are recorded as source
fields; no version-first-public known_at is generated from them.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

from . import nih_p2_official_history_browser_access as source
from . import nih_p2_official_history_status_fields as earlier

SCHEMA = "nih-p2-official-adjacent-original-status/v1"
# Predeclared adjacent source versions. If V259 submission date is incorrect,\n# live source admission must refuse the record, never silently change it.\nVERSIONS = {259: "2022-10-26", 260: "2022-11-04"}
STATUS = earlier.VALID_STATUS
POSTED = earlier.POSTED
DAY = earlier.DAY
SECTIONS = ("Study Details", "Study Identification", "Study Status", "Sponsor/Collaborators")
FIELDS = earlier.LABELS


def version_url(version: int) -> str:
    if type(version) is not int or version not in VERSIONS:
        raise ValueError("only two predeclared official versions admitted")
    return f"https://{source.HOST}/study/{source.NCT}?a={version}&tab=history"


def admit_source(*, version: int, url: str, body: str, status: int | None,
                 retrieved_utc: str) -> dict:
    """Never accept search snippets, altered query, current summary or wrong version."""
    expected = version_url(version)
    target = urlsplit(url)
    query = parse_qs(target.query, keep_blank_values=True)
    if (target.scheme != "https" or target.hostname != source.HOST or
        target.path != f"/study/{source.NCT}" or
        query != {"a": [str(version)], "tab": ["history"]} or
        target.port is not None or target.username is not None or
        target.password is not None or target.fragment or url != expected or
        status != 200):
        raise ValueError("no witnessed original official selected-version route")
    if type(body) is not str or len(body) > source.MAX_BODY:
        raise ValueError("missing or excessive original browser text")
    for required in (source.NCT, source.TITLE, "Study Record Versions", "Study Details"):
        if required not in body:
            raise ValueError("original study identity/history page not rendered")
    if any(marker in body.casefold() for marker in source.INACCESSIBLE):
        raise ValueError("original page is blocked or challenged")

    stamp = datetime.fromisoformat(retrieved_utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("no timezone-aware source observation")
    lines = [s.strip() for s in body.splitlines() if s.strip()]
    exact = re.compile(rf"Viewing\s+V{version}\s*\((\d{{4}}-\d{{2}}-\d{{2}})\)\Z")
    banners = [(i, m) for i, line in enumerate(lines) if (m := exact.fullmatch(line))]
    if len(banners) != 1:
        raise ValueError("no single exact original historical-version banner")
    selected_index, selected = banners[0]
    submission = earlier.normalized_day(selected.group(1))
    if submission != VERSIONS[version]:
        raise ValueError("selected version submission differs from original index")
    # Only inspect AFTER the selected banner. Earlier current-summary text
    # and history-index rows cannot satisfy a source-field claim.
    tail = lines[selected_index + 1:]
    indices = {}
    for header in SECTIONS:
        hits = [i for i, text in enumerate(tail) if text == header]
        if len(hits) != 1:
            raise ValueError("missing or ambiguous original section " + header)
        indices[header] = hits[0]
    if not all(indices[a] < indices[b] for a, b in zip(SECTIONS, SECTIONS[1:])):
        raise ValueError("historical source sections are not in original order")
    part = tail[indices["Study Status"] + 1:indices["Sponsor/Collaborators"]]
    raw_status = earlier.field_value(part, "Overall Status")
    if raw_status not in STATUS:
        raise ValueError("unrecognized original recruitment status")
    qc = earlier.normalized_day(earlier.field_value(
        part, "Last Update Submitted that Met QC Criteria"))
    posted_text = earlier.field_value(part, "Last Update Posted")
    m = POSTED.fullmatch(posted_text)
    if m is None:
        raise ValueError("source posted date or its Actual/Estimated mark unavailable")
    posted_day = earlier.normalized_day(m.group(1))
    if posted_day < qc or date.fromisoformat(posted_day) > stamp.date():
        raise ValueError("source posted date not compatible with witnessed sequence")
    # A version banner may be a submitted date and a posted date may be an
    # update-available date: neither proves the version's first-public time.
    return {
        "version": version, "source_url": expected,
        "submitted_in_original_selected_version": submission,
        "observed_overall_status": raw_status,
        "observed_version_local_qc_submitted": qc,
        "observed_version_local_last_update_posted": posted_day,
        "posted_date_qualifier": m.group(2),
        "retrieved_utc": retrieved_utc,
        "original_visible_text_sha256": sha256(body.encode("utf8")).hexdigest(),
        "version_local_status_section_sha256": sha256(
            "\n".join(part).encode("utf8")).hexdigest(),
        "original_version_fields_witnessed": True,
        "first_public_version_timestamp_independently_authenticated": False,
        "clinical_result_inferred": False,
    }


def summarize(rows: list[dict]) -> dict:
    if type(rows) is not list or len(rows) != 2:
        raise ValueError("exact two original source rows required")
    if [x.get("version") for x in rows] != list(VERSIONS):
        raise ValueError("original historical versions missing or misordered")
    for row in rows:
        if row.get("first_public_version_timestamp_independently_authenticated") is not False:
            raise ValueError("unsupported version first-public time promoted")
    present = all(row.get("original_version_fields_witnessed") is True for row in rows)
    changed = (rows[0]["observed_overall_status"] != rows[1]["observed_overall_status"]
               if present else None)
    return {
        "schema": SCHEMA,
        "adjacent_version_pair_checked": True,
        "source_owner": "ClinicalTrials.gov / U.S. National Library of Medicine",
        "study": source.NCT,
        "records": rows,
        "two_original_version_fields_witnessed": present,
        "observed_status_changed": changed,
        "first_public_version_timestamp": "UNAVAILABLE",
        "known_at_admitted_to_W13": False,
        "historical_temporal_benchmark_completed": False,
        "original_twelve_job_W13_modified": False,
        "nih_submission_or_clinical_verdict": False,
    }


def run(*, out_dir: Path) -> dict:
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    found = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1100, "height": 900})
            for version in VERSIONS:
                url = version_url(version)
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    status = response.status if response else None
                    if status == 200:
                        page.wait_for_function(
                            "(v)=>document.body?.innerText?.includes('Viewing V' + v + ' ')",
                            arg=version, timeout=18000)
                    body = page.locator("body").inner_text(timeout=12000)
                    result = admit_source(version=version, url=page.url,
                        body=body, status=status,
                        retrieved_utc=datetime.now(timezone.utc).isoformat())
                except (BrowserTimeout, ValueError, KeyError, TypeError) as exc:
                    result = {"version": version, "source_url": url,
                        "result": "UNAVAILABLE", "reason_class": type(exc).__name__,
                        "original_version_fields_witnessed": False,
                        "first_public_version_timestamp_independently_authenticated": False}
                found.append(result)
        finally:
            browser.close()
    result = summarize(found)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "original-status-contrast.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()
    result = run(out_dir=a.out_dir)
    print(json.dumps({
        "two_original_version_fields_witnessed":
            result["two_original_version_fields_witnessed"],
        "observed_status_changed": result["observed_status_changed"],
        "first_public_version_timestamp": result["first_public_version_timestamp"],
    }, sort_keys=True))
    if not result["two_original_version_fields_witnessed"]:
        raise SystemExit("UNAVAILABLE: exact public historical version could not be authenticated")
    # No difference is a valid observed result here. Do not claim the\n    # earlier V105/V260 contrast identifies this adjacent boundary.


if __name__ == "__main__":
    main()
