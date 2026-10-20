"""Inspect minimal Study Status fields within official historical version views.

Builds on PR #151's independent public-browser banner and route gate. Read the
historical section after the selected Viewing Vnn banner, never the current
study header or the list of versions. Retains no original page body.
An observed 'Last Update Posted' field is not on its own proof of the first
public posting time of every historical version. No private clinical data.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

from . import nih_p2_official_history_browser_access as ui

SCHEMA = "nih-p2-official-version-specific-status-fields/v1"
DAY = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
POSTED = re.compile(r"(\d{4}-\d{2}-\d{2})\s*\[(Actual|Estimated)\]\Z")
VALID_STATUS = frozenset({
    "Not yet recruiting", "Recruiting", "Enrolling by invitation",
    "Active, not recruiting", "Suspended", "Terminated", "Completed",
    "Withdrawn", "Unknown status",
})
LABELS = (
    "Overall Status",
    "Last Update Submitted that Met QC Criteria",
    "Last Update Posted",
)


def normalized_day(raw: str) -> str:
    if type(raw) is not str or not DAY.fullmatch(raw):
        raise ValueError("not a literal canonical day")
    if date.fromisoformat(raw).isoformat() != raw:
        raise ValueError("noncanonical calendar day")
    return raw


def field_value(lines: list[str], label: str) -> str:
    matches = [i for i, value in enumerate(lines) if value == label]
    if len(matches) != 1 or matches[0] + 1 >= len(lines):
        raise ValueError("missing/duplicated version-local field: " + label)
    next_value = lines[matches[0] + 1]
    if next_value in LABELS or not next_value or len(next_value) > 100:
        raise ValueError("invalid version-local value: " + label)
    return next_value


def extract_version_field(*, receipt: dict, body_text: str) -> dict:
    """Fail closed unless version route was *already* observed on original UI."""
    version = receipt.get("requested_version")
    if version not in ui.VERSIONS or type(version) is not int:
        raise ValueError("unsupported historical version")
    if receipt.get("actual_original_version_rendered") is not True:
        raise ValueError("original selected version view was not witnessed")
    if receipt.get("selected_exact_original_route") is not True:
        raise ValueError("historical source route not admitted")
    if type(body_text) is not str or len(body_text) > ui.MAX_BODY:
        raise ValueError("missing or oversized original browser text")
    body_sha = sha256(body_text.encode("utf8")).hexdigest()
    if receipt.get("visible_source_text_sha256") != body_sha:
        raise ValueError("source body changed after its witnessed hash")
    if receipt.get("result") != "EXPLICIT_ORIGINAL_VERSION_VIEW":
        raise ValueError("version banner did not pass original source gate")

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    banner = re.compile(rf"Viewing\s+V{version}\s*\((\d{{4}}-\d{{2}}-\d{{2}})\)\Z")
    selections = [(i, banner.fullmatch(line)) for i, line in enumerate(lines)]
    selected = [(i, m) for i, m in selections if m is not None]
    if len(selected) != 1:
        raise ValueError("no unique exact version-local banner")
    cursor, found = selected[0]
    submitted_day = normalized_day(found.group(1))
    remaining = lines[cursor + 1:]
    # The official history index and top-of-page current study summary are
    # entirely before the selected version banner and are NEVER inspected.
    def unique(section: str) -> int:
        positions = [i for i, line in enumerate(remaining) if line == section]
        if len(positions) != 1:
            raise ValueError("historical details section missing or ambiguous: " + section)
        return positions[0]
    intro = unique("Study Details")
    identity = unique("Study Identification")
    study = unique("Study Status")
    end = unique("Sponsor/Collaborators")
    if not intro < identity < study < end:
        raise ValueError("selected historical Study Status section misordered")
    local_lines = remaining[study + 1:end]
    raw_status = field_value(local_lines, LABELS[0])
    if raw_status not in VALID_STATUS:
        raise ValueError("unrecognized original status; preserve unavailable")
    accepted_submitted = normalized_day(field_value(local_lines, LABELS[1]))
    posted_text = field_value(local_lines, LABELS[2])
    m = POSTED.fullmatch(posted_text)
    if m is None:
        raise ValueError("historical Last Update Posted lacked source-specified precision")
    posted_day, posted_precision = normalized_day(m.group(1)), m.group(2)
    if posted_day < accepted_submitted:
        raise ValueError("historical posting precedes accepted submission")
    observed = receipt.get("retrieved_utc")
    observed_time = datetime.fromisoformat(observed)
    if observed_time.tzinfo is None or observed_time.utcoffset() is None:
        raise ValueError("retrieval UTC time not timezone aware")
    if date.fromisoformat(posted_day) > observed_time.date():
        raise ValueError("reported posted date after actual observation")
    status_hash = sha256("\n".join(local_lines).encode("utf8")).hexdigest()
    return {
        "requested_version": version,
        "source_url": ui.version_url(version),
        "source_visible_text_sha256": body_sha,
        "version_local_status_section_sha256": status_hash,
        "retrieved_utc": observed,
        "version_banner_submitted_day": submitted_day,
        "status_value_in_selected_version": raw_status,
        "last_update_submitted_qc_day_in_selected_version": accepted_submitted,
        "last_update_posted_day_in_selected_version": posted_day,
        "last_update_posted_precision": posted_precision,
        "qc_date_equals_version_banner_date": accepted_submitted == submitted_day,
        "version_local_status_observed": True,
        "original_version_first_public_day_independently_proved": False,
        "clinical_verdict": "NOT_EVALUATED",
    }


def report_pair(rows: list[dict]) -> dict:
    if type(rows) is not list or len(rows) != 2:
        raise ValueError("two selected original versions required")
    if [x.get("requested_version") for x in rows] != list(ui.VERSIONS):
        raise ValueError("missing, duplicated or reordered source version")
    witnessed = all(x.get("version_local_status_observed") is True for x in rows)
    if any(x.get("original_version_first_public_day_independently_proved") is not False
           for x in rows):
        raise ValueError("source view does not prove original first publication")
    return {
        "schema": SCHEMA,
        "source": "official ClinicalTrials.gov public Record History",
        "target_study": ui.NCT,
        "versions": rows,
        "two_exact_version_status_fields_observed": witnessed,
        "different_status_values_observed": (
            rows[0]["status_value_in_selected_version"] != rows[1]["status_value_in_selected_version"]
            if witnessed else None
        ),
        "public_known_at_admitted_for_temporal_program": False,
        "historical_first_publication_attribution": "UNAVAILABLE",
        "original_w13_journals_modified": False,
        "niH_phase2_benchmark_witnessed_by_this_report": False,
    }


def run(*, output_dir: Path) -> dict:
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1100, "height": 900})
            for version in ui.VERSIONS:
                url = ui.version_url(version)
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    status = response.status if response else None
                    if status == 200:
                        page.wait_for_function(
                            "(v) => document.body?.innerText?.includes('Viewing V' + v)",
                            arg=version, timeout=20000,
                        )
                    body = page.locator("body").inner_text(timeout=12000)
                    receipt = ui.validate_observed_page(
                        requested_version=version, requested_url=url,
                        effective_url=page.url, body_text=body, title=page.title() or "",
                        status=status, retrieved_utc=datetime.now(timezone.utc).isoformat(),
                    )
                    row = extract_version_field(receipt=receipt, body_text=body)
                except (BrowserTimeout, ValueError, KeyError, TypeError) as exc:
                    row = {
                        "requested_version": version,
                        "source_url": url,
                        "version_local_status_observed": False,
                        "result": "UNAVAILABLE",
                        "reason_class": type(exc).__name__,
                        "original_version_first_public_day_independently_proved": False,
                    }
                results.append(row)
        finally:
            browser.close()
    final = report_pair(results)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "historical-version-status-fields.json").write_text(
        json.dumps(final, sort_keys=True, indent=2) + "\n", encoding="utf8",
    )
    return final


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args()
    report = run(output_dir=args.output_dir)
    print(json.dumps({
        "schema": report["schema"],
        "two_exact_version_status_fields_observed":
            report["two_exact_version_status_fields_observed"],
        "different_status_values_observed": report["different_status_values_observed"],
        "historical_first_publication_attribution":
            report["historical_first_publication_attribution"],
    }, sort_keys=True))
    if not report["two_exact_version_status_fields_observed"]:
        raise SystemExit("original version-specific status source fields unavailable")


if __name__ == "__main__":
    main()
