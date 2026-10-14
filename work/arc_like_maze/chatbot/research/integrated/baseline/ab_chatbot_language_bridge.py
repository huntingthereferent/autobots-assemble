"""Tiny language interface to an existing, *bounded* A/B-labeled finite model.

Ground: A/B is the investigator's language for recognizing, describing, and
continuing relationships in movement (A/B Ground Record, 2026-10-11).
This program is a narrow communication experiment, NOT a definition of A/B,
an open-ended NL interpreter, or a new general mathematical decision engine.

Questions enter a fixed declared grammar; movement/observations use the
existing finite probe and the source-owned HTTP snapshot experiment. The
original utterance, fixed snapshot, translated claim and witnessed transitions
are recorded together; ambiguous language returns UNKNOWN, not inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from urllib.parse import urlencode
from urllib.error import URLError
import re
from typing import Literal

from ab_chatbot_relation_probe import FiniteSystem, build_probes, identify
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, RemoteSnapshot, SourceOwnedHTTP
from ab_chatbot_discovered_correspondence import DOMAIN_SET

State = tuple[int, int, int]
Pair = tuple[str, str]
OriginStatus = Literal['LOCAL_OWNER_VERIFIED', 'REMOTE_ORIGIN_UNVERIFIED']
ZERO: State = (0, 0, 0)
NINE = tuple(FiniteSystem((0, a, b)) for a, b in product(range(3), repeat=2))
PROBES = build_probes(NINE)
MAX_WORD_LENGTH = 24


class ObservationWall(Exception):
    """Missing or incompatible observed edge: no mathematical answer admitted."""


class EdgeBudgetReached(Exception):
    """An otherwise admissible observation exceeds the declared request budget."""


class PinnedEdges:
    """Revision-specific HTTP transition observer, NOT a 54-entry table read.

    One /head selects a claimed revision. Every edge is then requested at that
    revision and checked against its source label and digest. The HTTP server
    must preserve historical revisions; a remote untrusted provider can lie.
    """

    def __init__(self, client: RemoteObserver, max_edges: int = 12):
        if type(max_edges) is not int or max_edges < 0 or max_edges > 54:
            raise ValueError('edge budget must be an integer between 0 and 54')
        self.client = client
        self.max_edges = max_edges
        h = client.head()
        self.claimed_source = h['source']
        self.revision = h['revision']
        self.digest = h['digest']
        if (not self.claimed_source or self.revision < 0 or
                not re.fullmatch(r'[0-9a-f]{64}', self.digest)):
            raise ObservationWall('invalid source-reported version metadata')
        self.edges: dict[tuple[State, str], State] = {}
        self.owner_view = None  # populated only after explicit local binding

    def step(self, state: State, action: str) -> State:
        if state not in DOMAIN_SET or action not in ('A', 'B'):
            raise ObservationWall('action or state falls outside the declared finite domain')
        key = (state, action)
        if key not in self.edges:
            if len(self.edges) >= self.max_edges:
                raise EdgeBudgetReached('unique-transition observation budget exhausted')
            path = '/step/' + str(self.revision) + '?' + urlencode({
                'state': ','.join(map(str, state)), 'action': action})
            try:
                raw = self.client.request(path)
            except (URLError, OSError, ValueError) as err:
                raise ObservationWall(f'pinned observation unavailable: {type(err).__name__}') from err
            if (raw.get('source') != self.claimed_source or
                    raw.get('revision') != self.revision or
                    raw.get('digest') != self.digest or
                    raw.get('state') != list(state) or raw.get('action') != action or
                    type(raw.get('output')) is not list):
                raise ObservationWall('pinned observation provenance/shape conflict')
            candidate = tuple(raw['output'])
            if (type(candidate) is not tuple or len(candidate) != 3 or
                    any(type(v) is not int or v not in (0, 1, 2) for v in candidate)):
                raise ObservationWall('invalid transition output')
            if self.owner_view is not None and candidate != self.owner_view.step(state, action):
                raise ObservationWall('transition differs from trusted local owner view')
            self.edges[key] = candidate
        return self.edges[key]


@dataclass(frozen=True)
class PathWitness:
    word: str
    states: tuple[State, ...]


@dataclass(frozen=True)
class GroundedTurn:
    user_text: str
    referent: str
    status: str
    message: str
    revision: int
    claimed_source: str
    digest: str
    origin_scope: OriginStatus
    formal_question: str | None = None
    paths: tuple[PathWitness, ...] = ()
    class_candidates: tuple[tuple[int, int, int], ...] = ()
    class_probes: tuple[tuple[Pair, bool], ...] = ()
    # Prior grounding is preserved across an explicit repin, not overwritten.


class _ProbeBudget(Exception):
    pass


class LanguageBridge:
    """Only routes explicitly admitted utterance shapes into existing math.

    `owner` is optional same-process provenance, not an HTTP claim of trust.
    A remote caller with no owner can inspect mathematical relations in the
    delivered snapshot but cannot certify whose source produced its bytes.
    """

    def __init__(self, remote: RemoteObserver, *, owner: SourceOwnedHTTP | None = None,
                 mode: Literal['edges', 'snapshot'] = 'edges', edge_budget: int = 12):
        if mode not in ('edges', 'snapshot'):
            raise ValueError('unsupported observation mode')
        if type(edge_budget) is not int or not 0 <= edge_budget <= 54:
            raise ValueError('invalid edge budget (0..54)')
        self.remote = remote
        self.owner = owner
        self.mode = mode
        self.edge_budget = edge_budget
        self.snapshot: RemoteSnapshot | PinnedEdges = self._read_version()
        self.origin_scope: OriginStatus = self._scope(self.snapshot)
        self._last_path: PathWitness | None = None
        self.history: list[GroundedTurn] = []

    def _read_version(self) -> RemoteSnapshot | PinnedEdges:
        return (PinnedEdges(self.remote, self.edge_budget) if self.mode == 'edges'
                else self.remote.snapshot())

    def _scope(self, snap: RemoteSnapshot | PinnedEdges) -> OriginStatus:
        # A remote source can copy an honest owner's label, revision, digest,
        # and even transition values. This cannot attest provenance. Require
        # an active, explicitly bound *in-process* LoopbackHTTP handle whose
        # source object IS the supplied owner, then verify returned values.
        link = self.remote.bound_loopback if type(self.remote) is RemoteObserver else None
        if (self.owner is None or type(link) is not LoopbackHTTP or
                link.source is not self.owner or link.server is None or
                self.remote.url != link.url):
            return 'REMOTE_ORIGIN_UNVERIFIED'
        if isinstance(snap, RemoteSnapshot):
            return ('LOCAL_OWNER_VERIFIED' if self.owner.owned_view(snap) is not None
                    else 'REMOTE_ORIGIN_UNVERIFIED')
        view = self.owner.select(snap.revision)
        if (snap.claimed_source == self.owner.source_id and view is not None
                and view.digest == snap.digest):
            snap.owner_view = view
            return 'LOCAL_OWNER_VERIFIED'
        return 'REMOTE_ORIGIN_UNVERIFIED'

    def _turn(self, text: str, status: str, message: str, *, formal_question=None,
              paths=(), class_candidates=(), class_probes=()) -> GroundedTurn:
        snap = self.snapshot
        t = GroundedTurn(text, 'A/B chatbot: continuing a witnessed relationship',
                         status, message, snap.revision, snap.claimed_source,
                         snap.digest, self.origin_scope, formal_question,
                         tuple(paths), tuple(class_candidates), tuple(class_probes))
        self.history.append(t)
        # A follow-up may extend only the currently active endpoint referent,
        # not a path made stale by an intervening comparison or new question.
        if status not in ('WITNESSED_ENDPOINT', 'WITNESS_REPLAY'):
            self._last_path = None
        return t

    @staticmethod
    def _parse_word(phrase: str) -> str | None:
        """Explicit A/B action phrases only. No semantic guesses or synonyms."""
        s = phrase.strip().upper()
        if re.fullmatch(r'[AB]{1,24}', s):
            return s
        if re.fullmatch(r'[AB](?:\s+THEN\s+[AB])+', s):
            actions = re.split(r'\s+THEN\s+', s)
            word = ''.join(actions)
            return word if len(word) <= MAX_WORD_LENGTH else None
        return None

    def _follow(self, word: str) -> PathWitness:
        cur = ZERO
        path = [cur]
        for symbol in word:
            cur = self.snapshot.step(cur, symbol)
            path.append(cur)
        return PathWitness(word, tuple(path))

    @staticmethod
    def _text_path(path: PathWitness) -> str:
        return ' -> '.join(map(str, path.states))

    def ask(self, text: str, *, max_class_probes: int = 3) -> GroundedTurn:
        try:
            return self._route(text, max_class_probes=max_class_probes)
        except ObservationWall as err:
            return self._turn(str(text), 'WALL_OBSERVATION',
                              f'An observation could not be admitted: {err}. '
                              'No mathematical result is asserted.')
        except EdgeBudgetReached:
            return self._turn(str(text), 'UNKNOWN_BUDGET',
                              'Unique-transition budget exhausted on this pinned version. '
                              'Prior observations remain available; no new conclusion was admitted.')

    def _route(self, text: str, *, max_class_probes: int) -> GroundedTurn:
        if type(text) is not str or not text.strip():
            return self._turn(str(text), 'UNKNOWN_LANGUAGE',
                              'No unambiguous question was supplied; no mathematical movement admitted.')
        # Lexical routing is intentionally narrow. Preserve original text.
        q = text.strip()
        lower = q.lower()

        if re.fullmatch(r'(?:pin|open) (?:the )?current version\.?', lower):
            try:
                snap = self._read_version()
            except (ValueError, URLError, OSError) as err:
                return self._turn(q, 'WALL_OBSERVATION',
                                  f'Could not open a new version: {type(err).__name__}. '
                                  'The previous pinned referent is unchanged.')
            old = self.snapshot
            self.snapshot = snap
            self.origin_scope = self._scope(snap)
            self._last_path = None   # never extend an old trace in a new version
            return self._turn(q, 'PINNED_VERSION',
                              f'Opened version {snap.revision}; earlier witnesses remain in history. '
                              f'Previous version {old.revision}; no uninterrupted-continuity claim.',
                              formal_question='open one source-reported historical version')

        if lower in ('what does a/b mean?', 'what is a/b?'):
            return self._turn(q, 'GROUNDING',
                              'A/B is language for recognizing, describing, and continuing relationships '
                              'in movement. This finite mathematical model is only one translation; '
                              'it does not define A/B.')

        if lower in ('is this a/b?', 'does this prove a/b?', 'is a/b universal?'):
            return self._turn(q, 'WALL_SCOPE',
                              'A finite A/B-labeled transformation example cannot prove what A/B '
                              'itself is, or that A/B holds universally.')

        if lower in ('has the system stayed the same?', 'is the target unchanged?',
                     'has the target remained unchanged?'):
            return self._turn(q, 'UNKNOWN_TEMPORAL_CONTINUITY',
                              'This pinned source-reported version carries an observed mathematical relation; '
                              'it cannot prove the target remained unchanged between moments.')

        if lower in ('show witness', 'show the witness', 'show witness.', 'show the witness.'):
            if self._last_path is None:
                return self._turn(q, 'UNKNOWN_CONTEXT',
                                  'There is no active endpoint path for this pinned version.')
            path = self._last_path
            return self._turn(q, 'WITNESS_REPLAY',
                              f'From the declared origin: {self._text_path(path)}. '
                              'All transitions were observed at the same pinned source-reported version.',
                              formal_question=f'transition path for word {path.word}', paths=(path,))

        followup = re.fullmatch(r'and then ([ab])\?', lower)
        if followup:
            if self._last_path is None:
                return self._turn(q, 'UNKNOWN_CONTEXT',
                                  'No previous endpoint path is available on the pinned version. '
                                  'State the initial actions explicitly.')
            word = self._last_path.word + followup.group(1).upper()
            if len(word) > MAX_WORD_LENGTH:
                return self._turn(q, 'WALL_LIMIT', 'Action word exceeds the 24-action local bound.')
            path = self._follow(word)
            self._last_path = path
            return self._turn(q, 'WITNESSED_ENDPOINT',
                              f'Continuing the same path with {word[-1]} reaches {path.states[-1]}.',
                              formal_question=f'from origin, follow {word}', paths=(path,))

        endpoint = (re.fullmatch(r'where do i end up after (.+)\?', lower)
                    or re.fullmatch(r'where does (.+) end up\?', lower))
        if endpoint:
            word = self._parse_word(endpoint.group(1))
            if word is None:
                return self._turn(q, 'UNKNOWN_LANGUAGE',
                                  'Expected an explicit A/B word, e.g. “A then B”. '
                                  'No unknown action was guessed.')
            path = self._follow(word)
            self._last_path = path
            return self._turn(q, 'WITNESSED_ENDPOINT',
                              f'From the declared origin, {word} ends at {path.states[-1]}.',
                              formal_question=f'from origin, follow {word}', paths=(path,))

        equal = re.fullmatch(r'does (.+?) (?:reach|end up) (?:in )?the same (?:state|place) as (.+)\?', lower)
        if equal:
            word1, word2 = (self._parse_word(x) for x in equal.groups())
            if word1 is None or word2 is None:
                return self._turn(q, 'UNKNOWN_LANGUAGE',
                                  'The two sequences must be explicit A/B words. '
                                  'No mathematical comparison was admitted.')
            p1, p2 = self._follow(word1), self._follow(word2)
            same = p1.states[-1] == p2.states[-1]
            # Do not change last_path on comparison; no implicit choice of "which path".
            return self._turn(q, 'WITNESSED_EQUALITY',
                              f'{word1} and {word2} have '
                              f'{"equal" if same else "different"} endpoints in this pinned version: '
                              f'{p1.states[-1]} and {p2.states[-1]}.',
                              formal_question=f'equal endpoints for action words {word1!r} and {word2!r}',
                              paths=(p1, p2))

        if lower in ('which a/b relationship class fits?', 'which relationship class fits?'):
            if type(max_class_probes) is not int or max_class_probes < 0:
                return self._turn(q, 'WALL_LIMIT', 'Invalid relational-query budget.')
            observations: list[tuple[Pair, bool]] = []
            bridge = self

            class ObservedEndpointRelation:
                def equal_ends(self, pair: Pair) -> bool:
                    if len(observations) >= max_class_probes:
                        raise _ProbeBudget()
                    observed = bridge._follow(pair[0]).states[-1] == bridge._follow(pair[1]).states[-1]
                    observations.append((pair, observed))
                    return observed

            try:
                remaining, _ = identify(NINE, ObservedEndpointRelation(), PROBES)
            except (_ProbeBudget, EdgeBudgetReached):
                return self._turn(q, 'UNKNOWN_BUDGET',
                                  f'Only {len(observations)} complete discriminating observations admitted; '
                                  'family-relative classification remains unresolved. '
                                  'Any already observed transition edges remain cached.',
                                  formal_question='nine-law rooted endpoint-equality class',
                                  class_probes=observations)
            # The original chooser uses candidate relations only, observing a pinned
            # mathematical target by endpoint equalities. It has no target phi.
            matched = tuple(NINE[i].phi for i in remaining)
            return self._turn(q, 'CONDITIONAL_CLASS',
                              f'These observations match {matched} among the nine declared candidates. '
                              'This does NOT establish that the unknown target belongs to that family.',
                              formal_question='rooted endpoint-equality class within nine fixed models',
                              class_candidates=matched, class_probes=observations)

        return self._turn(q, 'UNKNOWN_LANGUAGE',
                          'No supported exact reading of that question. '
                          'The original referent is preserved; no A/B operation or mathematical claim was inferred.')


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP
    from ab_chatbot_stability_witness import TransportedLaw

    phi = (0, 1, 2)
    h = tuple((i, j, (k + i * j) % 3) for i, j, k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw(phi, h))
    with LoopbackHTTP(owner) as http:
        bot = LanguageBridge(RemoteObserver(http.url), owner=owner)
        samples = (
            'What does A/B mean?',
            'Where do I end up after A then B?',
            'And then B?',
            'Show the witness',
            'Does A then B reach the same state as B then A?',
            'Which A/B relationship class fits?',
            'Has the system stayed the same?',
            'What if I take the other side?',
        )
        for q in samples:
            t = bot.ask(q)
            print(f'Q: {q}\n  {t.status}: {t.message}')
        print(f'HTTP requests: {bot.remote.calls} (one version header, then cached individual edges)')
        print(f'Distinct observed edges: {len(bot.snapshot.edges)}')


if __name__ == '__main__':
    main()
