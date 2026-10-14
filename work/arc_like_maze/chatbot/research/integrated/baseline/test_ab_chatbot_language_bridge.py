"""Tests of exact ordinary-language-to-witness routing, not generic NLP/A/B."""
import unittest
from itertools import product
from unittest.mock import patch

from ab_chatbot_relation_probe import FiniteSystem, compare_systems
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_http_snapshot import LoopbackHTTP, SourceOwnedHTTP, RemoteObserver
from ab_chatbot_language_bridge import LanguageBridge, PinnedEdges, NINE, ObservationWall


class LanguageBridgeTests(unittest.TestCase):
    def setUp(self):
        self.h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.law = (0,1,2)
        self.owner = SourceOwnedHTTP(TransportedLaw(self.law,self.h))
        self.server = LoopbackHTTP(self.owner)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__,None,None,None)
        self.client = RemoteObserver(self.server.url, bound_loopback=self.server)
        self.bot = LanguageBridge(self.client,owner=self.owner)

    def test_starts_by_pinning_header_only_not_full_54_table(self):
        self.assertEqual(self.client.calls,1)
        self.assertIsInstance(self.bot.snapshot,PinnedEdges)
        self.assertEqual(len(self.bot.snapshot.edges),0)
        self.assertEqual(self.bot.origin_scope,'LOCAL_OWNER_VERIFIED')

    def test_ground_language_is_not_mathematical_operation(self):
        a=self.bot.ask('What does A/B mean?')
        self.assertEqual(a.status,'GROUNDING')
        self.assertIn('language',a.message)
        self.assertIn('does not define',a.message)
        self.assertEqual(self.client.calls,1)
        self.assertEqual(a.referent,'A/B chatbot: continuing a witnessed relationship')

    def test_endpoint_and_followup_stay_same_referent(self):
        a=self.bot.ask('Where do I end up after A then B?')
        self.assertEqual(a.status,'WITNESSED_ENDPOINT')
        self.assertEqual(a.paths[0].word,'AB')
        self.assertEqual(a.paths[0].states[-1],self.owner.select(0).step(
            self.owner.select(0).step((0,0,0),'A'),'B'))
        b=self.bot.ask('And then B?')
        self.assertEqual(b.status,'WITNESSED_ENDPOINT')
        self.assertEqual(b.paths[0].word,'ABB')
        self.assertEqual(b.paths[0].states[:3],a.paths[0].states)
        self.assertEqual(b.revision,a.revision)
        self.assertEqual(b.digest,a.digest)

    def test_replay_witness_no_new_network_call(self):
        self.bot.ask('Where do I end up after A then B?')
        n=self.client.calls
        t=self.bot.ask('Show the witness')
        self.assertEqual(t.status,'WITNESS_REPLAY')
        self.assertEqual(self.client.calls,n)
        self.assertEqual(t.paths[0].states[0],(0,0,0))
        self.assertEqual(len(t.paths[0].states),3)

    def test_word_AB_compares_to_BA_from_same_origin(self):
        t=self.bot.ask('Does A then B reach the same state as B then A?')
        self.assertEqual(t.status,'WITNESSED_EQUALITY')
        self.assertNotEqual(t.paths[0].states[-1],t.paths[1].states[-1])
        self.assertEqual([x.word for x in t.paths],['AB','BA'])

    def test_identity_word_equality_true(self):
        t=self.bot.ask('Does AB reach the same state as A then B?')
        self.assertEqual(t.status,'WITNESSED_EQUALITY')
        self.assertEqual(t.paths[0].states[-1],t.paths[1].states[-1])
        self.assertIn('equal',t.message)

    def test_comparison_cannot_select_implicit_followup(self):
        self.bot.ask('Where do I end up after A?')
        self.bot.ask('Does A reach the same state as B?')
        t=self.bot.ask('And then B?')
        self.assertEqual(t.status,'UNKNOWN_CONTEXT')

    def test_missing_context_is_not_invented(self):
        self.assertEqual(self.bot.ask('And then B?').status,'UNKNOWN_CONTEXT')
        self.assertEqual(self.bot.ask('Show witness').status,'UNKNOWN_CONTEXT')

    def test_unsupported_language_is_unknown_and_keeps_words(self):
        q='What if I take the other side?'
        t=self.bot.ask(q)
        self.assertEqual(t.status,'UNKNOWN_LANGUAGE')
        self.assertEqual(t.user_text,q)
        self.assertEqual(len(self.bot.snapshot.edges),0)

    def test_unsupported_action_is_not_guessed(self):
        t=self.bot.ask('Where do I end up after A then C?')
        self.assertEqual(t.status,'UNKNOWN_LANGUAGE')
        self.assertEqual(len(self.bot.snapshot.edges),0)

    def test_oversized_word_is_rejected(self):
        t=self.bot.ask('Where do I end up after ' + ('A'*25) + '?')
        self.assertEqual(t.status,'UNKNOWN_LANGUAGE')
        self.assertEqual(len(self.bot.snapshot.edges),0)

    def test_universal_claim_is_walled_not_inferred(self):
        for q in ('Is this A/B?','Does this prove A/B?','Is A/B universal?'):
            self.assertEqual(self.bot.ask(q).status,'WALL_SCOPE')
        self.assertEqual(self.client.calls,1)

    def test_temporal_continuity_is_unknown(self):
        self.assertEqual(self.bot.ask('Has the system stayed the same?').status,
                         'UNKNOWN_TEMPORAL_CONTINUITY')
        self.assertEqual(self.bot.ask('Is the target unchanged?').status,
                         'UNKNOWN_TEMPORAL_CONTINUITY')

    def test_classification_reuses_native_math_chooser_not_target_parameters(self):
        t=self.bot.ask('Which A/B relationship class fits?')
        self.assertEqual(t.status,'CONDITIONAL_CLASS')
        self.assertIn(self.law,t.class_candidates)
        self.assertEqual(set(t.class_candidates), {(0,1,2),(0,2,1)})
        self.assertIn('does NOT establish',t.message)
        self.assertIn(len(t.class_probes),(2,3))
        for pair,answer in t.class_probes:
            self.assertEqual(answer,
                self.bot._follow(pair[0]).states[-1]==self.bot._follow(pair[1]).states[-1])

    def test_all_nine_family_members_get_correct_rooted_class(self):
        for phi in product(range(3),repeat=2):
            law=(0,*phi)
            self.owner.replace(TransportedLaw(law,self.h))
            self.bot.ask('Pin current version')
            t=self.bot.ask('Which relationship class fits?')
            self.assertEqual(t.status,'CONDITIONAL_CLASS')
            self.assertEqual(set(t.class_candidates),
                {x.phi for x in NINE if compare_systems(FiniteSystem(law),x) is None})

    def test_outsider_may_match_class_but_never_claim_admission(self):
        self.owner.replace(TransportedLaw((1,0,0),self.h))
        self.bot.ask('Pin current version')
        t=self.bot.ask('Which A/B relationship class fits?')
        self.assertEqual(t.status,'CONDITIONAL_CLASS')
        self.assertTrue(t.class_candidates)
        self.assertNotIn((1,0,0),t.class_candidates)
        self.assertIn('does NOT establish',t.message)

    def test_zero_and_one_budget_preserve_unknown(self):
        self.assertEqual(self.bot.ask('Which A/B relationship class fits?',max_class_probes=0).status,
                         'UNKNOWN_BUDGET')
        t=self.bot.ask('Which A/B relationship class fits?',max_class_probes=1)
        self.assertEqual(t.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(t.class_probes),1)
        self.assertEqual(t.class_candidates,())

    def test_snapshot_mode_is_explicit_but_reads_complete_54(self):
        observer=RemoteObserver(self.server.url, bound_loopback=self.server)
        bot=LanguageBridge(observer,owner=self.owner,mode='snapshot')
        self.assertEqual(observer.calls,1)
        self.assertEqual(len(bot.snapshot.values),54)
        t=bot.ask('Where do I end up after AB?')
        self.assertEqual(t.status,'WITNESSED_ENDPOINT')
        self.assertEqual(observer.calls,1)

    def test_incremental_http_observations_reuse_cache(self):
        self.bot.ask('Where do I end up after AB?')
        self.assertEqual(self.client.calls,3)  # one /head and two edges
        self.bot.ask('Where do I end up after AB?')
        self.assertEqual(self.client.calls,3)
        self.assertEqual(len(self.bot.snapshot.edges),2)

    def test_live_head_changes_do_not_move_pinned_referent(self):
        first=self.bot.ask('Where do I end up after AB?')
        self.owner.replace(TransportedLaw((0,2,2),self.h))
        last=self.bot.ask('Where do I end up after AB?')
        self.assertEqual(first.paths[0],last.paths[0])
        self.assertEqual(first.revision,last.revision)
        self.assertEqual(last.origin_scope,'LOCAL_OWNER_VERIFIED')

    def test_explicit_repin_changes_version_and_resets_trace(self):
        before=self.bot.ask('Where do I end up after ABB?')
        self.owner.replace(TransportedLaw((0,2,0),self.h))
        pinned=self.bot.ask('Pin current version')
        self.assertEqual(pinned.status,'PINNED_VERSION')
        self.assertEqual(pinned.revision,1)
        self.assertEqual(self.bot.ask('And then B?').status,'UNKNOWN_CONTEXT')
        self.assertEqual(self.bot.history[0],before)
        after=self.bot.ask('Where do I end up after ABB?')
        self.assertEqual(after.revision,1)
        self.assertNotEqual(after.paths[0].states[-1],before.paths[0].states[-1])

    def test_unverified_external_client_only_has_remote_claim(self):
        client=RemoteObserver(self.server.url)
        bot=LanguageBridge(client)
        t=bot.ask('Where do I end up after AB?')
        self.assertEqual(t.origin_scope,'REMOTE_ORIGIN_UNVERIFIED')

    def test_different_local_owner_cannot_authorize_http_source(self):
        alien=SourceOwnedHTTP(TransportedLaw(self.law,self.h))
        client=RemoteObserver(self.server.url)
        bot=LanguageBridge(client,owner=alien)
        self.assertEqual(bot.origin_scope,'REMOTE_ORIGIN_UNVERIFIED')

    def test_unbound_matching_metadata_never_attests_owner(self):
        # A label, digest and revision are copyable by an unrelated source.
        observer = RemoteObserver(self.server.url)
        bot = LanguageBridge(observer, owner=self.owner)
        self.assertEqual(bot.origin_scope, 'REMOTE_ORIGIN_UNVERIFIED')
        result = bot.ask('Where do I end up after A?')
        self.assertEqual(result.origin_scope, 'REMOTE_ORIGIN_UNVERIFIED')

    def test_bound_owner_rejects_matching_metadata_with_wrong_edge(self):
        original = self.client.request
        def altered(path):
            value = original(path)
            if path.startswith('/step/'):
                value = dict(value)
                value['output'] = [2, 2, 2]
            return value
        with patch.object(self.client, 'request', side_effect=altered):
            result = self.bot.ask('Where do I end up after A?')
        self.assertEqual(result.status, 'WALL_OBSERVATION')
        self.assertEqual(self.bot.snapshot.edges, {})

    def test_corrupt_source_digest_in_edge_is_a_wall(self):
        original=self.client.request
        def altered(path):
            raw=original(path)
            if path.startswith('/step/'):
                raw=dict(raw)
                raw['digest']='0'*64
            return raw
        with patch.object(self.client,'request',side_effect=altered):
            t=self.bot.ask('Where do I end up after A?')
        self.assertEqual(t.status,'WALL_OBSERVATION')
        self.assertEqual(self.bot.snapshot.edges,{})

    def test_corrupt_source_identity_in_edge_is_a_wall(self):
        original=self.client.request
        def altered(path):
            raw=original(path)
            if path.startswith('/step/'):
                raw=dict(raw)
                raw['source']='alien'
            return raw
        with patch.object(self.client,'request',side_effect=altered):
            t=self.bot.ask('Where do I end up after A?')
        self.assertEqual(t.status,'WALL_OBSERVATION')

    def test_invalid_transition_output_is_a_wall(self):
        original=self.client.request
        def altered(path):
            raw=original(path)
            if path.startswith('/step/'):
                raw=dict(raw)
                raw['output']=[9,9,9]
            return raw
        with patch.object(self.client,'request',side_effect=altered):
            t=self.bot.ask('Where do I end up after A?')
        self.assertEqual(t.status,'WALL_OBSERVATION')

    def test_replay_chain_is_consistent_with_pinned_source(self):
        t=self.bot.ask('Where do I end up after A then B then A then B?')
        self.assertEqual(t.status,'WITNESSED_ENDPOINT')
        states=t.paths[0].states
        for i,a in enumerate(t.paths[0].word):
            self.assertEqual(self.owner.select(0).step(states[i],a),states[i+1])

    def test_unknown_after_endpoint_invalidates_followup(self):
        self.bot.ask('Where do I end up after A?')
        self.bot.ask('Which side is true?')
        self.assertEqual(self.bot.ask('And then B?').status,'UNKNOWN_CONTEXT')

    def test_history_preserves_question_wording_version_scope(self):
        a=self.bot.ask('Where do I end up after AB?')
        b=self.bot.ask('Which A/B relationship class fits?')
        self.assertEqual(len(self.bot.history),2)
        self.assertEqual(a.user_text,'Where do I end up after AB?')
        self.assertEqual(a.digest,b.digest)
        self.assertEqual(a.origin_scope,'LOCAL_OWNER_VERIFIED')
        self.assertEqual(b.status,'CONDITIONAL_CLASS')


class EdgeBudgetTests(unittest.TestCase):
    def setUp(self):
        h=tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner=SourceOwnedHTTP(TransportedLaw((0,1,2),h))
        self.server=LoopbackHTTP(self.owner)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__,None,None,None)
        self.client=RemoteObserver(self.server.url)

    def test_budget_blocks_new_edges_not_replays(self):
        bot=LanguageBridge(self.client,owner=self.owner,edge_budget=2)
        a=bot.ask('Where do I end up after AB?')
        self.assertEqual(a.status,'WITNESSED_ENDPOINT')
        self.assertEqual(bot.ask('Where do I end up after AB?').status,'WITNESSED_ENDPOINT')
        n=self.client.calls
        t=bot.ask('And then B?')
        self.assertEqual(t.status,'UNKNOWN_BUDGET')
        self.assertEqual(self.client.calls,n)
        self.assertEqual(len(bot.snapshot.edges),2)

    def test_zero_budget_prevents_network_edge_request(self):
        bot=LanguageBridge(self.client,owner=self.owner,edge_budget=0)
        self.assertEqual(self.client.calls,1)
        t=bot.ask('Where do I end up after A?')
        self.assertEqual(t.status,'UNKNOWN_BUDGET')
        self.assertEqual(self.client.calls,1)

    def test_bad_budget_is_rejected_before_service_start(self):
        for value in (-1,55,True,'3'):
            with self.assertRaises(ValueError):
                LanguageBridge(self.client,owner=self.owner,edge_budget=value)

    def test_partial_class_witness_retained_when_edge_budget_runs_out(self):
        bot=LanguageBridge(self.client,owner=self.owner,edge_budget=5)
        t=bot.ask('Which A/B relationship class fits?')
        self.assertEqual(t.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(bot.snapshot.edges),5)
        self.assertTrue(t.class_probes)  # earlier complete relational probes preserved
        self.assertEqual(t.class_candidates,())


if __name__ == "__main__":
    unittest.main()
