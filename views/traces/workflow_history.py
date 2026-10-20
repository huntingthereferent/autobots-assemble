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
    first = fetch_page(1)
    if not isinstance(first, dict) or not isinstance(first.get("workflow_runs"), list):
        raise RuntimeError("GitHub response missing workflow_runs array")
    reported_total = first.get("total_count")
    if not isinstance(reported_total, int) or isinstance(reported_total, bool) or reported_total < 0:
        raise RuntimeError("GitHub response missing integer total_count")
    expected_pages = max(1, (reported_total + PAGE_SIZE - 1) // PAGE_SIZE)
    planned_pages = min(max_pages, expected_pages)
    # Bound parallelism: 8 authenticated source requests instead of a browser's
    # 70+ anonymous reads or a long serial walk. Results are processed in page order.
    from concurrent.futures import ThreadPoolExecutor
    if planned_pages > 1:
        with ThreadPoolExecutor(max_workers=min(8, planned_pages - 1)) as pool:
            other = list(pool.map(fetch_page, range(2, planned_pages + 1)))
    else:
        other = []
    seen = {}
    fetched = 0
    malformed = 0
    inconsistent_totals = False
    processed_pages = 0
    for page, response in enumerate([first, *other], 1):
        if not isinstance(response, dict) or not isinstance(response.get("workflow_runs"), list):
            raise RuntimeError("GitHub response missing workflow_runs array")
        total = response.get("total_count")
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise RuntimeError("GitHub response missing integer total_count")
        if total != reported_total:
            inconsistent_totals = True
        rows = response["workflow_runs"]
        if len(rows) > PAGE_SIZE:
            raise RuntimeError("GitHub returned more rows than bounded page size")
        processed_pages = page
        for entry in rows:
            fetched += 1
            run = normalize_run(entry)
            if run is None:
                malformed += 1
            else:
                seen[run["id"]] = run
    runs = sorted(seen.values(), key=lambda r: (r["created_at"] or "", r["id"]), reverse=True)
    complete = bool(planned_pages == expected_pages and not inconsistent_totals
                    and fetched == reported_total and malformed == 0
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
        "pages_read": processed_pages,
        "complete": complete,
        "boundary": "A workflow run is not proof of a native verified research result; archived status is a source snapshot, not live telemetry.",
        "runs": runs,
    }



def collect_frozen_history(fetch_page, *, cutoff=None, start=None,
                           partition_max=900, max_windows=128):
    """Index all available source IDs through one fixed UTC cutoff.

    GitHub caps created-filter searches at 1,000 results. Split at UTC
    second boundaries until each search has <=900 source records, then
    collect every page. Newer runs cannot shift the frozen windows.
    The newest 100 are checked separately in the browser.
    """
    if cutoff is None:
        cutoff = int(time.time()) - 60
    if start is None:
        start = int(datetime(2018, 1, 1, tzinfo=timezone.utc).timestamp())
    if not isinstance(cutoff, int) or not isinstance(start, int) or start > cutoff:
        raise ValueError("invalid immutable UTC observation interval")
    if not (1 <= partition_max <= 900 and 1 <= max_windows <= 512):
        raise ValueError("invalid source-partition budget")

    def stamp(second):
        return datetime.fromtimestamp(second, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pending = [(start, cutoff)]
    windows = []
    requests = 0
    while pending:
        if len(pending) + len(windows) > max_windows:
            raise RuntimeError("Exhausted bounded source partition budget")
        lower, upper = pending.pop()
        window = stamp(lower) + ".." + stamp(upper)
        first = fetch_page(1, window)
        requests += 1
        if not isinstance(first, dict) or not isinstance(first.get("workflow_runs"), list):
            raise RuntimeError("GitHub date-scoped response missing workflow_runs")
        total = first.get("total_count")
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise RuntimeError("GitHub date-scoped response missing integer count")
        if total > partition_max:
            midpoint = lower + (upper - lower) // 2
            if midpoint >= upper:
                raise RuntimeError("More than search cap events share a UTC second")
            pending.append((midpoint + 1, upper))
            pending.append((lower, midpoint))
        else:
            windows.append((window, total, first))
    seen = {}
    raw_rows = 0
    malformed = 0
    pages_read = requests
    inconsistent = False
    from concurrent.futures import ThreadPoolExecutor
    for window, total, first in windows:
        page_count = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        if page_count > 10:
            raise RuntimeError("GitHub capped date range was not narrowed")
        if page_count > 1:
            with ThreadPoolExecutor(max_workers=min(8, page_count - 1)) as pool:
                other = list(pool.map(lambda p: fetch_page(p, window), range(2, page_count + 1)))
        else:
            other = []
        pages_read += len(other)
        for response in [first, *other]:
            if not isinstance(response, dict) or not isinstance(response.get("workflow_runs"), list):
                raise RuntimeError("GitHub page missing workflow_runs")
            if response.get("total_count") != total:
                inconsistent = True
            for entry in response["workflow_runs"]:
                raw_rows += 1
                run = normalize_run(entry)
                if run is None:
                    malformed += 1
                else:
                    seen[run["id"]] = run
    declared = sum(item[1] for item in windows)
    rows = sorted(seen.values(), key=lambda r: (r["created_at"] or "", r["id"]), reverse=True)
    complete = (not inconsistent and malformed == 0 and raw_rows == declared
                and len(rows) == declared)
    return {
        "schema": SCHEMA,
        "source": "GitHub Actions repository workflow runs; source execution metadata only",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cutoff_at": stamp(cutoff),
        "reported_total": declared,
        "source_rows_seen": raw_rows,
        "indexed_count": len(rows),
        "invalid_source_rows": malformed,
        "pages_read": pages_read,
        "windows_read": len(windows),
        "complete": complete,
        "boundary": "Complete for accessible GitHub run identities through cutoff_at, not a live worker feed. Newer run statuses come from separate GitHub polling.",
        "runs": rows,
    }


def fetch_from_github(token, repo=REPO):
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("invalid repository")
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing; cannot build full authenticated source index")

    def page(number, created=None):
        params = {"per_page": PAGE_SIZE, "page": number}
        if created is not None:
            params["created"] = created
        url = "https://api.github.com/repos/" + repo + "/actions/runs?" + urllib.parse.urlencode(params)
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
    # An immutable creation-time cutoff avoids races with newly queued work.
    # Partition each GitHub search below its documented 1,000-result cap.
    for attempt in range(2):
        doc = collect_frozen_history(fetch_page)
        if doc["complete"]:
            break
        if attempt == 0:
            print("Frozen source windows shifted or returned partial pages; retrying", flush=True)
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
