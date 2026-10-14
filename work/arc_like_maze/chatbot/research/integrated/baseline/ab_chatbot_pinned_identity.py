"""Version identity for *one finite mathematical model* of A/B relations.

A/B is language for continuing a referent; this module is a finite mathematical
observation scaffold, not a definition of A/B, a chatbot, or a network security
protocol. A source-owned, in-process version is immutable; a mutable outside
oracle is NOT admitted by a declared string, revision, hash, or trust flag.

Preserves distinctions:
  immutable historical version != current live version;
  equal tables at two epochs != unchanged history between epochs;
  coherent copied snapshot != proof that an external live system was stable.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import (
    DOMAIN, DOMAIN_SET, Discovery, State, verify_recorded_full,
)
from ab_chatbot_stability_witness import TransportedLaw, recheck_full_record

# Ordering is part of the finite observation contract, not a state-label guess.
KEYS = tuple((s, a) for s in DOMAIN for a in 'AB')


def _state(s: object) -> bool:
    return type(s) is tuple and len(s) == 3 and all(type(x) is int and x in (0, 1, 2) for x in s)


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, separators=(',', ':'), sort_keys=True).encode('utf-8')


def table_digest(values: tuple[State, ...]) -> str:
    """Content fingerprint of a complete *labeled* two-generator table."""
    if type(values) is not tuple or len(values) != len(KEYS) or not all(_state(s) for s in values):
        raise ValueError('complete F3^3 two-generator table is required')
    return sha256(_canonical([list(s) for s in values])).hexdigest()


def witness_digest(prior: Discovery) -> str:
    """Local integrity fingerprint, not cryptographic proof of external origin."""
    return sha256(_canonical({
        'status': prior.status,
        'rooted_pairs': prior.rooted_pairs,
        'full_pairs': prior.full_pairs,
        'observed': [(o.state, o.action, o.output) for o in prior.observed],
        'source': 'finite-F3-candidate',
    })).hexdigest()


@dataclass(frozen=True)
class PinnedView:
    """Immutable complete relation sampled from an owned *constructed* law.

    A PinnedView is usable for historical mathematics after a live update.
    Only the issuing OwnedVersions object can bind it as source-owned evidence.
    """
    version: int
    values: tuple[State, ...]
    digest: str

    def step(self, state: State, action: str) -> State:
        if state not in DOMAIN_SET or action not in ('A', 'B'):
            raise ValueError('outside finite state/action domain')
        return self.values[KEYS.index((state, action))]


@dataclass(frozen=True)
class BoundCorrespondence:
    """A mathematical witness bound to an owner-held, immutable version."""
    view: PinnedView
    source_phi: tuple[int, int, int]
    proof_digest: str


@dataclass(frozen=True)
class IdentityResult:
    status: str  # SAME_PINNED_VERSION / SAME_ENDPOINT_LAW_NEW_VERSION /
                 # CHANGED / UNKNOWN_UNBOUND / WALL_INVALID
    scope: str
    mismatch: tuple[State, str, State, State] | None = None
    inspected_edges: int = 0  # local *copied table* comparisons; not new oracle calls


class OwnedVersions:
    """An in-process model owner enforcing version immutability.

    It accepts ONLY frozen TransportedLaw construction objects, not arbitrary
    callbacks. The construction code computes all 54 transitions once per
    version and stores an immutable table. This is not an attestation of a real
    device, service, outside process, or mutation-resistant persistent store.
    """
    def __init__(self, law: TransportedLaw):
        if type(law) is not TransportedLaw:
            raise ValueError('only locally owned constructed laws are admitted')
        self._issued: list[PinnedView] = []
        self.replace(law)

    def replace(self, law: TransportedLaw) -> PinnedView:
        if type(law) is not TransportedLaw:
            raise ValueError('external oracle is not an owned constructed law')
        values = tuple(law.step(s, a) for s, a in KEYS)
        # This is a snapshot of an *immutable law object*, not 54 potentially
        # conflicting time-separated observations of an outside system.
        view = PinnedView(len(self._issued), values, table_digest(values))
        self._issued.append(view)
        return view

    def pin(self) -> PinnedView:
        return self._issued[-1]

    def _assert_owned(self, view: PinnedView) -> None:
        if (type(view) is not PinnedView or type(view.version) is not int or
                not (0 <= view.version < len(self._issued)) or
                self._issued[view.version] is not view):
            raise ValueError('view was not issued by this source-owned instance')
        if table_digest(view.values) != view.digest:
            raise ValueError('pinned table integrity failed')

    def current(self, view: PinnedView) -> bool:
        self._assert_owned(view)
        return view is self.pin()

    def bind(self, source: FiniteSystem, prior: Discovery, view: PinnedView) -> BoundCorrespondence:
        """Prove old recorded full H against this exact owned version."""
        self._assert_owned(view)
        if type(source) is not FiniteSystem or not verify_recorded_full(source, prior):
            raise ValueError('missing valid full A/B mathematical witness')
        recorded = {(o.state, o.action): o.output for o in prior.observed}
        if len(recorded) != len(KEYS) or any(recorded[k] != view.values[i] for i, k in enumerate(KEYS)):
            raise ValueError('recorded witness does not describe this pinned version')
        return BoundCorrespondence(view, source.phi, witness_digest(prior))

    def reenter(self, source: FiniteSystem, prior: Discovery, bound: BoundCorrespondence,
                *, current: PinnedView | None = None) -> IdentityResult:
        """Decide whether previously admitted H describes a pinned version.

        Requires the SAME issuing owner object. With unchanged version, the
        earlier fully checked correspondence remains a valid mathematical
        witness without requerying a live target. A new version is compared as
        a full table (54 local entries); digest alone is not treated as source
        authentication and cannot prove unchanged intervening history.
        """
        if type(bound) is not BoundCorrespondence or type(source) is not FiniteSystem:
            return IdentityResult('WALL_INVALID', 'invalid witness or source')
        try:
            self._assert_owned(bound.view)
            if (source.phi != bound.source_phi or
                    not verify_recorded_full(source, prior) or
                    bound.proof_digest != witness_digest(prior)):
                return IdentityResult('WALL_INVALID', 'source or recorded witness changed')
            # Recheck that a saved record actually belongs to the pinned table.
            recorded = {(o.state, o.action): o.output for o in prior.observed}
            if len(recorded) != len(KEYS) or any(recorded[k] != bound.view.values[i] for i, k in enumerate(KEYS)):
                return IdentityResult('WALL_INVALID', 'original bound witness no longer verifies')
            newer = self.pin() if current is None else current
            self._assert_owned(newer)
        except (ValueError, AttributeError, TypeError):
            return IdentityResult('UNKNOWN_UNBOUND', 'issuer and immutable source identity not established')
        if newer is bound.view:
            return IdentityResult('SAME_PINNED_VERSION',
                                  'full A/B correspondence reused for the same immutable owned version; '
                                  'not a claim about an outside live target', inspected_edges=0)
        for i, ((state, action), old, new) in enumerate(zip(KEYS, bound.view.values, newer.values), 1):
            if old != new:
                return IdentityResult('CHANGED',
                                      'different owned-version transition; old H cannot transfer automatically',
                                      (state, action, old, new), i)
        return IdentityResult('SAME_ENDPOINT_LAW_NEW_VERSION',
                              '54 table entries equal in two owner-held snapshots; '
                              'intervening versions may differ and live continuity is unproved',
                              inspected_edges=54)


def unbound_external_identity(claimed_id: str, claimed_revision: int, claimed_hash: str) -> IdentityResult:
    """A provider-supplied label, clock, or hash is NOT a provenance witness."""
    return IdentityResult('UNKNOWN_UNBOUND', 'unverified external id/revision/hash cannot prove current identity')


def mutable_scan_counterexample(source: FiniteSystem, prior: Discovery, old: PinnedView):
    """An unsafe black-box reread whose 54 observations all match while it changes.

    On first read, return old first edge THEN mutate that edge permanently.
    The scanner will not revisit it. This witnesses the temporal limitation.
    """
    present = dict(zip(KEYS, old.values))
    count = 0
    def read(s: State, a: str) -> State:
        nonlocal count
        count += 1
        v = present[(s, a)]
        if count == 1:
            present[(s, a)] = ((v[0] + 1) % 3, v[1], v[2])
        return v
    result = recheck_full_record(source, prior, read)
    return result, count, present[KEYS[0]] != old.values[0]


def main() -> None:
    from ab_chatbot_discovered_correspondence import discover
    from ab_chatbot_discovered_correspondence import DOMAIN
    phi = (0, 0, 0)
    src = FiniteSystem(phi)
    h = tuple((i, j, (k + i * j) % 3) for i, j, k in DOMAIN)
    owner = OwnedVersions(TransportedLaw(phi, h))
    snap0 = owner.pin()
    prior = discover(src, snap0.step, full=True)
    assert prior.status == 'FULL_CONJUGACY'
    record = owner.bind(src, prior, snap0)
    print('first:', owner.reenter(src, prior, record).status)
    phi2 = (0, 0, 1)
    owner.replace(TransportedLaw(phi2, h))
    print('new law:', owner.reenter(src, prior, record).status)
    owner.replace(TransportedLaw(phi, h))
    print('returned law:', owner.reenter(src, prior, record).status,
          '(equal endpoint snapshots, NOT unchanged history)')
    scan, calls, moved = mutable_scan_counterexample(src, prior, snap0)
    print('unfrozen scan:', scan.status, 'calls:', calls, 'actually changed:', moved)
    print('external claimed revision:', unbound_external_identity('target', 0, snap0.digest).status)


if __name__ == '__main__':
    main()
