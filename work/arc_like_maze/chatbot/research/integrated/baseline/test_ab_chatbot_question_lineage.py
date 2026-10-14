"""Same mathematical answer must never erase a different question referent."""
import unittest

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_paraphrase_bridge import ParaphraseBridge
from ab_chatbot_clarification_bridge import ClarificationBridge
from ab_chatbot_question_lineage import QuestionLineageBridge
from ab_chatbot_stability_witness import TransportedLaw


def law(phi=(0, 1, 2)):
    h = tuple((i, j, (k + i * j) % 3) for i, j, k in DOMAIN)
    return TransportedLaw(phi, h)


class QuestionLineageTests(unittest.TestCase):
    def setUp(self):
        self.owner = SourceOwnedHTTP(law())
        self.http = LoopbackHTTP(self.owner)
        self.http.__enter__()
        self.addCleanup(self.http.__exit__, None, None, None)
        self.remote = RemoteObserver(self.http.url)
        self.base = LanguageBridge(self.remote, owner=self.owner)
        self.clarification = ClarificationBridge(ParaphraseBridge(self.base))
        self.bot = QuestionLineageBridge(self.clarification)

    def test_same_endpoint_different_question_distinct_identity(self):
        a = self.bot.ask('Where do I end up after A?')
        b = self.bot.ask('Where do I end up after AAAA?')
        self.assertEqual(a.endpoint, b.endpoint)
        self.assertEqual(a.endpoint, (1, 0, 0))
        self.assertNotEqual(a.semantic_key, b.semantic_key)
        self.assertEqual(tuple(p.word for p in a.paths), ('A',))
        self.assertEqual(tuple(p.word for p in b.paths), ('AAAA',))
        self.assertNotEqual(a.paths, b.paths)
        self.assertEqual((a.number, b.number), (1, 2))
        self.assertEqual((a.utterance, b.utterance),
                         ('Where do I end up after A?', 'Where do I end up after AAAA?'))

    def test_explicit_reentry_selects_earlier_question_not_latest_endpoint(self):
        a = self.bot.ask('Where do I end up after A?')
        self.bot.ask('Where do I end up after AAAA?')
        r = self.bot.ask('Continue question 1 with B.')
        self.assertEqual(r.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(r.paths[0].word, 'AB')
        self.assertNotEqual(r.paths[0].word, 'AAAAB')
        self.assertEqual(r.parent_question, a.number)
        self.assertEqual(r.original_question, a.utterance)
        self.assertEqual(r.asked_as, 'Where do I end up after AB?')
        self.assertEqual(r.semantic_key, ('continuation', 'parent_question=1', 'AB'))

    def test_implicit_followup_uses_last_active_question_not_equal_endpoint(self):
        self.bot.ask('Where do I end up after A?')
        self.bot.ask('Where do I end up after AAAA?')
        r = self.bot.ask('And then B?')
        self.assertEqual(r.paths[0].word, 'AAAAB')
        self.assertEqual(r.parent_question, 2)
        self.assertEqual(r.semantic_key, ('continuation', 'parent_question=2', 'AAAAB'))

    def test_same_false_answer_does_not_merge_different_comparisons(self):
        a = self.bot.ask('Does AB reach the same state as BA?')
        b = self.bot.ask('Does A reach the same state as B?')
        self.assertEqual(a.status, 'WITNESSED_EQUALITY')
        self.assertEqual(a.equality, b.equality)
        self.assertFalse(a.equality)
        self.assertNotEqual(a.semantic_key, b.semantic_key)
        self.assertNotEqual(tuple(p.word for p in a.paths),
                            tuple(p.word for p in b.paths))
        self.assertIsNone(a.endpoint)

    def test_paraphrases_share_semantic_question_not_turn_identity(self):
        a = self.bot.ask('Do AB and BA end in the same place?')
        edges = len(self.base.snapshot.edges)
        b = self.bot.ask('Are the endpoints of BA and AB equal?')
        self.assertEqual(a.semantic_key, b.semantic_key)
        self.assertNotEqual(a.number, b.number)
        self.assertNotEqual(a.utterance, b.utterance)
        self.assertEqual(len(self.base.snapshot.edges), edges)
        self.assertEqual(tuple(p.word for p in b.paths), ('BA', 'AB'))

    def test_historical_replay_no_new_http_observations(self):
        first = self.bot.ask('Where do I end up after A?')
        self.bot.ask('Where do I end up after AAAA?')
        before = self.remote.calls
        shown = self.bot.ask('Show witness for question 1.')
        self.assertEqual(shown.status, 'HISTORICAL_WITNESS')
        self.assertEqual(shown.parent_question, 1)
        self.assertEqual(shown.version, first.version)
        self.assertEqual(shown.paths, first.paths)
        self.assertIn('not a fresh observation', shown.message)
        self.assertEqual(self.remote.calls, before)

    def test_old_witness_replay_after_repin_is_historical(self):
        first = self.bot.ask('Where do I end up after A?')
        self.owner.replace(law((0, 2, 0)))
        new = self.bot.ask('Pin current version')
        self.assertEqual(new.status, 'PINNED_VERSION')
        before = self.remote.calls
        old = self.bot.ask('Show witness for question 1.')
        self.assertEqual(old.status, 'HISTORICAL_WITNESS')
        self.assertEqual(old.version, first.version)
        self.assertNotEqual(old.version, new.version)
        self.assertEqual(self.remote.calls, before)
        self.assertIsNone(old.endpoint)

    def test_old_continuation_after_repin_is_unknown_without_reads(self):
        self.bot.ask('Where do I end up after A?')
        self.owner.replace(law((0, 2, 0)))
        self.bot.ask('Pin current version')
        before = self.remote.calls
        reject = self.bot.ask('Continue question 1 with B.')
        self.assertEqual(reject.status, 'UNKNOWN_VERSION')
        self.assertEqual(reject.parent_question, 1)
        self.assertEqual(self.remote.calls, before)
        self.assertIsNone(reject.answer)

    def test_live_change_without_repin_keeps_historical_version(self):
        old = self.bot.ask('Where do I end up after A?')
        self.owner.replace(law((0, 2, 0)))
        follow = self.bot.ask('Continue question 1 with B.')
        self.assertEqual(follow.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(follow.version, old.version)
        self.assertEqual(follow.paths[0].word, 'AB')
        self.assertIn('Explicit continuation', follow.message)

    def test_unknown_number_does_not_query_or_invent_path(self):
        self.bot.ask('Where do I end up after A?')
        before = self.remote.calls
        t = self.bot.ask('Continue question 99 with B.')
        self.assertEqual(t.status, 'UNKNOWN_REFERENT')
        self.assertIsNone(t.semantic_key)
        self.assertEqual(self.remote.calls, before)
        self.assertEqual(self.bot.ask('And then B?').status, 'UNKNOWN_CONTEXT')

    def test_comparison_cannot_be_continued_as_one_path(self):
        self.bot.ask('Does AB reach the same state as BA?')
        before = self.remote.calls
        r = self.bot.ask('Continue question 1 with A.')
        self.assertEqual(r.status, 'UNKNOWN_REFERENT')
        self.assertEqual(self.remote.calls, before)

    def test_unknown_language_cannot_gain_witness_by_number(self):
        self.bot.ask('What if I take the other side?')
        before = self.remote.calls
        self.assertEqual(self.bot.ask('Show witness for question 1.').status,
                         'UNKNOWN_REFERENT')
        self.assertEqual(self.remote.calls, before)

    def test_clarification_selection_retains_original_ancestry(self):
        original = self.bot.ask('Where do I end up after A or B?')
        self.assertEqual(original.status, 'NEEDS_CLARIFICATION')
        before = self.remote.calls
        selected = self.bot.ask('second')
        self.assertEqual(selected.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(selected.parent_question, original.number)
        self.assertEqual(selected.original_question, original.utterance)
        self.assertEqual(selected.paths[0].word, 'B')
        self.assertEqual(selected.semantic_key, ('endpoint', 'origin=(0,0,0)', 'B'))
        self.assertGreater(self.remote.calls, before)

    def test_unresolved_clarification_cannot_be_continued(self):
        self.bot.ask('Where do I end up after A or B?')
        before = self.remote.calls
        r = self.bot.ask('Continue question 1 with B.')
        self.assertEqual(r.status, 'UNKNOWN_CONTEXT')
        self.assertEqual(self.remote.calls, before)
        # The original ambiguous choice is still pending, and can be resolved.
        selected = self.bot.ask('1')
        self.assertEqual(selected.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(selected.paths[0].word, 'A')

    def test_unknown_clarification_preserves_parent_and_zero_observation(self):
        p = self.bot.ask('Where do I end up after A or B?')
        before = self.remote.calls
        unclear = self.bot.ask('both')
        self.assertEqual(unclear.status, 'UNKNOWN_CLARIFICATION')
        self.assertEqual(unclear.parent_question, p.number)
        self.assertEqual(self.remote.calls, before)

    def test_explicit_reentry_respects_24_action_bound(self):
        self.bot.ask('Where do I end up after ' + 'A' * 24 + '?')
        before = self.remote.calls
        r = self.bot.ask('Continue question 1 with B.')
        self.assertEqual(r.status, 'WALL_LIMIT')
        self.assertEqual(self.remote.calls, before)

    def test_budget_failure_never_claims_new_endpoint(self):
        # A first observed endpoint is valid even when there is no remaining
        # budget for its next transition.
        with_budget = QuestionLineageBridge(ClarificationBridge(ParaphraseBridge(
            LanguageBridge(self.remote, owner=self.owner, edge_budget=1))))
        self.assertEqual(with_budget.ask('Where do I end up after A?').status,
                         'WITNESSED_ENDPOINT')
        r = with_budget.ask('Continue question 1 with B.')
        self.assertEqual(r.status, 'UNKNOWN_BUDGET')
        self.assertIsNone(r.endpoint)
        self.assertEqual(r.parent_question, 1)
        self.assertEqual(with_budget.history[0].endpoint, (1, 0, 0))

    def test_equal_law_at_two_revisions_is_not_temporal_identity(self):
        first = self.bot.ask('Where do I end up after A?')
        self.owner.replace(law())  # A -> A, identical table at a new revision
        self.bot.ask('Pin current version')
        again = self.bot.ask('Where do I end up after A?')
        self.assertEqual(first.endpoint, again.endpoint)
        self.assertEqual(first.semantic_key, again.semantic_key)
        self.assertEqual(first.version[2], again.version[2])  # same table digest
        self.assertNotEqual(first.version[1], again.version[1])
        self.assertNotEqual(first.number, again.number)
        self.assertNotIn('unchanged between', again.message.lower())

    def test_same_true_answer_does_not_merge_distinct_questions(self):
        a = self.bot.ask('Does A reach the same state as A?')
        b = self.bot.ask('Does AAAA reach the same state as A?')
        self.assertTrue(a.equality)
        self.assertTrue(b.equality)
        self.assertNotEqual(a.semantic_key, b.semantic_key)
        self.assertNotEqual(a.paths, b.paths)

    def test_historical_witness_does_not_become_implicit_followup(self):
        self.bot.ask('Where do I end up after A?')
        self.bot.ask('Where do I end up after AAAA?')
        self.assertEqual(self.bot.ask('Show witness for question 1.').status,
                         'HISTORICAL_WITNESS')
        self.assertEqual(self.bot.ask('And then B?').status, 'UNKNOWN_CONTEXT')
        # Explicitly naming the earlier question still admits valid re-entry.
        self.assertEqual(self.bot.ask('Continue question 1 with B.').paths[0].word, 'AB')

    def test_pending_clarification_prevents_historical_replay(self):
        self.bot.ask('Where do I end up after A?')
        self.bot.ask('Where do I end up after A or B?')
        before = self.remote.calls
        reject = self.bot.ask('Show witness for question 1.')
        self.assertEqual(reject.status, 'UNKNOWN_CONTEXT')
        self.assertEqual(self.remote.calls, before)
        self.assertEqual(self.bot.ask('first').status, 'WITNESSED_ENDPOINT')

    def test_clarified_question_can_be_explicitly_continued(self):
        original = self.bot.ask('Where do I end up after A or B?')
        chosen = self.bot.ask('second')
        r = self.bot.ask(f'Continue question {chosen.number} with B.')
        self.assertEqual(r.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(r.paths[0].word, 'BB')
        self.assertEqual(r.parent_question, chosen.number)
        self.assertEqual(r.original_question, original.utterance)

    def test_replay_of_comparison_retains_both_paths(self):
        first = self.bot.ask('Does AB reach the same state as BA?')
        old_calls = self.remote.calls
        r = self.bot.ask('Replay witness of question 1.')
        self.assertEqual(r.status, 'HISTORICAL_WITNESS')
        self.assertEqual(r.paths, first.paths)
        self.assertEqual(self.remote.calls, old_calls)

    def test_replay_no_witness_held_after_budget(self):
        tiny = QuestionLineageBridge(ClarificationBridge(ParaphraseBridge(
            LanguageBridge(self.remote, owner=self.owner, edge_budget=0))))
        r = tiny.ask('Where do I end up after A?')
        self.assertEqual(r.status, 'UNKNOWN_BUDGET')
        self.assertEqual(tiny.ask('Show witness for question 1.').status,
                         'UNKNOWN_REFERENT')

    def test_unverified_source_keeps_scope_unknown(self):
        remote_bot = QuestionLineageBridge(ClarificationBridge(ParaphraseBridge(
            LanguageBridge(self.remote))))
        r = remote_bot.ask('Where do I end up after A?')
        self.assertEqual(r.answer.origin_scope, 'REMOTE_ORIGIN_UNVERIFIED')
        continuation = remote_bot.ask('Continue question 1 with B.')
        self.assertEqual(continuation.answer.origin_scope, 'REMOTE_ORIGIN_UNVERIFIED')
        self.assertEqual(continuation.status, 'WITNESSED_ENDPOINT')


if __name__ == '__main__':
    unittest.main()
