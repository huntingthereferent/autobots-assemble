"""Bounded route transfer across discovered, not pre-supplied, finite relabelings."""
import unittest
from dataclasses import replace

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_goal_agent import GoalAgent
from ab_chatbot_goal_transport import RootedGoalTransport, _check_rooted
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge, PathWitness
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw


class RootedGoalTransportTests(unittest.TestCase):
    def owner(self, phi, shear=0):
        return SourceOwnedHTTP(TransportedLaw(phi, tuple(
            (i, j, (k+shear*i*j) % 3) for i,j,k in DOMAIN)))

    def setUp(self):
        self.phi=(0,0,0)
        self.source_owner=self.owner(self.phi)
        self.target_owner=self.owner(self.phi, shear=1)
        self.source_server=LoopbackHTTP(self.source_owner)
        self.target_server=LoopbackHTTP(self.target_owner)
        self.source_server.__enter__()
        self.target_server.__enter__()
        self.addCleanup(self.target_server.__exit__, None,None,None)
        self.addCleanup(self.source_server.__exit__, None,None,None)
        self.source_client=RemoteObserver(self.source_server.url,bound_loopback=self.source_server)
        self.target_client=RemoteObserver(self.target_server.url,bound_loopback=self.target_server)
        self.source_bridge=LanguageBridge(self.source_client,owner=self.source_owner,edge_budget=54)
        self.target_bridge=LanguageBridge(self.target_client,owner=self.target_owner,edge_budget=54)
        self.transport=RootedGoalTransport(FiniteSystem(self.phi),self.source_bridge,self.target_bridge)

    def test_discovers_nonlinear_mapping_without_supplied_mapping(self):
        original=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        self.assertEqual(original.path.word, 'AB')
        result=self.transport.carry(original,max_queries=18)
        self.assertEqual(result.status,'PRESERVED_ROOTED_WITNESSED')
        self.assertEqual(result.transported_path.word,'AB')
        self.assertEqual(result.transported_path.states,((0,0,0),(1,0,0),(1,2,2)))
        self.assertEqual(result.source_rooted_states,9)
        self.assertEqual(result.target_new_edge_reads,18)
        self.assertEqual(len(self.target_bridge.snapshot.edges),18)
        self.assertEqual(self.target_owner.select().step((1,0,0),'B'),(1,2,2))
        self.assertEqual(self.transport.discovery.status,'ROOTED_REACHABLE')
        self.assertEqual(self.transport.discovery.full_pairs,())

    def test_reuses_correspondence_for_all_reachable_goals_without_new_target_reads(self):
        a=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        self.assertEqual(self.transport.carry(a).status,'PRESERVED_ROOTED_WITNESSED')
        after=self.target_client.calls
        mapping=dict(self.transport.discovery.rooted_pairs)
        for s in mapping:
            with self.subTest(state=s):
                goal=GoalAgent(self.source_bridge,s).advance(max_new_edges=54)
                self.assertEqual(goal.status,'COMPLETE_WITNESSED')
                carried=self.transport.carry(goal)
                self.assertEqual(carried.status,'PRESERVED_ROOTED_WITNESSED')
                self.assertEqual(carried.transported_path.states[-1],mapping[s])
                self.assertEqual(carried.transported_path.word,goal.path.word)
        self.assertEqual(self.target_client.calls,after)

    def test_query_budget_preserves_evidence_and_can_resume(self):
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        result=self.transport.carry(g,max_queries=4)
        self.assertEqual(result.status,'UNKNOWN_RELATION_BUDGET')
        self.assertIsNone(result.transported_path)
        self.assertEqual(len(self.target_bridge.snapshot.edges),4)
        result=self.transport.carry(g,max_queries=18)
        self.assertEqual(result.status,'PRESERVED_ROOTED_WITNESSED')
        self.assertEqual(result.target_new_edge_reads,18)

    def test_total_edge_budget_is_not_raised_by_discovery(self):
        self.target_bridge.snapshot.max_edges=5
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        r=self.transport.carry(g,max_queries=18)
        self.assertEqual(r.status,'UNKNOWN_RELATION_BUDGET')
        self.assertEqual(len(self.target_bridge.snapshot.edges),5)
        self.assertEqual(self.target_bridge.snapshot.max_edges,5)

    def test_rejects_incompatible_target_law(self):
        self.target_owner.replace(TransportedLaw((0,1,2),tuple(
            (i,j,(k+i*j)%3) for i,j,k in DOMAIN)))
        self.target_bridge.ask('Pin current version')
        tr=RootedGoalTransport(FiniteSystem(self.phi),self.source_bridge,self.target_bridge)
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        r=tr.carry(g,max_queries=54)
        self.assertEqual(r.status,'ROOTED_OBSTRUCTED')
        self.assertIsNone(r.transported_path)

    def test_rejects_fake_source_path_and_unobserved_source_path(self):
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        bad=replace(g,path=PathWitness('AB',((0,0,0),(1,0,0),(2,2,2))))
        self.assertEqual(self.transport.carry(bad).status,'WALL_SOURCE_GOAL')
        # Even if a forged record states the right endpoint, no unobserved
        # mathematical path is allowed into the target transport.
        unobserved=replace(g,path=PathWitness('ABA', ((0,0,0),(1,0,0),(1,2,0),(2,2,0))))
        self.assertEqual(self.transport.carry(unobserved).status,'WALL_SOURCE_GOAL')

    def test_repin_invalidates_existing_transport(self):
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        self.assertEqual(self.transport.carry(g).status,'PRESERVED_ROOTED_WITNESSED')
        self.target_owner.replace(TransportedLaw(self.phi, tuple(
            (i,j,(k+i*j)%3) for i,j,k in DOMAIN)))
        self.target_bridge.ask('Pin current version')
        self.assertEqual(self.transport.carry(g).status,'UNKNOWN_VERSION')

    def test_unbound_observer_keeps_remote_reported_status(self):
        remote=LanguageBridge(RemoteObserver(self.target_server.url), owner=self.target_owner,edge_budget=54)
        tr=RootedGoalTransport(FiniteSystem(self.phi),self.source_bridge,remote)
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        result=tr.carry(g,max_queries=18)
        self.assertEqual(result.status,'PRESERVED_ROOTED_REMOTE_REPORTED')
        self.assertIsNotNone(result.transported_path)

    def test_multiple_laws_and_coordinate_shears(self):
        for law in ((0,0,0),(0,1,2),(1,1,1)):
            for shear in (1,2):
                with self.subTest(law=law,shear=shear):
                    source=FiniteSystem(law)
                    owned_s=self.owner(law)
                    owned_t=self.owner(law,shear)
                    with LoopbackHTTP(owned_s) as ls, LoopbackHTTP(owned_t) as lt:
                        bs=LanguageBridge(RemoteObserver(ls.url,bound_loopback=ls),owner=owned_s,edge_budget=54)
                        bt=LanguageBridge(RemoteObserver(lt.url,bound_loopback=lt),owner=owned_t,edge_budget=54)
                        reach=GoalAgent(bs,source.follow('AB')).advance(max_new_edges=54)
                        self.assertEqual(reach.status,'COMPLETE_WITNESSED')
                        result=RootedGoalTransport(source,bs,bt).carry(reach,max_queries=54)
                        self.assertEqual(result.status,'PRESERVED_ROOTED_WITNESSED')
                        self.assertEqual(result.transported_path.states[-1],
                                         (lambda i,j,k:(i,j,(k+shear*i*j)%3))(*reach.path.states[-1]))

    def test_rooted_match_does_not_claim_off_root_equality(self):
        from ab_chatbot_discovered_correspondence import discover
        law=FiniteSystem((0,0,0))
        def altered_offroot(s,action):
            if s == (0,0,1) and action == 'B':
                return (0,1,0)  # one off-root edge changed
            return law.step(s,action)
        partial=discover(law,altered_offroot,full=False,max_queries=54)
        self.assertEqual(partial.status,'ROOTED_REACHABLE')
        self.assertEqual(partial.rooted_count,9)
        whole=discover(law,altered_offroot,full=True,max_queries=54)
        self.assertNotEqual(whole.status,'FULL_CONJUGACY')

    def test_replay_rejects_forged_or_incomplete_rooted_record(self):
        g=GoalAgent(self.source_bridge,(1,2,0)).advance(max_new_edges=54)
        self.transport.carry(g,max_queries=18)
        rec=self.transport.discovery
        self.assertTrue(_check_rooted(FiniteSystem(self.phi),rec,(0,0,0),(0,0,0)))
        self.assertFalse(_check_rooted(FiniteSystem(self.phi),replace(rec,observed=rec.observed[:-1]),
                                       (0,0,0),(0,0,0)))
        self.assertFalse(_check_rooted(FiniteSystem(self.phi),replace(rec,rooted_pairs=rec.rooted_pairs[:-1]),
                                       (0,0,0),(0,0,0)))


if __name__=='__main__':
    unittest.main()
