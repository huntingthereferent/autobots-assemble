"""Explicit public GitHub content observer for ALREADY accepted signed source claims.

The receiver fetches pinned public repository branch contents and checks exact
SHA-256 bytes. A GitHub HTTPS response is not a real-world owner credential,
not a signed statement by the user-enrolled Ed25519 key, and not proof that a
CP30 route/edge requirement holds. No general URL fetching or arbitrary hosts.
"""
from __future__ import annotations

import base64
import binascii
from datetime import datetime, timedelta, timezone
from hashlib import sha1, sha256
import json
import re
from pathlib import Path
from typing import Any
from urllib import error, request

from .external_evidence import SourceEvidenceLedger, SCOPES, _parse_time

_OBSERVER = "github-public-branch-contents-v1"
_GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
_ACCOUNT = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
_REPOSITORY = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}"
_BRANCH = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}"
_PATH = r"[A-Za-z0-9._/-]{1,256}"
_PIN = re.compile(rf"https://github\.com/({_ACCOUNT})/({_REPOSITORY})/blob/({_BRANCH})/({_PATH})\Z")
_MAX_BYTES = 1_048_576
_MAX_HTTP = 1_550_000
_MAX_RECEIPT_AGE = timedelta(minutes=10)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("GitHub observation refuses HTTP redirects")


def _github_json(resource: str) -> dict[str, Any]:
    """One bounded public GET to fixed api.github.com; no private credentials."""
    if not resource.startswith("/repos/") or "//" in resource:
        raise ValueError("invalid GitHub API resource")
    url = "https://api.github.com" + resource
    req = request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "process-workstation-observer/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }, method="GET")
    opener = request.build_opener(_NoRedirect())
    try:
        with opener.open(req, timeout=8) as response:
            if response.status != 200:
                raise ValueError("GitHub public read did not return HTTP 200")
            raw = response.read(_MAX_HTTP + 1)
    except (error.HTTPError, error.URLError, TimeoutError, OSError) as exc:
        raise ValueError("GitHub public source could not be observed") from exc
    if len(raw) > _MAX_HTTP:
        raise ValueError("GitHub public response exceeded size limit")
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("GitHub public response was not JSON") from exc
    if type(value) is not dict:
        raise ValueError("GitHub public response must be an object")
    return value


def _parse_locator(locator: str) -> tuple[str, str, str, str]:
    if type(locator) is not str:
        raise ValueError("expected an enrolled GitHub source locator")
    match = _PIN.fullmatch(locator)
    if match is None:
        raise ValueError("GitHub observer requires exact https://github.com/OWNER/REPO/blob/BRANCH/PATH")
    owner, repo, branch, path = match.groups()
    if (repo in (".", "..") or branch in (".", "..") or
            any(part in ("", ".", "..") for part in path.split("/")) or
            path.endswith("/") or path.startswith("/")):
        raise ValueError("invalid GitHub source path or branch")
    return owner, repo, branch, path


def _branch_sha(owner: str, repo: str, branch: str) -> str:
    response = _github_json(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
    obj = response.get("object")
    value = obj.get("sha") if type(obj) is dict else None
    if type(value) is not str or not _GIT_SHA.fullmatch(value):
        raise ValueError("GitHub branch head was not an exact commit SHA-1")
    return value


def _file_at_commit(owner: str, repo: str, path: str, commit: str) -> dict:
    row = _github_json(f"/repos/{owner}/{repo}/contents/{path}?ref={commit}")
    content = row.get("content")
    if (row.get("type") != "file" or row.get("path") != path or
            row.get("encoding") != "base64" or type(content) is not str or
            len(content) > 1_430_000 or type(row.get("size")) is not int):
        raise ValueError("GitHub response was not an inline regular file")
    try:
        raw = base64.b64decode(content.replace("\n", ""), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("GitHub source had invalid base64") from exc
    if len(raw) > _MAX_BYTES or len(raw) != row["size"]:
        raise ValueError("GitHub source size was not bounded or consistent")
    blob_sha = sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
    if row.get("sha") != blob_sha:
        raise ValueError("GitHub content did not match its Git blob identifier")
    return {"sha256": sha256(raw).hexdigest(), "size": len(raw), "git_blob_sha1": blob_sha}


def _eligible(store: SourceEvidenceLedger, challenge: str) -> tuple[dict, dict, str]:
    """Require accepted signed claims, still-active enrollment and no prior observation."""
    keys, challenges, accepted, history = store._state()
    if challenge not in challenges or challenge not in accepted:
        raise ValueError("GitHub observation needs an already accepted signed challenge")
    if any(e["kind"] == "SOURCE_OBSERVED" and e["record"].get("challenge") == challenge for e in history):
        raise ValueError("GitHub challenge already observed")
    issued = challenges[challenge]
    receipt = next(e["record"] for e in history if e["kind"] == "EVIDENCE_ACCEPTED"
                   and e["record"]["challenge"] == challenge)
    age = _now() - _parse_time(receipt["accepted_at"])
    if age < timedelta(seconds=-30) or age > _MAX_RECEIPT_AGE:
        raise ValueError("signed source receipt is too old for a fresh observation")
    issued_seq = next(e["seq"] for e in history if e["kind"] == "CHALLENGE_ISSUED" and e["record"]["challenge"] == challenge)
    if any(e["kind"] == "KEY_REVOKED" and e["record"].get("scope") in SCOPES and e["seq"] > issued_seq for e in history):
        raise ValueError("source keys changed since the signed challenge")
    sources = {}
    for scope in SCOPES:
        original = issued["pinned_keys"][scope]
        current = keys.get(scope)
        if (not current or current["key_sha256"] != original["key_sha256"] or
                current["source_id"] != original["source_id"]):
            raise ValueError("source enrollment no longer matches signed challenge")
        _parse_locator(current["locator"])
        sources[scope] = current["locator"]
    return issued, sources, history[-1]["event_hash"]


def observe_accepted_github_sources(*, data_dir: str | Path, challenge: str,
                                    confirm_challenge: str, allow_network: bool = False) -> dict:
    """Explicit network read, digest comparison and one append-only observation event.

    Does NOT submit a HandoffRuntime job or supply evidence of a CP30 route.
    The GitHub branch must be unchanged throughout this bounded read session.
    """
    if not allow_network or challenge != confirm_challenge:
        raise PermissionError("explicit --observe and exact challenge confirmation required")
    store = SourceEvidenceLedger(data_dir)
    issued, sources, previous = _eligible(store, challenge)
    identities = {s: _parse_locator(sources[s]) for s in SCOPES}
    # Scope labels alone do not establish that owners or repositories are distinct.
    branches = sorted(set((owner, repo, branch) for owner, repo, branch, _ in identities.values()))
    before = {b: _branch_sha(*b) for b in branches}
    reports = {}
    for scope in SCOPES:
        owner, repo, branch, path = identities[scope]
        file = _file_at_commit(owner, repo, path, before[(owner, repo, branch)])
        if file["sha256"] != issued["source_digests"][scope]:
            raise ValueError(f"observed GitHub bytes differ from signed {scope} digest")
        reports[scope] = {"source_id": issued["pinned_keys"][scope]["source_id"],
                          "locator": sources[scope], "commit_sha1": before[(owner, repo, branch)],
                          **file}
    for branch in branches:
        if _branch_sha(*branch) != before[branch]:
            raise ValueError("GitHub branch changed while sources were observed")
    # A single-writer ledger remains required. Refuse if a different local
    # record appeared during network IO; this is not multiprocess locking.
    issued_again, sources_again, current = _eligible(store, challenge)
    if current != previous or sources_again != sources or issued_again != issued:
        raise ValueError("enrollment or evidence history changed during observation")
    now = _now().isoformat()
    record = {"challenge": challenge, "observer": _OBSERVER,
              "observed_at": now, "observations": reports,
              "cp30_route_audited": False, "exact_task_authorized": False,
              "real_world_owners_authenticated": False}
    event = store._append("SOURCE_OBSERVED", record)
    return {"status": "PUBLIC_GITHUB_BYTES_MATCH_SIGNED_DIGESTS",
            "challenge": challenge, "observation_event": event["event_hash"],
            "scopes": reports, "external_content_observed": True,
            "cp30_route_audited": False, "exact_task_authorized": False,
            "real_world_owners_authenticated": False}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Explicit signed-claim-bound public GitHub source observation")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--confirm-challenge", required=True)
    parser.add_argument("--observe", action="store_true", help="Permit HTTPS reads of three enrolled public GitHub sources")
    args = parser.parse_args(argv)
    result = observe_accepted_github_sources(data_dir=args.data_dir, challenge=args.challenge,
                 confirm_challenge=args.confirm_challenge, allow_network=args.observe)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
