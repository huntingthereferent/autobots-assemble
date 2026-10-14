"""Check continuity of two *external declarations*, never CP30 native owner pins.

Both snapshots must already have independent receiver challenges, Ed25519
receipts, and public GitHub observations. This adapter only relates evidence
across those two instants. It cannot manufacture CP30 in-process owner objects.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .external_evidence import SCOPES, SourceEvidenceLedger, _canonical
from .external_route_mapping import map_observed_sources, _strict_object
from .github_observation import _branch_sha, _github_json, _parse_locator


def _exact_observation(history: list[dict], challenge: str, event_hash: str) -> dict:
    matches = [e for e in history if e["kind"] == "SOURCE_OBSERVED" and
               e["record"].get("challenge") == challenge]
    if len(matches) != 1 or matches[0]["event_hash"] != event_hash:
        raise ValueError("exact previously recorded observation required")
    return matches[0]


def _side_identity(path: str | Path, expected_sha256: str) -> dict:
    """Return bounded semantic side fingerprints; never trust the data as owner proof."""
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 1_048_576:
        raise ValueError("unsafe or missing observed declaration")
    raw = source.read_bytes()
    if sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("observed declaration changed during comparison")
    value = json.loads(raw, object_pairs_hook=_strict_object)
    return {side: sha256(_canonical(value[side])).hexdigest() for side in ("old", "new")}


def _verify_ancestry(owner: str, repo: str, earlier: str, later: str) -> dict:
    """Consult GitHub's native comparison of two exact commit IDs.

    GitHub's answer is a repository-history statement, not third-party proof
    of legal ownership or continuity of the source's real-world referent.
    """
    if earlier == later:
        return {"status": "IDENTICAL", "earlier": earlier, "later": later}
    value = _github_json(f"/repos/{owner}/{repo}/compare/{earlier}...{later}")
    base, merge = value.get("base_commit"), value.get("merge_base_commit")
    commits = value.get("commits")
    if (value.get("status") != "ahead" or type(value.get("ahead_by")) is not int or
            value["ahead_by"] < 1 or type(value.get("behind_by")) is not int or
            value["behind_by"] != 0 or type(base) is not dict or
            base.get("sha") != earlier or type(merge) is not dict or
            merge.get("sha") != earlier or type(commits) is not list or
            not commits or type(commits[-1]) is not dict or
            commits[-1].get("sha") != later):
        raise ValueError("GitHub did not establish descendant commit history")
    return {"status": "DESCENDANT", "earlier": earlier, "later": later}


def compare_external_observations(*, data_dir: str | Path,
        earlier_challenge: str, earlier_event: str,
        later_challenge: str, later_event: str,
        earlier_files: dict[str, str | Path], later_files: dict[str, str | Path],
        allow_network: bool = False, confirm_later_challenge: str = "") -> dict[str, Any]:
    """Optional online ancestry check over two validated external snapshots.

    There is NO owner enrollment, issuance of local native owner pins, source
    execution, job admission, or journal write in either mode.
    """
    if earlier_challenge == later_challenge:
        raise ValueError("continuity requires two independently issued challenges")
    if type(earlier_files) is not dict or set(earlier_files) != set(SCOPES) or \
       type(later_files) is not dict or set(later_files) != set(SCOPES):
        raise ValueError("exact two complete donor/middle/final observations required")
    if allow_network and confirm_later_challenge != later_challenge:
        raise PermissionError("explicit current challenge confirmation required for GitHub reads")
    store = SourceEvidenceLedger(data_dir)
    history = store.history()
    earlier = _exact_observation(history, earlier_challenge, earlier_event)
    later = _exact_observation(history, later_challenge, later_event)
    if earlier["seq"] >= later["seq"]:
        raise ValueError("external observation order is not forward-moving")
    before_tip = history[-1]["event_hash"]
    prior = map_observed_sources(data_dir=data_dir, challenge=earlier_challenge,
                                 observation_event=earlier_event, source_files=earlier_files)
    current = map_observed_sources(data_dir=data_dir, challenge=later_challenge,
                                   observation_event=later_event, source_files=later_files)
    if (prior["route"], prior["declared_route_fingerprint"], prior["declared_witness_sha256"]) != \
       (current["route"], current["declared_route_fingerprint"], current["declared_witness_sha256"]):
        raise ValueError("route or witness referent changed; start a new continuity comparison")
    issued = {e["record"]["challenge"]: e["record"] for e in history
              if e["kind"] == "CHALLENGE_ISSUED" and
                 e["record"].get("challenge") in (earlier_challenge, later_challenge)}
    old_pin, new_pin = issued[earlier_challenge]["pinned_keys"], issued[later_challenge]["pinned_keys"]
    lineage = {}
    ancestry_targets = {}
    for scope in SCOPES:
        a, b = prior["scopes"][scope], current["scopes"][scope]
        a_ob, b_ob = earlier["record"]["observations"][scope], later["record"]["observations"][scope]
        # Both challenges must bind precisely the same enrolled key + locator.
        if (old_pin[scope].get("key_sha256") != new_pin[scope].get("key_sha256") or
                old_pin[scope].get("source_id") != new_pin[scope].get("source_id") or
                a_ob.get("locator") != b_ob.get("locator")):
            raise ValueError("source enrollment or locator changed between observations")
        locator = _parse_locator(a_ob["locator"])
        old_commit, new_commit = a_ob["commit_sha1"], b_ob["commit_sha1"]
        # Prevent one commit ID being advertised for changed bytes of the same file.
        if old_commit == new_commit and a["source_sha256"] != b["source_sha256"]:
            raise ValueError("same Git commit cannot carry two different bytes for one path")
        for side in ("old", "new"):
            av, bv = a[side], b[side]
            if av["source_label"] != bv["source_label"]:
                raise ValueError("source label changed; identity not carried")
            if bv["revision"] < av["revision"]:
                raise ValueError("claimed source revision regressed")
        fingerprints_a = _side_identity(earlier_files[scope], a["source_sha256"])
        fingerprints_b = _side_identity(later_files[scope], b["source_sha256"])
        for side in ("old", "new"):
            if (a[side]["revision"] == b[side]["revision"] and
                    fingerprints_a[side] != fingerprints_b[side]):
                raise ValueError("claimed source content changed without a revision change")
        branch_key = locator[:3]
        if branch_key in ancestry_targets and ancestry_targets[branch_key] != (old_commit, new_commit):
            raise ValueError("one GitHub branch gave conflicting observed commit identities")
        ancestry_targets[branch_key] = (old_commit, new_commit)
        lineage[scope] = {"source_id": old_pin[scope]["source_id"],
                           "public_key_sha256": old_pin[scope]["key_sha256"],
                           "earlier_commit": old_commit, "later_commit": new_commit,
                           "old_side_revisions": [a["old"]["revision"], b["old"]["revision"]],
                           "new_side_revisions": [a["new"]["revision"], b["new"]["revision"]],
                           "declaration_content_changed": fingerprints_a != fingerprints_b,
                           "signed_file_bytes_changed": a["source_sha256"] != b["source_sha256"]}
    if allow_network:
        for branch, (old_commit, new_commit) in sorted(ancestry_targets.items()):
            owner, repo, branch_name = branch
            # Verify CURRENT branch head before *and* after commit ancestry checks.
            if _branch_sha(owner, repo, branch_name) != new_commit:
                raise ValueError("GitHub branch head moved since second observation")
            _verify_ancestry(owner, repo, old_commit, new_commit)
        for branch, (_, new_commit) in sorted(ancestry_targets.items()):
            if _branch_sha(*branch) != new_commit:
                raise ValueError("GitHub branch moved during ancestry verification")
        # A separate process could still race this read; no lock is claimed.
        for scope in SCOPES:
            for path, summary in ((earlier_files[scope], prior), (later_files[scope], current)):
                _side_identity(path, summary["scopes"][scope]["source_sha256"])
    if store.history()[-1]["event_hash"] != before_tip:
        raise ValueError("source evidence journal changed during comparison")
    return {"status": ("EXTERNAL_GITHUB_LINEAGE_REPORTED_NATIVE_OWNER_UNPROVED" if allow_network
                       else "EXTERNAL_SIGNED_OBSERVATION_PAIR_NATIVE_OWNER_UNPROVED"),
            "earlier_challenge": earlier_challenge, "later_challenge": later_challenge,
            "earlier_observation_event": earlier_event, "later_observation_event": later_event,
            "route": current["route"], "scopes": lineage,
            "online_ancestry_checked": allow_network,
            "github_reported_descendant_commits": allow_network,
            "online_observation_completed": False,
            "live_local_owner_verified": False, "native_owner_pins_verified": False,
            "native_route_reaudited": False, "exact_task_authorized": False,
            "native_handoff_admitted": False, "journal_modified": False,
            "notes": ["Two receiver-issued challenges, verified signed receipts, and observed bytes are compared.",
                      "GitHub ancestry is a public-repository history report, not external owner identity.",
                      "No CP30 in-process owner snapshots or pins are created; route tasks remain unproved."]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only external source snapshot continuity check")
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--earlier-challenge", required=True)
    ap.add_argument("--earlier-event", required=True)
    ap.add_argument("--later-challenge", required=True)
    ap.add_argument("--later-event", required=True)
    for position in ("earlier", "later"):
        for scope in SCOPES:
            ap.add_argument(f"--{position}-{scope}-file", type=Path, required=True)
    ap.add_argument("--verify-github-ancestry", action="store_true")
    ap.add_argument("--confirm-later-challenge", default="")
    opts = ap.parse_args(argv)
    result = compare_external_observations(data_dir=opts.data_dir,
        earlier_challenge=opts.earlier_challenge, earlier_event=opts.earlier_event,
        later_challenge=opts.later_challenge, later_event=opts.later_event,
        earlier_files={s: getattr(opts, f"earlier_{s}_file") for s in SCOPES},
        later_files={s: getattr(opts, f"later_{s}_file") for s in SCOPES},
        allow_network=opts.verify_github_ancestry,
        confirm_later_challenge=opts.confirm_later_challenge)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
