"""Account-level GitHub Actions capacity observer and explicitly gated twin birth.

This module does not itself run in the background. A trusted scheduler may collect
snapshots and invoke birth after configured sustained saturation. Existing twins
remain independent research records; no workflow result is silently transferred.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib import parse, request

ACCOUNT = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})\Z")
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
MAX_CONCURRENT_FREE = 20


def checked_repo(name: str) -> tuple[str, str]:
    parts = name.split("/")
    if len(parts) != 2 or not ACCOUNT.fullmatch(parts[0]) or not REPO.fullmatch(parts[1]):
        raise ValueError("Expected owner/repository")
    return parts[0], parts[1]


def _github_get(path: str, token: str):
    if not token or not path.startswith("/") or "//" in path:
        raise ValueError("Invalid API request or missing read credential")
    url = "https://api.github.com" + path
    req = request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "digital-twin-factory/1",
    })
    with request.urlopen(req, timeout=15) as res:
        payload = json.load(res)
    return payload


def observe_account(owner: str, token: str, *, cap: int = MAX_CONCURRENT_FREE) -> dict:
    """Enumerate account-owned repositories; count all in-progress and queued runs.

    The latest-100 workflow viewer is NOT a reliable account capacity source.
    A short/incomplete response or missing permissions fails closed.
    """
    if not ACCOUNT.fullmatch(owner) or not (1 <= cap <= 1000):
        raise ValueError("Invalid account or concurrency limit")
    identity = _github_get("/user", token)
    if identity.get("login", "").lower() != owner.lower():
        raise PermissionError("Read token does not belong to the requested owner")
    repos: list[str] = []
    page = 1
    while True:
        rows = _github_get("/user/repos?affiliation=owner&per_page=100&page=" + str(page), token)
        if not isinstance(rows, list):
            raise ValueError("Repository enumeration did not return a list")
        for repo in rows:
            if repo.get("owner", {}).get("login", "").lower() == owner.lower():
                repos.append(repo["full_name"])
        if len(rows) < 100:
            break
        page += 1
        if page > 100:
            raise ValueError("Repository enumeration exceeded safety bound")
    if not repos:
        raise ValueError("No accessible owner repositories; cannot assess capacity")
    running = queued = 0
    details = []
    for name in sorted(set(repos)):
        encoded = "/".join(parse.quote(p, safe="") for p in checked_repo(name))
        counts = {}
        for status in ("in_progress", "queued"):
            response = _github_get(f"/repos/{encoded}/actions/runs?status={status}&per_page=1", token)
            value = response.get("total_count")
            if type(value) is not int or value < 0:
                raise ValueError(f"Missing full {status} count for {name}")
            counts[status] = value
        running += counts["in_progress"]
        queued += counts["queued"]
        details.append({"repository": name, "running": counts["in_progress"], "queued": counts["queued"]})
    return {
        "schema": "digital-twin-capacity/v1", "owner": owner,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "running": running, "queued": queued, "concurrency_ceiling": cap,
        "fully_enumerated": True, "repositories": details,
        "measurement": "GitHub REST account-owned repository Actions status totals",
    }


def birth_decision(samples: list[dict], *, minimum_samples: int = 3,
                   min_elapsed_seconds: int = 120) -> dict:
    """Fail closed unless independent, sufficiently spaced samples show saturation."""
    if len(samples) < minimum_samples or minimum_samples < 2:
        return {"spawn": False, "reason": "insufficient_samples"}
    recent = samples[-minimum_samples:]
    if any(s.get("schema") != "digital-twin-capacity/v1"
           or s.get("fully_enumerated") is not True for s in recent):
        return {"spawn": False, "reason": "incomplete_observation"}
    owners = {s.get("owner") for s in recent}
    ceilings = {s.get("concurrency_ceiling") for s in recent}
    if len(owners) != 1 or len(ceilings) != 1:
        return {"spawn": False, "reason": "incomparable_sources"}
    try:
        times = [datetime.fromisoformat(s["observed_at"]) for s in recent]
        if any(t.tzinfo is None for t in times):
            raise ValueError("Naive timestamp")
        spacing = [(b-a).total_seconds() for a,b in zip(times, times[1:])]
        valid = all(x > 0 for x in spacing) and (times[-1] - times[0]).total_seconds() >= min_elapsed_seconds
        saturation = all(type(s.get("running")) is int and type(s.get("queued")) is int
                         and type(s.get("concurrency_ceiling")) is int
                         and s["running"] >= s["concurrency_ceiling"]
                         and s["queued"] > 0 for s in recent)
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"spawn": False, "reason": "invalid_measurement"}
    if not valid:
        return {"spawn": False, "reason": "unsustained_observation"}
    if not saturation:
        return {"spawn": False, "reason": "capacity_not_saturated"}
    return {"spawn": True, "reason": "sustained_capacity_with_backlog",
            "owner": recent[-1]["owner"], "running": recent[-1]["running"],
            "queued": recent[-1]["queued"], "source_samples": minimum_samples}


def _run(*argv: str) -> str:
    result = subprocess.run(argv, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def birth_twin(*, source: str, target: str, source_sha: str, confirm: str,
               visibility: str = "private") -> dict:
    """Provision an EMPTY destination and copy all branch/tag history; keep Actions disabled.

    Requires locally installed git + gh authenticated AS THE TARGET OWNER.
    Never overwrites existing repositories or copies another account's secrets.
    """
    source_owner, source_repo = checked_repo(source)
    target_owner, target_repo = checked_repo(target)
    if source == target or not SHA.fullmatch(source_sha) or confirm != target:
        raise PermissionError("Source SHA and exact target confirmation are required")
    if visibility not in ("private", "public"):
        raise ValueError("Invalid visibility")
    authenticated_as = _run("gh", "api", "user", "--jq", ".login")
    if authenticated_as.lower() != target_owner.lower():
        raise PermissionError("gh must be authenticated as the destination owner")
    exists = subprocess.run(["gh", "repo", "view", target, "--json", "nameWithOwner"],
                            capture_output=True, text=True)
    if exists.returncode == 0:
        raise FileExistsError("Destination must be a NEW, empty repository")
    with tempfile.TemporaryDirectory(prefix="digital-twin-") as temporary:
        clone = str(Path(temporary) / "source.git")
        _run("git", "clone", "--bare",
             f"https://github.com/{source_owner}/{source_repo}.git", clone)
        head = _run("git", "-C", clone, "rev-parse", "refs/heads/main")
        if head != source_sha:
            raise ValueError("Source moved or differs from the pinned SHA; no birth")
        _run("gh", "repo", "create", target, "--" + visibility,
             "--description", f"Source-pinned digital twin of {source}")
        # Disable all workflow executions BEFORE pushing hundreds of workflow files.
        _run("gh", "api", "-X", "PUT", f"repos/{target}/actions/permissions",
             "-F", "enabled=false")
        _run("git", "-c", "credential.helper=",
             "-c", "credential.helper=!gh auth git-credential",
             "-C", clone, "push", "--mirror", f"https://github.com/{target}.git")
        mirrored_head = _run("git", "-c", "credential.helper=",
                             "-c", "credential.helper=!gh auth git-credential",
                             "ls-remote", f"https://github.com/{target}.git", "refs/heads/main")
        if not mirrored_head.startswith(source_sha + "\t"):
            raise RuntimeError("Destination main SHA verification FAILED")
    return {
        "schema": "digital-twin-birth/v1", "source": source, "target": target,
        "pinned_main_sha": source_sha, "verified_main_sha": source_sha,
        "branch_and_tag_history_cloned": True, "actions_enabled": False,
        "independent_workloads_started": False,
        "next": "Audit workflow triggers and configure an explicit lane allowlist before enabling Actions",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capacity-driven GitHub workstation twin factory")
    sub = parser.add_subparsers(dest="cmd", required=True)
    obs = sub.add_parser("observe", help="Read all owned repo Action counts")
    obs.add_argument("--owner", required=True)
    obs.add_argument("--cap", type=int, default=MAX_CONCURRENT_FREE)
    dec = sub.add_parser("decide", help="Evaluate newline-separated JSON snapshots")
    dec.add_argument("--snapshots", type=Path, required=True)
    birth = sub.add_parser("birth", help="Exact confirmation required; no overwrite")
    birth.add_argument("--source", default="huntingthereferent/autobots-assemble")
    birth.add_argument("--target", required=True)
    birth.add_argument("--source-sha", required=True)
    birth.add_argument("--confirm", required=True)
    birth.add_argument("--visibility", choices=("private", "public"), default="private")
    args = parser.parse_args()
    if args.cmd == "observe":
        result = observe_account(args.owner, os.environ.get("FACTORY_SOURCE_TOKEN", ""), cap=args.cap)
    elif args.cmd == "decide":
        samples = [json.loads(line) for line in args.snapshots.read_text().splitlines() if line.strip()]
        result = birth_decision(samples)
    else:
        result = birth_twin(source=args.source, target=args.target,
                            source_sha=args.source_sha, confirm=args.confirm,
                            visibility=args.visibility)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
