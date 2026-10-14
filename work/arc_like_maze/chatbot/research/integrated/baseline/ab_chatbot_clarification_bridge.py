"""Bounded one-question clarification above the existing A/B paraphrase bridge.

A/B is relational language, not the finite A/B generator model.  This module
only preserves competing linguistic readings of *supported finite questions*.
It never guesses a mathematical movement, changes the source, or adds an
operator to the existing mathematical observer.

An ambiguous utterance costs no mathematical transition observations. A
selection is explicitly recorded with the original utterance, both readings,
source-reported pinned version, and the existing bridge's mathematical witness.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import re

from ab_chatbot_language_bridge import GroundedTurn, LanguageBridge
from ab_chatbot_paraphrase_bridge import ParaphraseBridge, RecordedAnswer


@dataclass(frozen=True)
class ReadingOption:
    label: str
    described: str
    canonical: str
    semantic_key: tuple[str, ...]


@dataclass(frozen=True)
class PendingClarification:
    original: str
    options: tuple[ReadingOption, ReadingOption]
    question: str
    version: tuple[str, int, str, str]
    history_cursor: int


@dataclass(frozen=True)
class ClarificationTurn:
    user_text: str
    status: str
    message: str
    original_question: str | None
    offered: tuple[ReadingOption, ...]
    selected: ReadingOption | None
    answer: GroundedTurn | None
    version: tuple[str, int, str, str]


# Incomplete English disjunction is not silently treated as logical OR or a
# machine-level A/B operator. Both *single-choice* interpretations are offered.
# Even with simple A/B tokens, unknown referents require their own clarification.
_PATH_ALTERNATIVES = (
    re.compile(r'where do i end up after (.+?) or (.+?)\?', re.I),
    re.compile(r'what state do i reach after (.+?) or (.+?)\?', re.I),
)
_EQUAL_ALTERNATIVES = (
    re.compile(r'does (.+?) or (.+?) reach the same state as (.+?)\?', re.I),
    re.compile(r'does (.+?) or (.+?) end up in the same place as (.+?)\?', re.I),
)
_CHOICE = {
    'first': 0, 'the first': 0, 'option 1': 0, '1': 0,
    'second': 1, 'the second': 1, 'option 2': 1, '2': 1,
}
_WITHDRAW = {'neither', 'neither one', 'cancel', 'never mind'}


def _norm(s: str) -> str:
    return ' '.join(s.strip().lower().split())


def _options(text: str) -> tuple[ReadingOption, ReadingOption] | None:
    """Two precisely declared readings or NONE. Invalid words are not guessed."""
    if type(text) is not str:
        return None
    q = ' '.join(text.strip().split())
    for pattern in _PATH_ALTERNATIVES:
        m = pattern.fullmatch(q)
        if m:
            a, b = (LanguageBridge._parse_word(x) for x in m.groups())
            if not a or not b or a == b:
                return None
            return tuple(ReadingOption(str(i+1), f'follow {w}',
                         f'Where do I end up after {w}?',
                         ('endpoint', 'origin=(0,0,0)', w))
                         for i, w in enumerate((a,b)))  # type: ignore[return-value]
    for pattern in _EQUAL_ALTERNATIVES:
        m = pattern.fullmatch(q)
        if m:
            a, b, fixed = (LanguageBridge._parse_word(x) for x in m.groups())
            if not a or not b or not fixed or a == b:
                return None
            return tuple(ReadingOption(str(i+1), f'compare {w} with {fixed}',
                         f'Does {w} reach the same state as {fixed}?',
                         ('equal_endpoints', 'origin=(0,0,0)', *sorted((w,fixed))))
                         for i,w in enumerate((a,b)))  # type: ignore[return-value]
    return None


class ClarificationBridge:
    """Language-only negotiation over one existing ParaphraseBridge.

    The selected reading is then submitted to the unmodified observer. A
    version change, interruption, or withdrawal prevents latent choices from
    being executed. All interaction evidence is retained in this history.
    """
    def __init__(self, paraphrases: ParaphraseBridge):
        self.paraphrases = paraphrases
        self.pending: PendingClarification | None = None
        self.history: list[ClarificationTurn] = []

    def _version(self) -> tuple[str, int, str, str]:
        b = self.paraphrases.bridge
        s = b.snapshot
        return (s.claimed_source, s.revision, s.digest, b.origin_scope)

    def _unknown(self, text: str, status: str, msg: str, *, original: str | None = None,
                 offered: tuple[ReadingOption, ...] = ()) -> ClarificationTurn:
        # Invoke the existing unadmitted-language path so implicit endpoint
        # follow-up context is invalidated by the same normal rule, and keep
        # history in both layers. This route makes no /step requests.
        answer = self.paraphrases.ask(text)
        if answer.status != 'UNKNOWN_LANGUAGE':
            # The helper is only used for replies outside the base grammar.
            raise AssertionError('unexpected admitted mathematical request')
        answer = replace(answer, status=status, message=msg)
        self.paraphrases.bridge.history[-1] = answer
        old = self.paraphrases.history[-1]
        self.paraphrases.history[-1] = RecordedAnswer(old.reading, answer)
        result = ClarificationTurn(text, status, msg, original, offered, None, answer,
                                   self._version())
        self.history.append(result)
        return result

    def ask(self, text: str, *, max_class_probes: int = 3) -> ClarificationTurn:
        if type(text) is not str:
            text = str(text)
        readings = _options(text)
        if readings is not None:
            self.pending = PendingClarification(
                text, readings,
                f'Do you mean {readings[0].described} (1), or {readings[1].described} (2)?',
                self._version(), len(self.paraphrases.bridge.history))
            p = self.pending
            result = self._unknown(text, 'NEEDS_CLARIFICATION', p.question,
                                   original=text, offered=p.options)
            self.pending = replace(p, history_cursor=len(self.paraphrases.bridge.history))
            return result

        p = self.pending
        if p is not None:
            reply = _norm(text)
            # An independently asked complete question or repin replaces the
            # pending question, rather than secretly answering it.
            if reply in _WITHDRAW:
                self.pending = None
                return self._unknown(text, 'CLARIFICATION_WITHDRAWN',
                                     'The ambiguous question was not answered or executed.',
                                     original=p.original, offered=p.options)

            choice = _CHOICE.get(reply)
            if reply in ('a','b'):
                matches = [i for i, o in enumerate(p.options)
                           if o.described == f'follow {reply.upper()}']
                choice = matches[0] if len(matches) == 1 else None

            if choice is not None:
                self.pending = None
                if self._version() != p.version:
                    return self._unknown(text, 'UNKNOWN_VERSION',
                                         'The pinned source/version changed while awaiting clarification. '
                                         'Restate the original question on the new version.',
                                         original=p.original, offered=p.options)
                if len(self.paraphrases.bridge.history) != p.history_cursor:
                    return self._unknown(text, 'UNKNOWN_CONTEXT',
                                         'An intervening turn changed the conversation before your selection. '
                                         'Please restate the question.',
                                         original=p.original, offered=p.options)
                selected = p.options[choice]
                # Only the selected existing formal reading reaches the
                # mathematical bridge; never fetch edges for the other option.
                answer = self.paraphrases.ask(selected.canonical,
                                              max_class_probes=max_class_probes)
                message = (f'You selected {selected.described} from the original question. '
                           + answer.message)
                result = ClarificationTurn(text, answer.status, message, p.original,
                                           p.options, selected, answer, p.version)
                self.history.append(result)
                return result

            # Complete new questions supersede a pending clarification, even
            # if the new question is unsupported. Do not hold latent choices.
            if text.strip().endswith('?'):
                self.pending = None
                answer = self.paraphrases.ask(text, max_class_probes=max_class_probes)
                result = ClarificationTurn(text, answer.status, answer.message,
                                           None, (), None, answer, self._version())
                self.history.append(result)
                return result

            # An unclear short reply keeps BOTH candidate readings pending.
            from ab_chatbot_paraphrase_bridge import decode
            if decode(text).status in ('ADMITTED', 'PASS_THROUGH'):
                self.pending = None
                answer = self.paraphrases.ask(text, max_class_probes=max_class_probes)
                result = ClarificationTurn(text, answer.status, answer.message,
                                           None, (), None, answer, self._version())
                self.history.append(result)
                return result

            msg = p.question + ' Please answer 1 or 2, or say neither.'
            result = self._unknown(text, 'UNKNOWN_CLARIFICATION', msg,
                                   original=p.original, offered=p.options)
            self.pending = replace(p, history_cursor=len(self.paraphrases.bridge.history))
            return result

        answer = self.paraphrases.ask(text, max_class_probes=max_class_probes)
        result = ClarificationTurn(text, answer.status, answer.message,
                                   None, (), None, answer, self._version())
        self.history.append(result)
        return result


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_language_bridge import LanguageBridge
    from ab_chatbot_stability_witness import TransportedLaw

    shear = tuple((i, j, (k + i*j) % 3) for i,j,k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw((0, 1, 2), shear))
    with LoopbackHTTP(owner) as service:
        bot = ClarificationBridge(ParaphraseBridge(LanguageBridge(
            RemoteObserver(service.url), owner=owner)))
        for q in ('Where do I end up after A or B?', 'second',
                  'Does A or B reach the same state as BA?', '1',
                  'What if I take the other side?'):
            r = bot.ask(q)
            print(f'{q}\n  {r.status}: {r.message}')
        print('Observed edges:', len(bot.paraphrases.bridge.snapshot.edges))


if __name__ == '__main__':
    main()
