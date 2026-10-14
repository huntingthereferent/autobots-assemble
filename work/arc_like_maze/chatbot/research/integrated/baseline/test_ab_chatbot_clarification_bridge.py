"""Local A/B clarification tests: preserve alternatives, version and evidence."""
import unittest

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_paraphrase_bridge import ParaphraseBridge
from ab_chatbot_clarification_bridge import ClarificationBridge
from ab_chatbot_stability_witness import TransportedLaw


def law(phi=(0,1,2)):
    h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
    return TransportedLaw(phi,h)


class ClarificationTests(unittest.TestCase):
    def setUp(self):
        self.owner = SourceOwnedHTTP(law())
        self.http = LoopbackHTTP(self.owner)
        self.http.__enter__()
        self.addCleanup(self.http.__exit__, None, None, None)
        self.remote = RemoteObserver(self.http.url)
        self.base = LanguageBridge(self.remote, owner=self.owner)
        self.p = ParaphraseBridge(self.base)
        self.bot = ClarificationBridge(self.p)

    def test_ambiguous_question_retains_both_and_asks_one_question(self):
        q = 'Where do I end up after A or B?'
        r = self.bot.ask(q)
        self.assertEqual(r.status, 'NEEDS_CLARIFICATION')
        self.assertEqual(r.original_question, q)
        self.assertEqual(tuple(o.canonical for o in r.offered),
                         ('Where do I end up after A?', 'Where do I end up after B?'))
        self.assertIn('follow A',r.message)
        self.assertIn('follow B',r.message)
        self.assertEqual(self.remote.calls,1)  # /head only, no steps
        self.assertEqual(len(self.base.snapshot.edges),0)
        self.assertEqual(self.base.history[-1].status,'NEEDS_CLARIFICATION')

    def test_first_selection_executes_only_first_option(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('first')
        self.assertEqual(r.status,'WITNESSED_ENDPOINT')
        self.assertEqual(r.original_question,'Where do I end up after A or B?')
        self.assertEqual(r.user_text,'first')
        self.assertEqual(r.selected.canonical,'Where do I end up after A?')
        self.assertEqual(r.answer.paths[0].word,'A')
        self.assertEqual(len(self.base.snapshot.edges),1)
        self.assertEqual(self.remote.calls,2)
        self.assertIsNone(self.bot.pending)

    def test_second_selection_preserves_original_query_and_input(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('option 2')
        self.assertEqual(r.status,'WITNESSED_ENDPOINT')
        self.assertEqual(r.answer.paths[0].word,'B')
        self.assertEqual(r.offered, self.bot.history[0].offered)
        self.assertEqual(r.selected.semantic_key,('endpoint','origin=(0,0,0)','B'))
        self.assertIn('follow B',r.message)
        self.assertEqual(r.version,self.bot.history[0].version)

    def test_a_and_b_short_selection_only_for_literal_a_b_options(self):
        self.bot.ask('Where do I end up after A or B?')
        self.assertEqual(self.bot.ask('B').answer.paths[0].word,'B')
        self.bot.ask('Where do I end up after AB or BA?')
        r = self.bot.ask('B')
        self.assertEqual(r.status,'UNKNOWN_CLARIFICATION')
        self.assertIsNotNone(self.bot.pending)

    def test_equality_question_preserves_both_comparisons(self):
        r = self.bot.ask('Does A or B reach the same state as BA?')
        self.assertEqual(r.status,'NEEDS_CLARIFICATION')
        self.assertEqual(tuple(o.canonical for o in r.offered),
                         ('Does A reach the same state as BA?',
                          'Does B reach the same state as BA?'))
        self.assertEqual(self.remote.calls,1)
        r = self.bot.ask('2')
        self.assertEqual(r.status,'WITNESSED_EQUALITY')
        self.assertEqual(tuple(p.word for p in r.answer.paths),('B','BA'))
        self.assertEqual(r.original_question,'Does A or B reach the same state as BA?')
        self.assertEqual(r.selected.described,'compare B with BA')

    def test_preserve_selected_source_order_and_original_words(self):
        q = 'Does AB or BA reach the same state as A?'
        self.bot.ask(q)
        r = self.bot.ask('second')
        self.assertEqual(r.status,'WITNESSED_EQUALITY')
        self.assertEqual(tuple(p.word for p in r.answer.paths),('BA','A'))
        self.assertEqual(r.original_question,q)
        self.assertEqual(r.selected.semantic_key,('equal_endpoints','origin=(0,0,0)','A','BA'))

    def test_invalid_answer_does_not_resolve_or_observe(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('both')
        self.assertEqual(r.status,'UNKNOWN_CLARIFICATION')
        self.assertEqual(len(r.offered),2)
        self.assertEqual(self.remote.calls,1)
        self.assertIsNotNone(self.bot.pending)
        r = self.bot.ask('2')
        self.assertEqual(r.status,'WITNESSED_ENDPOINT')

    def test_neither_cancels_without_mathematical_action(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('neither')
        self.assertEqual(r.status,'CLARIFICATION_WITHDRAWN')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(self.remote.calls,1)
        self.assertEqual(len(self.base.snapshot.edges),0)
        self.assertEqual(self.bot.ask('1').status,'UNKNOWN_LANGUAGE')

    def test_ambiguous_question_invalidates_previous_endpoint_followup(self):
        self.assertEqual(self.bot.ask('Where do I end up after A?').status,'WITNESSED_ENDPOINT')
        self.bot.ask('Where do I end up after A or B?')
        self.bot.ask('neither')
        self.assertEqual(self.bot.ask('And then B?').status,'UNKNOWN_CONTEXT')

    def test_new_admitted_question_interrupts_pending(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('What does A/B mean?')
        self.assertEqual(r.status,'GROUNDING')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(self.bot.ask('1').status,'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_new_unsupported_question_interrupts_pending(self):
        self.bot.ask('Where do I end up after A or B?')
        r = self.bot.ask('What if I take the other side?')
        self.assertEqual(r.status,'UNKNOWN_LANGUAGE')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(self.bot.ask('1').status,'UNKNOWN_LANGUAGE')

    def test_new_ambiguous_question_replaces_prior_options(self):
        self.bot.ask('Where do I end up after A or B?')
        self.bot.ask('What state do I reach after AB or BA?')
        r = self.bot.ask('first')
        self.assertEqual(r.answer.paths[0].word,'AB')
        self.assertEqual(r.original_question,'What state do I reach after AB or BA?')

    def test_repin_interrupts_pending_without_stale_selection(self):
        self.bot.ask('Where do I end up after A or B?')
        self.owner.replace(law((0,2,0)))
        r = self.bot.ask('Pin current version')
        self.assertEqual(r.status,'PINNED_VERSION')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(self.bot.ask('first').status,'UNKNOWN_LANGUAGE')
        self.assertEqual(self.base.snapshot.revision,1)

    def test_out_of_band_version_change_detected_at_selection(self):
        self.bot.ask('Where do I end up after A or B?')
        self.owner.replace(law((0,2,0)))
        self.base.ask('Pin current version')  # outside wrapper: re-pin another way
        r = self.bot.ask('first')
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertEqual(r.original_question,'Where do I end up after A or B?')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(len(self.base.snapshot.edges),0)

    def test_out_of_band_intervening_turn_invalidates_reply_even_same_version(self):
        self.bot.ask('Where do I end up after A or B?')
        self.base.ask('Where do I end up after AB?')
        r = self.bot.ask('first')
        self.assertEqual(r.status,'UNKNOWN_CONTEXT')
        self.assertIsNone(self.bot.pending)
        self.assertEqual(r.original_question,'Where do I end up after A or B?')
        self.assertEqual(r.selected,None)

    def test_mutable_live_version_does_not_change_historical_pin(self):
        self.bot.ask('Where do I end up after A or B?')
        self.owner.replace(law((0,2,0)))
        r = self.bot.ask('first')
        self.assertEqual(r.status,'WITNESSED_ENDPOINT')
        self.assertEqual(r.version[1],0)
        self.assertEqual(r.answer.revision,0)
        self.assertEqual(self.base.snapshot.revision,0)

    def test_edge_budget_holds_after_clarification(self):
        restricted = ClarificationBridge(ParaphraseBridge(LanguageBridge(
            RemoteObserver(self.http.url),owner=self.owner,edge_budget=0)))
        q=restricted.ask('Where do I end up after A or B?')
        self.assertEqual(q.status,'NEEDS_CLARIFICATION')
        r=restricted.ask('1')
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(restricted.paraphrases.bridge.snapshot.edges),0)
        self.assertEqual(r.original_question,q.user_text)

    def test_unsupported_words_do_not_form_options(self):
        for q in ('Where do I end up after A or C?',
                  'Where do I end up after A or A?',
                  'Where do I end up after A/B or BA?',
                  'Does A or C reach the same state as BA?',
                  'Where do I end up after A or B from (1,0,0)?'):
            self.assertEqual(self.bot.ask(q).status,'UNKNOWN_LANGUAGE')
            self.assertIsNone(self.bot.pending)
        self.assertEqual(self.remote.calls,1)

    def test_unrelated_ambiguous_meaning_is_not_invented(self):
        self.assertEqual(self.bot.ask('What if I take the other side?').status,
                         'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_option_is_not_proof_of_family_admission_or_source_auth(self):
        external=ClarificationBridge(ParaphraseBridge(LanguageBridge(
            RemoteObserver(self.http.url),owner=None)))
        external.ask('Where do I end up after A or B?')
        r=external.ask('1')
        self.assertEqual(r.answer.origin_scope,'REMOTE_ORIGIN_UNVERIFIED')
        self.assertIsNone(r.answer.class_candidates or None)
        self.assertEqual(r.status,'WITNESSED_ENDPOINT')

    def test_duplicate_phrasing_preserves_semantic_key_after_choice(self):
        self.bot.ask('Where do I end up after A or B?')
        r=self.bot.ask('1')
        x=self.bot.ask('What state do I reach after A?')
        self.assertEqual(r.selected.semantic_key,self.p.history[-1].reading.semantic_key)
        self.assertEqual(r.answer.paths[0],x.answer.paths[0])


if __name__=='__main__':
    unittest.main()
