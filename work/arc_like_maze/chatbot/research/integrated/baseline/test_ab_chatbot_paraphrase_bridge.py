"""Bounded wording equivalence and contradiction tests, not general NLP."""
import unittest

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_paraphrase_bridge import ParaphraseBridge, decode
from ab_chatbot_stability_witness import TransportedLaw


class ParaphraseBridgeTests(unittest.TestCase):
    def setUp(self):
        h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner = SourceOwnedHTTP(TransportedLaw((0,1,2),h))
        self.server = LoopbackHTTP(self.owner)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__,None,None,None)
        self.remote = RemoteObserver(self.server.url)
        self.base = LanguageBridge(self.remote, owner=self.owner)
        self.bot = ParaphraseBridge(self.base)

    def test_distinct_equal_phrasings_preserve_mathematical_question_and_witness(self):
        questions = (
            'Does A then B reach the same state as B then A?',
            'Do AB and BA end at the same place?',
            'Are the endpoints of A then B and B then A equal?',
            'Do AB and BA lead to the same state?',
            'From the origin, do AB and BA finish at the same state?',
        )
        results = []
        for q in questions:
            results.append(self.bot.ask(q))
            self.assertEqual(self.bot.history[-1].reading.status, 'ADMITTED')
        self.assertTrue(all(x.status == 'WITNESSED_EQUALITY' for x in results))
        self.assertTrue(all(x.paths == results[0].paths for x in results))
        self.assertEqual(len({x.formal_question for x in results}), 1)
        self.assertEqual(len({x.revision for x in results}), 1)
        self.assertEqual(len({x.digest for x in results}), 1)
        self.assertEqual(len({r.reading.semantic_key for r in self.bot.history}), 1)
        self.assertEqual([t.user_text for t in results], list(questions))
        self.assertEqual([t.user_text for t in self.base.history], list(questions))
        self.assertEqual(self.remote.calls, 5)  # /head plus AB/BA edges, cached

    def test_reversed_comparison_is_symmetric_but_preserves_source_order(self):
        forward = self.bot.ask('Do AB and BA end in the same place?')
        backwards = self.bot.ask('Are the endpoints after BA and AB the same?')
        self.assertEqual(self.bot.history[0].reading.semantic_key,
                         self.bot.history[1].reading.semantic_key)
        self.assertEqual(forward.status, backwards.status)
        self.assertEqual(forward.paths, tuple(reversed(backwards.paths)))
        self.assertNotEqual(forward.formal_question, backwards.formal_question)
        self.assertEqual(self.remote.calls, 5)

    def test_endpoint_paraphrases_are_one_question(self):
        a = self.bot.ask('Where do I end up after A then B?')
        b = self.bot.ask('What state do I reach after AB?')
        c = self.bot.ask('After A then B, what state do I reach?')
        d = self.bot.ask('From the origin, where does AB end?')
        self.assertTrue(all(t.status == 'WITNESSED_ENDPOINT' for t in (a,b,c,d)))
        self.assertEqual({t.paths[0] for t in (a,b,c,d)}, {a.paths[0]})
        self.assertEqual(len({t.formal_question for t in (a,b,c,d)}), 1)
        self.assertEqual(len({r.reading.semantic_key for r in self.bot.history}), 1)
        self.assertEqual(self.remote.calls, 3)

    def test_explicit_next_continues_path_and_replay_uses_cache(self):
        start = self.bot.ask('What state do I reach after AB?')
        next_turn = self.bot.ask('Continue with B.')
        self.assertEqual(next_turn.status, 'WITNESSED_ENDPOINT')
        self.assertEqual(next_turn.paths[0].word, 'ABB')
        self.assertEqual(next_turn.paths[0].states[:3], start.paths[0].states)
        count = self.remote.calls
        replay = self.bot.ask('Replay the path.')
        self.assertEqual(replay.status, 'WITNESS_REPLAY')
        self.assertEqual(replay.paths[0], next_turn.paths[0])
        self.assertEqual(self.remote.calls, count)

    def test_no_followup_path_is_unknown_context(self):
        t = self.bot.ask('Continue with B.')
        self.assertEqual(t.status, 'UNKNOWN_CONTEXT')
        self.assertEqual(self.remote.calls, 1)
        self.assertEqual(t.user_text, 'Continue with B.')

    def test_comparison_invalidates_prior_active_endpoint(self):
        self.bot.ask('What state do I reach after A?')
        self.bot.ask('Do AB and BA lead to the same state?')
        t = self.bot.ask('Continue with B.')
        self.assertEqual(t.status, 'UNKNOWN_CONTEXT')

    def test_reject_negation_not_equivalent_to_equality(self):
        q = 'Do AB and BA end at different states?'
        self.assertEqual(decode(q).status,'UNRESOLVED')
        t = self.bot.ask(q)
        self.assertEqual(t.status,'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_reject_changed_origin_no_scope_promotion(self):
        for q in ('From (1,0,0), do AB and BA end at the same place?',
                  'Do AB and BA end at the same place from state (1,0,0)?'):
            self.assertEqual(self.bot.ask(q).status,'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_reject_temporal_qualifier_not_same_question(self):
        self.assertEqual(self.bot.ask('Do AB and BA still end at the same place?').status,
                         'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_reject_ambiguity_and_unadmitted_actions(self):
        for q in ('Does A or B reach the same state as BA?',
                  'Do A then C and BA end at the same place?',
                  'Do A/B and BA end at the same place?',
                  'What if I take the other side?'):
            self.assertEqual(self.bot.ask(q).status, 'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls, 1)

    def test_spaces_and_case_have_no_semantic_effect(self):
        first = self.bot.ask('Do A then B and B then A end at the same state?')
        second = self.bot.ask('  dO   A   THEN   B  and  B  then  A  end at the same state?  ')
        self.assertEqual(first.paths,second.paths)
        self.assertEqual(self.bot.history[0].reading.semantic_key,
                         self.bot.history[1].reading.semantic_key)
        self.assertEqual(second.user_text, '  dO   A   THEN   B  and  B  then  A  end at the same state?  ')

    def test_edge_budget_cannot_be_bypassed_with_paraphrasing(self):
        restricted = ParaphraseBridge(LanguageBridge(RemoteObserver(self.server.url),
                                          owner=self.owner, edge_budget=2))
        first = restricted.ask('What state do I reach after AB?')
        self.assertEqual(first.status, 'WITNESSED_ENDPOINT')
        second = restricted.ask('After AB, what state do I reach?')
        self.assertEqual(second.status, 'WITNESSED_ENDPOINT')
        third = restricted.ask('Do AB and BA end at the same place?')
        self.assertEqual(third.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(restricted.bridge.snapshot.edges),2)

    def test_unknown_breaks_implicit_followup(self):
        self.bot.ask('What state do I reach after A?')
        self.bot.ask('What does the other side mean?')
        self.assertEqual(self.bot.ask('Continue with B.').status, 'UNKNOWN_CONTEXT')

    def test_repin_resets_path_and_keeps_original_language_history(self):
        first = self.bot.ask('What state do I reach after AB?')
        self.owner.replace(TransportedLaw((0,2,0),
            tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)))
        pinned = self.bot.ask('Pin current version')
        self.assertEqual(pinned.status,'PINNED_VERSION')
        self.assertEqual(pinned.revision,1)
        self.assertEqual(self.bot.ask('Continue with A.').status,'UNKNOWN_CONTEXT')
        self.assertEqual(first.revision,0)
        self.assertEqual(self.bot.history[0].reading.original, first.user_text)

    def test_class_and_ground_survive_passthrough(self):
        self.assertEqual(self.bot.ask('What does A/B mean?').status,'GROUNDING')
        cls = self.bot.ask('Which relationship class fits?')
        self.assertEqual(cls.status,'CONDITIONAL_CLASS')
        self.assertIn('does NOT establish',cls.message)
        self.assertEqual(self.bot.history[-1].reading.status,'PASS_THROUGH')

    def test_comparison_no_implicit_family_admission(self):
        self.owner.replace(TransportedLaw((1,0,0),
            tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)))
        self.bot.ask('Pin current version')
        a = self.bot.ask('Do AB and BA end at the same state?')
        self.assertEqual(a.status,'WITNESSED_EQUALITY')
        self.assertIsNone(a.class_candidates or None)
        self.assertNotIn('universal', a.message.lower())

    def test_max_length_inherited_in_synonyms(self):
        self.assertEqual(self.bot.ask('What state do I reach after '+ 'A'*25 + '?').status,
                         'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)

    def test_reading_is_language_provenance_not_mathematical_certificate(self):
        r = decode('Are the endpoints of AB and BA equal?')
        self.assertEqual(r.status,'ADMITTED')
        self.assertEqual(r.semantic_key, ('equal_endpoints', 'origin=(0,0,0)', 'AB', 'BA'))
        self.assertEqual(r.canonical,'Does AB reach the same state as BA?')
        self.assertIn('endpoints',r.basis)
        self.assertEqual(self.remote.calls,1)

    def test_unknown_does_not_hallucinate_observation(self):
        self.assertEqual(self.bot.ask('Compare the movement between us.').status,
                         'UNKNOWN_LANGUAGE')
        self.assertEqual(self.remote.calls,1)
        self.assertEqual(len(self.base.snapshot.edges),0)


if __name__=='__main__':
    unittest.main()
