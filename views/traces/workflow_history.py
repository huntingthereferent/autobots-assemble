"""Source-owned, bounded GitHub Actions run index for the public research workbench.

Run *inside a GitHub Actions job* with read-only Actions API token access.
This is execution metadata, NOT a native verified research movement or worker journal.
No invented statuses. Refuse to call a partially retrieved archive complete.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "workstation-run-index/v1"
REPO = "huntingthereferent/autobots-assemble"
OUTPUT = Path("views/traces/workflow-runs-index.json")
PAGE_SIZE = 100
MAX_PAGES = 400
VALID_STATES = {"queued", "waiting", "pending", "requested", "in_progress", "completed"}


def normalize_run(raw):
    if not isinstance(raw, dict):
        return None
    run_id = raw.get("id")
    head = raw.get("head_sha")
    name = raw.get("name")
    status = raw.get("status")
    if (not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1
            or not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head)
            or not isinstance(name, str) or not name.strip() or status not in VALID_STATES):
        return None
    keep = ("id", "name", "head_sha", "status", "conclusion", "html_url",
            "created_at", "updated_at", "run_number", "head_branch", "event")
    return {k: raw.get(k) for k in keep}


def collect(fetch_page, *, max_pages=MAX_PAGES, collected_at=None):
    """Return first-party run identities. A page limit/invalid row is explicit."""
    if not 1 <= max_pages <= MAX_PAGES:
        raise ValueError("invalid bounded page budget")
    seen = {}
    page = 1
    reported_total = None
    fetched = 0
    malformed = 0
    exhausted = False
    while page <= max_pages:
        response = fetch_page(page)
        if not isinstance(response, dict) or not isinstance(response.get("workflow_runs"), list):
            raise RuntimeError("GitHub response missing workflow_runs array")
        total = response.get("total_count")
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise RuntimeError("GitHub response missing integer total_count")
        if reported_total is None:
            reported_total = total
        rows = response["workflow_runs"]
        if len(rows) > PAGE_SIZE:
            raise RuntimeError("GitHub returned more rows than bounded page size")
        for entry in rows:
            fetched += 1
            run = normalize_run(entry)
            if run is None:
                malformed += 1
            else:
                seen[run["id"]] = run
        if len(rows) < PAGE_SIZE:
            exhausted = True
            break
        page += 1
    runs = sorted(seen.values(), key=lambda r: (r["created_at"] or "", r["id"]), reverse=True)
    complete = bool(exhausted and fetched == reported_total and malformed == 0
                    and len(runs) == reported_total)
    if collected_at is None:
        collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "schema": SCHEMA,
        "source": "GitHub Actions repository workflow runs; source execution metadata only",
        "collected_at": collected_at,
        "reported_total": reported_total,
        "source_rows_seen": fetched,
        "indexed_count": len(runs),
        "invalid_source_rows": malformed,
        "pages_read": page,
        "complete": complete,
        "boundary": "A workflow run is not proof of a native verified research result; archived status is a source snapshot, not live telemetry.",
        "runs": runs,
    }


def fetch_from_github(token, repo=REPO):
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("invalid repository")
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing; cannot build full authenticated source index")

    def page(number):
        url = "https://api.github.com/repos/" + repo + "/actions/runs?" + urllib.parse.urlencode(
            {"per_page": PAGE_SIZE, "page": number})
        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "source-owned-workstation-index",
        })
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise RuntimeError("GitHub source fetch failed, HTTP " + str(exc.code)) from None
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise RuntimeError("GitHub source unavailable after bounded retries") from None
            time.sleep(2 ** attempt)
        raise RuntimeError("source fetch exhausted")
    return page


def main():
    token = os.environ.get("GH_TOKEN", "")
    fetch_page = fetch_from_github(token)
    # Concurrent GitHub runs can shift page offsets during the first walk.
    # Start afresh on an inconsistent snapshot; never patch gaps with guesses.
    for attempt in range(3):
        doc = collect(fetch_page)
        if doc["complete"]:
            break
        if attempt < 2:
            print("Source changed during collection or returned partial pages; retrying a fresh walk")
            time.sleep(3 * (attempt + 1))
    if not doc["runs"]:
        raise RuntimeError("GitHub returned no valid recorded workflow identities")
    if not doc["complete"]:
        raise RuntimeError("Refuse publication of incomplete source index: "
                           + str(doc["indexed_count"]) + "/" + str(doc["reported_total"])
                           + " after " + str(doc["pages_read"]) + " pages")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("Indexed", doc["indexed_count"], "original GitHub run IDs across",
          doc["pages_read"], "pages; no worker status fabricated.")


if __name__ == "__main__":
    main()
