"""Read-only operator preflight for an actually enrolled public CP30 source.

An enrolled source is a LOCAL policy decision, not real-world identity proof.
This module never enrolls identities, writes evidence, or admits a native job.
An optional, explicit network probe matches already signed challenge digests
against the currently published bytes and separately pinned numeric repo IDs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from .external_evidence import SCOPES, SourceEvidenceLedger, _parse_time
from .external_authority_binding import AuthorityAnchorLedger
from .independent_authority_source import IndependentWitnessLedger, _checked_public_repo, _head
from .source_origin_authority import SourceOriginPolicy
from .github_observation import _eligible, _parse_locator, _file_at_commit


def _clock_utc() -> datetime:
    return datetime.now(timezone.utc)


def _require_unexpired_challenge(issued: dict) -> None:
    start = _parse_time(issued['issued_at'])
    ttl = issued.get('ttl_seconds')
    if type(ttl) is not int or not 30 <= ttl <= 600:
        raise ValueError('invalid original receiver challenge lifetime')
    now = _clock_utc()
    if now < start or now > start + timedelta(seconds=ttl):
        raise ValueError('original receiver challenge expired before live probe')


def readiness(data_dir: str | Path) -> dict[str, Any]:
    """Inspect policy journals without network, writes, or claimed authority.

    Invalid journals raise rather than being ignored. No key material is
    returned; only scope availability and coarse prerequisites are disclosed.
    """
    path = Path(data_dir)
    keys, challenges, accepted, events = SourceEvidenceLedger(path)._state()
    pins = SourceOriginPolicy(path).current()
    anchors = AuthorityAnchorLedger(path).current()
    witnesses = IndependentWitnessLedger(path).current()
    scopes = {}
    for scope in SCOPES:
        key = keys.get(scope)
        pin = pins.get(scope)
        matched = bool(key and pin and key.get('key_sha256') == pin.get('key_sha256')
                       and key.get('source_id') == pin.get('source_id')
                       and key.get('locator') == pin.get('locator'))
        scopes[scope] = {'source_key_enrolled': key is not None,
                         'repository_identity_pinned': pin is not None,
                         'enrollment_matches_repo_policy': matched}
    missing = []
    for scope in SCOPES:
        if not scopes[scope]['enrollment_matches_repo_policy']:
            missing.append('ACTIVE_SOURCE_AND_REPOSITORY_PIN:' + scope)
    if not anchors:
        missing.append('INDEPENDENTLY_REVIEWED_AUTHORITY_ANCHOR')
    if not witnesses:
        missing.append('SEPARATELY_ENROLLED_PUBLIC_WITNESS')
    # Issued/accepted records alone cannot demonstrate an unexpired usable
    # challenge. The actual network operation invokes _eligible, which checks it.
    if not accepted or not any(e['kind'] == 'EVIDENCE_ACCEPTED' for e in events):
        missing.append('ACCEPTED_THREE_SCOPE_SIGNED_CHALLENGE')
    if not challenges:
        missing.append('RECEIVER_ISSUED_CHALLENGE')
    return {'status': 'PREREQUISITES_PRESENT_NOT_AUTHENTICATED' if not missing else 'BLOCKED',
            'scope_status': scopes, 'missing': missing,
            'network_requested': False, 'network_observed': False,
            'owner_identity_authenticated': False,
            'cp30_route_audited': False, 'task_authorized': False,
            'journal_written': False,
            'note': 'Policy presence is not independent identity or authority verification; probe checks freshness.'}


def probe_enrolled_public_sources(*, data_dir: str | Path, challenge: str,
                                  confirm_challenge: str,
                                  allow_network: bool = False) -> dict[str, Any]:
    """Explicit live read of existing configured sources; ZERO journal writes."""
    if (allow_network is not True or not isinstance(challenge, str)
            or confirm_challenge != challenge):
        raise PermissionError('explicit --network and matching challenge confirmation required')
    path = Path(data_dir)
    store = SourceEvidenceLedger(path)
    # Signed receipt freshness, active enrollment, non-replay and hash chain.
    issued, locators, previous = _eligible(store, challenge)
    _require_unexpired_challenge(issued)
    pinned_policy = SourceOriginPolicy(path)
    previous_origin = pinned_policy.history()
    policy = pinned_policy.current()
    if set(policy) != set(SCOPES):
        raise PermissionError('three source repository identities must be pinned before network reads')
    locations = {}
    identities = {}
    for scope in SCOPES:
        owner, repo, branch, filename = _parse_locator(locators[scope])
        pin = policy[scope]
        signed = issued['pinned_keys'][scope]
        if (pin['locator'] != locators[scope] or pin['source_id'] != signed['source_id']
                or pin['key_sha256'] != signed['key_sha256']):
            raise PermissionError('repository identity and signed enrollment do not match')
        locations[scope] = (owner, repo, branch, filename)
        identities[(owner, repo)] = {'repo_id': pin['repo_id'],
                                    'owner_account_id': pin['owner_account_id']}
    # Both trust policy layers must exist. These checks do not prove legitimacy.
    if not AuthorityAnchorLedger(path).current() or not IndependentWitnessLedger(path).current():
        raise PermissionError('configured authority anchor and witness enrollment required')
    initial_authority = AuthorityAnchorLedger(path).history()
    initial_witness = IndependentWitnessLedger(path).history()
    for (owner, repo), expected in identities.items():
        actual = _checked_public_repo(owner, repo)
        if actual != expected:
            raise ValueError('public GitHub repository immutable identity disagrees with pinned identity')
    branches = sorted(set((owner, repo, branch) for owner, repo, branch, filename in locations.values()))
    before = {(owner, repo, branch): _head(owner, repo, branch) for owner, repo, branch in branches}
    observed = {}
    for scope in SCOPES:
        owner, repo, branch, filename = locations[scope]
        commit = before[(owner, repo, branch)]
        file = _file_at_commit(owner, repo, filename, commit)
        if file['sha256'] != issued['source_digests'][scope]:
            raise ValueError('live public source differs from signed ' + scope + ' digest')
        observed[scope] = {'repository_id': policy[scope]['repo_id'],
                           'owner_account_id': policy[scope]['owner_account_id'],
                           'commit': commit, 'path': filename,
                           'source_sha256': file['sha256'],
                           'git_blob_sha1': file['git_blob_sha1'],
                           'bytes': file['size']}
    for owner, repo, branch in branches:
        if _head(owner, repo, branch) != before[(owner, repo, branch)]:
            raise ValueError('GitHub branch moved during public content read')
    issued2, locators2, last2 = _eligible(store, challenge)
    _require_unexpired_challenge(issued2)
    if (previous != last2 or locators != locators2 or issued != issued2
            or pinned_policy.history() != previous_origin
            or AuthorityAnchorLedger(path).history() != initial_authority
            or IndependentWitnessLedger(path).history() != initial_witness):
        raise ValueError('evidence or trust policy changed during network read')
    return {'status': 'LIVE_PUBLIC_BYTES_MATCH_PRIOR_SIGNED_CLAIMS',
            'challenge': challenge,
            'observed_at': datetime.now(timezone.utc).isoformat(),
            'scopes': observed, 'network_observed': True,
            'recorded': False, 'journal_written': False,
            'owner_identity_authenticated': False, 'source_owner_authority_established': False,
            'cp30_route_audited': False, 'task_authorized': False,
            'note': 'This is a public-source preflight, not CP30 admission or authority attestation.'}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Read-only CP30 external-source operator preflight')
    parser.add_argument('--data-dir', type=Path, required=True)
    cmds = parser.add_subparsers(dest='action', required=True)
    cmds.add_parser('readiness', help='Read local policy state; no network')
    p = cmds.add_parser('probe', help='Explicit public GitHub GETs; no journal writes')
    p.add_argument('--challenge', required=True)
    p.add_argument('--confirm-challenge', required=True)
    p.add_argument('--network', action='store_true')
    args = parser.parse_args(argv)
    result = (readiness(args.data_dir) if args.action == 'readiness'
              else probe_enrolled_public_sources(data_dir=args.data_dir,
                    challenge=args.challenge, confirm_challenge=args.confirm_challenge,
                    allow_network=args.network))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
