"""Question identity and explicit re-entry for the bounded A/B chatbot experiment.

Ground (2026-10-11): A/B is relational language. The finite two-generator
mathematics is a deliberately limited translation, not A/B itself.

This *language-side record* distinguishes an utterance, its admitted formal
question, the actual witnessed answer, and the path by which it was obtained.
It never merges questions merely because their endpoints or truth values agree.
Only explicit references may resume an older path; the mathematical observer,
version identity and observation budgets remain owned by the earlier bridge.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from ab_chatbot_clarification_bridge import ClarificationBridge, ClarificationTurn
from ab_chatbot_language_bridge import GroundedTurn, MAX_WORD_LENGTH, PathWitness

Version = tuple[str, int, str, str]
SemanticKey = tuple[str, ...]


@dataclass(frozen=True)
class QuestionRecord:
    number: int
    utterance: str
    status: str
    message: str
    semantic_key: SemanticKey | None
    asked_as: str | None
    parent_question: int | None
    original_question: str | None
    version: Version
    answer: GroundedTurn | None
    paths: tuple[PathWitness, ...]
    # Source-owned identity is not inferred from equal numerical results.

    @property
    def endpoint(self):
        if self.status == 'WITNESSED_ENDPOINT' and len(self.paths) == 1:
            return self.paths[0].states[-1]
        return None

    @property
    def equality(self) -> bool | None:
        if self.status == 'WITNESSED_EQUALITY' and len(self.paths) == 2:
            return self.paths[0].states[-1] == self.paths[1].states[-1]
        return None


_REFERENCE_CONTINUE = re.compile(r'continue (?:from )?question ([1-9][0-9]*) with ([ab])\.', re.I)
_REFERENCE_REPLAY = re.compile(r'(?:show|replay) (?:the )?witness (?:for|of) question ([1-9][0-9]*)\.', re.I)


class QuestionLineageBridge:
    """Preserve distinct linguistic referents over one existing ClarificationBridge.

    History numbers are local to this session, never durable external IDs.
    A stored answer is historical evidence about its particular pinned
    source-reported version, not a claim about the current live target.
    """
    def __init__(self, clarification: ClarificationBridge):
        self.clarification = clarification
        self.history: list[QuestionRecord] = []
        self._active_endpoint_question: int | None = None

    def _current_version(self) -> Version:
        return self.clarification._version()

    def _store(self, utterance: str, status: str, message: str, *,
               semantic_key: SemanticKey | None = None,
               asked_as: str | None = None,
               parent_question: int | None = None,
               original_question: str | None = None,
               version: Version | None = None,
               answer: GroundedTurn | None = None) -> QuestionRecord:
        rec = QuestionRecord(
            len(self.history) + 1, utterance, status, message,
            semantic_key, asked_as, parent_question, original_question,
            self._current_version() if version is None else version, answer,
            answer.paths if answer is not None else ())
        self.history.append(rec)
        if rec.status == 'WITNESSED_ENDPOINT' and len(rec.paths) == 1:
            self._active_endpoint_question = rec.number
        elif rec.status != 'WITNESS_REPLAY':
            self._active_endpoint_question = None
        return rec

    def _find(self, number: int) -> QuestionRecord | None:
        if 1 <= number <= len(self.history):
            return self.history[number - 1]
        return None

    def _unknown(self, utterance: str, status: str, message: str, *,
                 parent: int | None = None) -> QuestionRecord:
        # This language-only refusal performs NO observation. Invalidate the
        # underlying implicit path too, so an unsupported reference cannot be
        # followed by an unanchored "and then B?" continuation.
        self.clarification.paraphrases.bridge._last_path = None
        return self._store(utterance, status, message, parent_question=parent)

    def _reading_key(self, turn: ClarificationTurn, parent: int | None) -> SemanticKey | None:
        if turn.selected is not None:
            return turn.selected.semantic_key
        if not turn.answer:
            return None
        a = turn.answer
        # The exact model action sequence is kept even when resulting states
        # happen to agree with another action sequence.
        if a.status == 'WITNESSED_ENDPOINT' and len(a.paths) == 1:
            if parent is not None:
                return ('continuation', f'parent_question={parent}', a.paths[0].word)
            return ('endpoint', 'origin=(0,0,0)', a.paths[0].word)
        if a.status == 'WITNESSED_EQUALITY' and len(a.paths) == 2:
            w1, w2 = (p.word for p in a.paths)
            return ('equal_endpoints', 'origin=(0,0,0)', *sorted((w1, w2)))
        if a.status == 'WITNESS_REPLAY' and parent is not None:
            return ('replay', f'parent_question={parent}')
        # Statuses like UNKNOWN_LANGUAGE and CONDITIONAL_CLASS aren't
        # assigned an endpoint semantic identity just to fill a field.
        return None

    def ask(self, utterance: str, *, max_class_probes: int = 3) -> QuestionRecord:
        if type(utterance) is not str:
            utterance = str(utterance)
        q = ' '.join(utterance.strip().split())
        go = _REFERENCE_CONTINUE.fullmatch(q)
        if go:
            num, symbol = int(go.group(1)), go.group(2).upper()
            parent = self._find(num)
            if self.clarification.pending is not None:
                return self._unknown(utterance, 'UNKNOWN_CONTEXT',
                                     'A clarification is pending. Resolve or withdraw it first.',
                                     parent=num)
            if parent is None:
                return self._unknown(utterance, 'UNKNOWN_REFERENT',
                                     'That numbered question is not in this conversation.',
                                     parent=num)
            if parent.status != 'WITNESSED_ENDPOINT' or len(parent.paths) != 1:
                return self._unknown(utterance, 'UNKNOWN_REFERENT',
                                     'That earlier question does not have one witnessed endpoint path.',
                                     parent=num)
            if parent.version != self._current_version():
                return self._unknown(utterance, 'UNKNOWN_VERSION',
                                     'The current pinned version differs from the historical question. '
                                     'No path was transferred between versions.', parent=num)
            word = parent.paths[0].word + symbol
            if len(word) > MAX_WORD_LENGTH:
                return self._unknown(utterance, 'WALL_LIMIT',
                                     'The requested continuation exceeds the local action bound.',
                                     parent=num)
            formal = f'Where do I end up after {word}?'
            turn = self.clarification.ask(formal, max_class_probes=max_class_probes)
            return self._store(utterance, turn.status,
                               f'Explicit continuation of question {num}: {turn.message}',
                               semantic_key=('continuation', f'parent_question={num}', word),
                               asked_as=formal, parent_question=num,
                               original_question=parent.original_question or parent.utterance,
                               version=turn.version, answer=turn.answer)

        show = _REFERENCE_REPLAY.fullmatch(q)
        if show:
            num = int(show.group(1))
            if self.clarification.pending is not None:
                return self._unknown(utterance, 'UNKNOWN_CONTEXT',
                                     'A clarification is pending. Resolve or withdraw it first.',
                                     parent=num)
            parent = self._find(num)
            if parent is None or not parent.paths or parent.status not in (
                    'WITNESSED_ENDPOINT', 'WITNESSED_EQUALITY', 'WITNESS_REPLAY'):
                return self._unknown(utterance, 'UNKNOWN_REFERENT',
                                     'No witnessed path is recorded for that numbered question.',
                                     parent=num)
            # Inspecting old evidence does not query or repin the mathematical
            # source, and may refer to a historical version not current today.
            # Do not make this old path the implicit focus of the next turn.
            self.clarification.paraphrases.bridge._last_path = None
            words = ', '.join(p.word for p in parent.paths)
            return self._store(utterance, 'HISTORICAL_WITNESS',
                               f'Question {num} used {words}, pinned revision '
                               f'{parent.version[1]}; this is its recorded witness, '
                               'not a fresh observation or claim of live continuity.',
                               semantic_key=('inspect_historical_witness', str(num)),
                               asked_as=None, parent_question=num,
                               original_question=parent.original_question or parent.utterance,
                               version=parent.version, answer=parent.answer)

        # Interpret the actual user's utterance at the existing narrow language
        # boundary. Clarification and all observed math remain in older layers.
        pending_before = self.clarification.pending
        pending_parent = next((r.number for r in reversed(self.history)
                               if pending_before is not None
                               and r.status in ('NEEDS_CLARIFICATION',
                                                'UNKNOWN_CLARIFICATION')
                               and r.original_question == pending_before.original), None)
        parent = None
        lower = q.lower()
        if lower in ('and then a?', 'and then b?', 'continue with a.',
                     'continue with b.', 'and next, a?', 'and next, b?',
                     'show witness', 'show witness.', 'show the witness',
                     'show the witness.', 'replay the path', 'replay the path.'):
            parent = self._active_endpoint_question
        turn = self.clarification.ask(utterance, max_class_probes=max_class_probes)
        if pending_parent is not None and (turn.selected is not None or turn.status in (
                'UNKNOWN_CLARIFICATION', 'CLARIFICATION_WITHDRAWN')):
            parent = pending_parent
        key = self._reading_key(turn, parent)
        asked_as = (turn.selected.canonical if turn.selected is not None else
                    self.clarification.paraphrases.history[-1].reading.canonical
                    if self.clarification.paraphrases.history else None)
        return self._store(utterance, turn.status, turn.message, semantic_key=key,
                           asked_as=asked_as, parent_question=parent,
                           original_question=turn.original_question,
                           version=turn.version, answer=turn.answer)


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_language_bridge import LanguageBridge
    from ab_chatbot_paraphrase_bridge import ParaphraseBridge
    from ab_chatbot_stability_witness import TransportedLaw

    h = tuple((i, j, (k+i*j)%3) for i, j, k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw((0,1,2), h))
    with LoopbackHTTP(owner) as server:
        bot = QuestionLineageBridge(ClarificationBridge(ParaphraseBridge(
            LanguageBridge(RemoteObserver(server.url), owner=owner))))
        for q in ('Where do I end up after A?',
                  'Where do I end up after AAAA?',
                  'Show witness for question 1.',
                  'Continue question 1 with B.',
                  'Does AB reach the same state as BA?',
                  'Does A reach the same state as B?'):
            r = bot.ask(q)
            print(f'{r.number}. {q}\n   {r.status} | semantic={r.semantic_key} '
                  f'| endpoint={r.endpoint} | equality={r.equality}')


if __name__ == '__main__':
    main()
