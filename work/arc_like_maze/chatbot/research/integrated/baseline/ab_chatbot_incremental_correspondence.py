"""Incremental, witness-preserving finite A/B correspondence continuation.

Mathematical scope: the declared deterministic F3^3 two-generator laws.
An origin-rooted orbit is A/B-invariant; reaching a *different* orbit requires
choosing another starting state, not a newly invented third generator.

A certified partial map is a bijective A/B-intertwiner on its whole union of
closed rooted orbits. Extend it without querying previously recorded edges.
The recorded table is trusted as an observation of the *same* target oracle;
neither a digest nor an opaque source label proves external source identity.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import (
    DOMAIN, DOMAIN_SET, Discovery, Observation, ZERO,
)

State = tuple[int, int, int]
Step = Callable[[State, str], State]
SCHEMA = 'incremental-rooted-a-b-v1'


def _is_state(s: object) -> bool:
    return type(s) is tuple and len(s) == 3 and all(type(x) is int and x in (0, 1, 2) for x in s)


def _wire(source_phi: tuple[int, int, int], target_id: str,
          anchors: tuple[tuple[State, State], ...],
          pairs: tuple[tuple[State, State], ...],
          observations: tuple[Observation, ...]) -> dict:
    return {
        'schema': SCHEMA, 'source_phi': list(source_phi), 'target_id': target_id,
        'anchors': [[list(s), list(t)] for s, t in anchors],
        'pairs': [[list(s), list(t)] for s, t in pairs],
        'observations': [[list(x.state), x.action, list(x.output)] for x in observations],
    }


def _hash(payload: dict) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class PartialWitness:
    source_phi: tuple[int, int, int]
    target_id: str
    anchors: tuple[tuple[State, State], ...]
    pairs: tuple[tuple[State, State], ...]
    observations: tuple[Observation, ...]
    digest: str

    @property
    def mapped(self) -> int:
        return len(self.pairs)

    def payload(self) -> dict:
        record = _wire(self.source_phi, self.target_id, self.anchors, self.pairs, self.observations)
        record['digest'] = self.digest
        return record

    def snapshot(self) -> str:
        return json.dumps(self.payload(), sort_keys=True, indent=2)

    def verify(self, source: FiniteSystem, *, target_id: str) -> None:
        """Replay all saved A/B squares without consulting an external oracle.

        This checks internal proof consistency, NOT authenticity of an external log.
        """
        if type(source) is not FiniteSystem or self.source_phi != source.phi or self.target_id != target_id:
            raise ValueError('source law or target identity differs from the witnessed record')
        if not self.target_id or self.digest != _hash(_wire(
                self.source_phi, self.target_id, self.anchors, self.pairs, self.observations)):
            raise ValueError('record integrity or target label failed')
        forward = dict(self.pairs)
        inv = {t: s for s, t in self.pairs}
        table = {(o.state, o.action): o.output for o in self.observations}
        if (not self.pairs or len(forward) != len(self.pairs) or len(inv) != len(self.pairs)
                or len(table) != len(self.observations) or len(self.pairs) > 27):
            raise ValueError('not a bijective uniquely observed correspondence')
        if self.pairs != tuple(sorted(self.pairs)):
            raise ValueError('pairs not canonical')
        if any(not (_is_state(s) and _is_state(t)) for s, t in self.pairs):
            raise ValueError('invalid mapped state')
        if any(not (_is_state(o.state) and _is_state(o.output) and o.action in ('A', 'B'))
               for o in self.observations):
            raise ValueError('invalid recorded transition')
        if (not self.anchors or len(set(self.anchors)) != len(self.anchors)
                or any(forward.get(s) != t for s, t in self.anchors)):
            raise ValueError('unwitnessed anchor')
        for s, t in self.pairs:
            for a in 'AB':
                if (t, a) not in table or forward.get(source.step(s, a)) != table[(t, a)]:
                    raise ValueError('incomplete or contradictory A/B generator square')
        if len(forward) == 27 and (set(forward) != DOMAIN_SET or set(forward.values()) != DOMAIN_SET):
            raise ValueError('incorrect full-domain coverage')

    @classmethod
    def reenter(cls, snapshot: str, source: FiniteSystem, *, target_id: str) -> 'PartialWitness':
        raw = json.loads(snapshot)
        if type(raw) is not dict or set(raw) != {
                'schema', 'source_phi', 'target_id', 'anchors', 'pairs', 'observations', 'digest'}:
            raise ValueError('invalid snapshot schema')
        if raw['schema'] != SCHEMA:
            raise ValueError('unknown witness schema')
        try:
            source_phi = tuple(raw['source_phi'])
            anchors = tuple((tuple(s), tuple(t)) for s, t in raw['anchors'])
            pairs = tuple((tuple(s), tuple(t)) for s, t in raw['pairs'])
            obs = tuple(Observation(tuple(s), a, tuple(t)) for s, a, t in raw['observations'])
            packet = cls(source_phi, raw['target_id'], anchors, pairs, obs, raw['digest'])
            packet.verify(source, target_id=target_id)
        except (TypeError, KeyError, IndexError) as exc:
            raise ValueError('malformed witness') from exc
        return packet


def _seal(source: FiniteSystem, target_id: str,
          anchors: list[tuple[State, State]], forward: dict[State, State],
          table: dict[tuple[State, str], State]) -> PartialWitness:
    pairs = tuple(sorted(forward.items()))
    observations = tuple(Observation(s, a, v) for (s, a), v in table.items())
    witness = PartialWitness(source.phi, target_id, tuple(anchors), pairs,
                             observations, _hash(_wire(source.phi, target_id, tuple(anchors), pairs, observations)))
    witness.verify(source, target_id=target_id)
    return witness


def from_discovery(source: FiniteSystem, record: Discovery, *, target_id: str) -> PartialWitness:
    """Recheck a previously witnessed, *completed rooted* correspondence."""
    if record.status != 'ROOTED_REACHABLE' or record.full_pairs:
        raise ValueError('requires the complete rooted-only result from discovery')
    if (len(dict(record.rooted_pairs)) != len(record.rooted_pairs)
            or len({(o.state, o.action) for o in record.observed}) != len(record.observed)):
        raise ValueError('ambiguous original discovery record')
    return _seal(source, target_id, [(ZERO, ZERO)], dict(record.rooted_pairs),
                 {(o.state, o.action): o.output for o in record.observed})


class _Budget(Exception):
    pass


class _Invalid(Exception):
    pass


@dataclass(frozen=True)
class Audit:
    status: str  # PRESERVED / CHANGED / WALL_INVALID_OBSERVATION
    calls: int
    mismatch: tuple[State, str, object, State] | None = None


@dataclass(frozen=True)
class Continuation:
    status: str
    witness: PartialWitness
    new_queries: int
    attempted_anchors: int
    detail: str = ''


class Incremental:
    """Maintains a fixed oracle and immutable, locally verified proof snapshots."""

    def __init__(self, source: FiniteSystem, observe_target: Step, previous: PartialWitness,
                 *, target_id: str):
        previous.verify(source, target_id=target_id)
        self.source = source
        self.oracle = observe_target
        self.target_id = target_id
        self.current = previous

    def audit_previous(self) -> Audit:
        """Explicitly re-observe cached evidence when oracle continuity is in doubt.

        Auditing costs one query per cached edge; normal incremental continuation
        makes the *declared assumption* that its target source did not change.
        """
        self.current.verify(self.source, target_id=self.target_id)
        calls = 0
        for saved in self.current.observations:
            actual = self.oracle(saved.state, saved.action)
            calls += 1
            if not _is_state(actual):
                return Audit('WALL_INVALID_OBSERVATION', calls,
                             (saved.state, saved.action, actual, saved.output))
            if actual != saved.output:
                return Audit('CHANGED', calls,
                             (saved.state, saved.action, actual, saved.output))
        return Audit('PRESERVED', calls)

    def _continue(self, candidates: tuple[tuple[State, State], ...], *, max_new_queries: int,
                  max_anchor_attempts: int | None = None) -> Continuation:
        if type(max_new_queries) is not int or max_new_queries < 0:
            raise ValueError('max_new_queries must be nonnegative')
        if max_anchor_attempts is not None and (type(max_anchor_attempts) is not int or max_anchor_attempts < 0):
            raise ValueError('max_anchor_attempts must be nonnegative')
        original = self.current
        original.verify(self.source, target_id=self.target_id)
        forward = dict(original.pairs)
        backward = {t: s for s, t in original.pairs}
        table = {(o.state, o.action): o.output for o in original.observations}
        first_len = len(table)
        tries = 0

        def save(fwd: dict[State, State] | None = None,
                 anchors: list[tuple[State, State]] | None = None):
            nonlocal forward
            witness = _seal(self.source, self.target_id,
                            anchors if anchors is not None else list(original.anchors),
                            fwd if fwd is not None else forward, table)
            self.current = witness
            return witness

        def read(t: State, a: str) -> State:
            if (t, a) not in table:
                if len(table) - first_len >= max_new_queries:
                    raise _Budget()
                out = self.oracle(t, a)
                if not _is_state(out):
                    raise _Invalid()
                table[t, a] = out
            return table[t, a]

        for source_anchor, target_anchor in candidates:
            if max_anchor_attempts is not None and tries >= max_anchor_attempts:
                return Continuation('UNKNOWN_SEARCH_BUDGET', save(), len(table) - first_len, tries)
            tries += 1
            if source_anchor in forward or target_anchor in backward:
                if forward.get(source_anchor) == target_anchor:
                    return Continuation('UNCHANGED', save(), len(table) - first_len, tries)
                continue
            stage = dict(forward)
            stage_inv = dict(backward)
            queue = deque([(source_anchor, target_anchor)])
            compatible = True
            try:
                while queue:
                    s, t = queue.popleft()
                    if s in stage:
                        if stage[s] != t or stage_inv.get(t) != s:
                            compatible = False
                            break
                        continue
                    if t in stage_inv:
                        compatible = False
                        break
                    stage[s] = t
                    stage_inv[t] = s
                    for a in 'AB':
                        queue.append((self.source.step(s, a), read(t, a)))
            except _Budget:
                return Continuation('UNKNOWN_QUERY_BUDGET', save(), len(table) - first_len, tries,
                                    'new orbit not yet completely witnessed')
            except _Invalid:
                return Continuation('WALL_INVALID_OBSERVATION', save(), len(table) - first_len, tries)
            if not compatible:
                continue
            next_anchors = [*original.anchors, (source_anchor, target_anchor)]
            new = save(stage, next_anchors)
            return Continuation('FULL_CONJUGACY' if new.mapped == len(DOMAIN) else 'EXTENDED',
                                new, len(table) - first_len, tries)
        return Continuation('ANCHOR_OBSTRUCTED', save(), len(table) - first_len, tries,
                            'none of the requested anchor pairings extended the preserved map')

    def extend_at(self, source_anchor: State, target_anchor: State, *,
                  max_new_queries: int = 54) -> Continuation:
        """A newly observed anchor pairing extends one whole A/B orbit."""
        if not _is_state(source_anchor) or not _is_state(target_anchor):
            raise ValueError('anchors must lie in F3^3')
        return self._continue(((source_anchor, target_anchor),), max_new_queries=max_new_queries)

    def extend_next(self, *, max_new_queries: int = 54,
                    max_anchor_attempts: int | None = None) -> Continuation:
        """Find a compatible new orbit anchor, without a supplied H."""
        mapped = dict(self.current.pairs)
        if len(mapped) == len(DOMAIN):
            return Continuation('UNCHANGED', self.current, 0, 0, 'full state already covered')
        next_source = next(s for s in DOMAIN if s not in mapped)
        used = set(mapped.values())
        candidates = tuple((next_source, t) for t in DOMAIN if t not in used)
        return self._continue(candidates, max_new_queries=max_new_queries,
                              max_anchor_attempts=max_anchor_attempts)


def main():
    from ab_chatbot_discovered_correspondence import discover, verify_recorded_full
    from ab_chatbot_admission_probe import OffOrbitAlteration
    from ab_chatbot_witness_transport import Shear, SourceWitness, ReachedWitness
    from ab_chatbot_structural_witness import CovariantSource

    source = FiniteSystem((0, 0, 0))
    target = ReachedWitness(SourceWitness.establish(CovariantSource.for_law(source.phi))).transport(Shear(1))
    initial = from_discovery(source, discover(source, target.step, full=False), target_id='native-shear-1')
    tracker = Incremental(source, target.step, initial, target_id='native-shear-1')
    print('rooted states:', initial.mapped, 'recorded target edges:', len(initial.observations))
    for i in range(2):
        result = tracker.extend_next()
        print(f'turn={i + 1} status={result.status} mapped={result.witness.mapped} '
              f'new_queries={result.new_queries} attempted_anchors={result.attempted_anchors}')
    assert tracker.current.mapped == 27
    assert len(tracker.current.observations) == 54
    print('full correspondence from preserved three rooted carriers: 54 distinct total edges')
    altered = OffOrbitAlteration()
    first = from_discovery(source, discover(source, altered.step, full=False), target_id='altered-oracle')
    outsider = Incremental(source, altered.step, first, target_id='altered-oracle')
    outcome = outsider.extend_next()
    print('off-orbit alternative:', outcome.status, 'new queries:', outcome.new_queries,
          '(no global conclusion from a partial attempt)')


if __name__ == '__main__':
    main()
