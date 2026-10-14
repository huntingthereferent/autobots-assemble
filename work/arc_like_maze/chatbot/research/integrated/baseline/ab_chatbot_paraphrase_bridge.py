"""Bounded utterance-equivalence test over an existing A/B mathematical observer.

Language grounding: A/B names relationships continuing through movement; its
finite labelled generator models here are translations, not its definition.
Only admitted explicit utterances are rewritten. The original bridge alone
owns observation, budgets, pinned revision, witnesses, and UNKNOWN states.

This module uses deterministic lexical recognition, not general NLP.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import Literal

from ab_chatbot_language_bridge import GroundedTurn, LanguageBridge, MAX_WORD_LENGTH

ReadingStatus = Literal['ADMITTED', 'UNRESOLVED', 'PASS_THROUGH']
SemanticKey = tuple[str, ...]


@dataclass(frozen=True)
class LanguageReading:
    original: str
    status: ReadingStatus
    canonical: str | None
    semantic_key: SemanticKey | None
    basis: str


@dataclass(frozen=True)
class RecordedAnswer:
    reading: LanguageReading
    answer: GroundedTurn


# No guessing pronouns, unseen state, implicit actions, or operator semantics.
# All forms are independently bound to the same declared origin and version.
_EQUAL_FORMS = (
    ("existing_comparison",
     r'does (.+?) (?:reach|end up) (?:in )?the same (?:state|place) as (.+)\?'),
    ("two_paths_same_endpoint",
     r'do (.+?) and (.+?) end (?:at|in) the same (?:state|place)\?'),
    ("two_paths_same_result",
     r'do (.+?) and (.+?) (?:lead to|reach) the same (?:state|place)\?'),
    ("equal_endpoints",
     r'are the endpoints (?:of|after) (.+?) and (.+?) (?:equal|the same)\?'),
    ("explicit_origin_comparison",
     r'from the origin, do (.+?) and (.+?) (?:end|finish) (?:at|in) the same (?:state|place)\?'),
)
_ENDPOINT_FORMS = (
    ("existing_endpoint_1", r'where do i end up after (.+)\?'),
    ("existing_endpoint_2", r'where does (.+) end up\?'),
    ("ask_state", r'what state do i reach after (.+)\?'),
    ("after_what_state", r'after (.+?), what state do i reach\?'),
    ("explicit_origin_endpoint", r'from the origin, where does (.+?) end\?'),
)
_CONTINUE_FORMS = (
    ("existing_followup", r'and then ([ab])\?'),
    ("explicit_next", r'continue with ([ab])\.'),
    ("explicit_followup", r'and next, ([ab])\?'),
)
_REPLAY_FORMS = (
    ("existing_replay", r'show (?:the )?witness\.?'),
    ("witness_replay", r'replay (?:the )?path\.?'),
)


def _word(s: str) -> str | None:
    # Reuse the existing action grammar and its length bound.
    w = LanguageBridge._parse_word(s)
    return w if w is not None and 0 < len(w) <= MAX_WORD_LENGTH else None


def _normalize(text: str) -> str:
    # Whitespace/case are purely surface-level. Internal meaning is NOT guessed.
    return ' '.join(text.strip().lower().split())


def decode(text: str) -> LanguageReading:
    """Return an exact semantic key only when a listed reading is justified.

    Equality of endpoints is a symmetric proposition; witness display order
    remains in the user's order, never silently reversed.
    """
    if type(text) is not str or not text.strip():
        return LanguageReading(str(text), 'UNRESOLVED', None, None, 'missing_question')
    normalized = _normalize(text)

    for basis, pattern in _EQUAL_FORMS:
        m = re.fullmatch(pattern, normalized)
        if m:
            a, b = map(_word, m.groups())
            if a is None or b is None:
                return LanguageReading(text, 'UNRESOLVED', None, None,
                                       basis + ':invalid_action_word')
            # The original bridge is the only mathematical observer.
            canonical = f'Does {a} reach the same state as {b}?'
            key = ('equal_endpoints', 'origin=(0,0,0)', *sorted((a, b)))
            return LanguageReading(text, 'ADMITTED', canonical, key, basis)

    for basis, pattern in _ENDPOINT_FORMS:
        m = re.fullmatch(pattern, normalized)
        if m:
            w = _word(m.group(1))
            if w is None:
                return LanguageReading(text, 'UNRESOLVED', None, None,
                                       basis + ':invalid_action_word')
            return LanguageReading(text, 'ADMITTED',
                                   f'Where do I end up after {w}?',
                                   ('endpoint', 'origin=(0,0,0)', w), basis)

    for basis, pattern in _CONTINUE_FORMS:
        m = re.fullmatch(pattern, normalized)
        if m:
            a = m.group(1).upper()
            return LanguageReading(text, 'ADMITTED', f'And then {a}?',
                                   # The previous path must be checked by base.
                                   ('continue', 'active_pinned_path', a), basis)

    for basis, pattern in _REPLAY_FORMS:
        m = re.fullmatch(pattern, normalized)
        if m:
            return LanguageReading(text, 'ADMITTED', 'Show the witness',
                                   ('replay', 'active_pinned_path'), basis)

    # Retain existing ground/class/repin/temporal status handling unchanged.
    # This is not a separate semantic parser for those legacy questions.
    if normalized in (
        'what does a/b mean?', 'what is a/b?', 'is this a/b?',
        'does this prove a/b?', 'is a/b universal?',
        'has the system stayed the same?', 'is the target unchanged?',
        'has the target remained unchanged?',
        'which a/b relationship class fits?', 'which relationship class fits?',
        'pin current version', 'pin current version.',
        'open current version', 'open current version.',
        'pin the current version', 'pin the current version.',
        'open the current version', 'open the current version.',
    ):
        return LanguageReading(text, 'PASS_THROUGH', text, None,
                               'existing_bridge_exact_language')

    return LanguageReading(text, 'UNRESOLVED', None, None,
                           'no_admitted_paraphrase')


class ParaphraseBridge:
    """One language boundary over the existing observer, never a new engine.

    The canonical phrase is stored next to the original utterance, but the
    original utterance must remain on the underlying mathematical turn too.
    Any unresolved reading is sent unchanged to the base bridge so its already
    defined walls (including temporal continuity) remain authoritative.
    """

    def __init__(self, bridge: LanguageBridge):
        self.bridge = bridge
        self.history: list[RecordedAnswer] = []

    def ask(self, text: str, *, max_class_probes: int = 3) -> GroundedTurn:
        reading = decode(text)
        forwarded = reading.canonical if reading.status == 'ADMITTED' else text
        answer = self.bridge.ask(forwarded, max_class_probes=max_class_probes)
        if answer.user_text != text:
            answer = replace(answer, user_text=text)
            # No double history entry. Preserve the one existing answer and
            # its witness under exactly the same source revision and scope.
            self.bridge.history[-1] = answer
        self.history.append(RecordedAnswer(reading, answer))
        return answer


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP, SourceOwnedHTTP, RemoteObserver
    from ab_chatbot_stability_witness import TransportedLaw

    shear = tuple((i, j, (k + i*j) % 3) for i, j, k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw((0, 1, 2), shear))
    with LoopbackHTTP(owner) as server:
        remote = RemoteObserver(server.url)
        base = LanguageBridge(remote, owner=owner)
        bot = ParaphraseBridge(base)
        for q in (
            'Do A then B and B then A end in the same place?',
            'Are the endpoints of AB and BA equal?',
            'Do BA and AB lead to the same state?',
            'What state do I reach after A then B?',
            'Continue with B.',
            'Replay the path.',
            'Do AB and BA end at different states?',
        ):
            answer = bot.ask(q)
            reading = bot.history[-1].reading
            print(f'{q}\n  {answer.status} | key={reading.semantic_key} | '
                  f'canonical={reading.canonical!r} | edge_count={len(base.snapshot.edges)}')
        print(f'Network requests: {remote.calls}')


if __name__ == '__main__':
    main()
