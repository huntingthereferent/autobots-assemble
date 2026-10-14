"""Completion claims require replayed transitions; limits never become success."""
import unittest
from unittest.mock import patch

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_goal_agent import GoalAgent
from ab_chatbot_stability_witness import TransportedLaw


class GoalAgentTests(unittest.TestCase):
    def setUp(self):
        h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner = SourceOwnedHTTP(TransportedLaw((0,1,2), h))
        self.server = LoopbackHTTP(self.owner)
        self.server.__enter__()
        self.addCleanup(self.server.__exit__, None, None, None)
        self.client = RemoteObserver(self.server.url, bound_loopback=self.server)
        self.bridge = LanguageBridge(self.client, owner=self.owner, edge_budget=54)

    def test_finds_witnessed_shortest_path_without_supplied_word(self):
        agent = GoalAgent(self.bridge, (1,2,2))
        self.assertEqual(agent.advance(max_new_edges=2).status, 'CONTINUING')
        result = agent.advance(max_new_edges=2)
        self.assertEqual(result.status, 'COMPLETE_WITNESSED')
        self.assertEqual(result.path.word, 'AB')
        self.assertEqual(result.path.states, ((0,0,0),(1,0,0),(1,2,2)))
        self.assertEqual(result.observed_edges, 4)
        n = self.client.calls
        self.assertEqual(agent.advance().path, result.path)
        self.assertEqual(self.client.calls, n)

    def test_reuses_observed_edges_for_new_goal(self):
        first = GoalAgent(self.bridge, (1,2,2)).advance(max_new_edges=5)
        self.assertEqual(first.status, 'COMPLETE_WITNESSED')
        n = self.client.calls
        second = GoalAgent(self.bridge, (1,0,0)).advance(max_new_edges=0)
        self.assertEqual(second.status, 'COMPLETE_WITNESSED')
        self.assertEqual(second.path.word, 'A')
        self.assertEqual(self.client.calls, n)

    def test_completed_state_can_be_next_start_without_resetting_source(self):
        first = GoalAgent(self.bridge, (1,2,2)).advance(max_new_edges=7)
        self.assertEqual(first.status, 'COMPLETE_WITNESSED')
        second = GoalAgent(self.bridge,(1,1,0), start=first.path.states[-1])
        result = second.advance(max_new_edges=10)
        self.assertEqual(result.status,'COMPLETE_WITNESSED')
        self.assertEqual(result.path.word,'B')
        self.assertEqual(first.path.word + result.path.word,'ABB')
        self.assertEqual(first.path.states[-1],result.path.states[0])

    def test_all_targets_across_distinct_source_laws_against_reference_bfs(self):
        from collections import deque
        h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        for law in ((0,0,0), (0,1,2), (1,1,1), (2,0,1)):
            with self.subTest(law=law):
                self.owner.replace(TransportedLaw(law,h))
                self.bridge.ask('Pin current version')
                model = self.owner.select()
                distances = {(0,0,0):0}
                queue = deque([(0,0,0)])
                while queue:
                    cur = queue.popleft()
                    for symbol in 'AB':
                        nxt = model.step(cur,symbol)
                        if nxt not in distances:
                            distances[nxt]=distances[cur]+1
                            queue.append(nxt)
                for target in DOMAIN:
                    report=GoalAgent(self.bridge,target).advance(max_new_edges=54)
                    if target in distances:
                        self.assertEqual(report.status, 'COMPLETE_WITNESSED')
                        self.assertEqual(len(report.path.word),distances[target])
                        self.assertEqual(report.path.states[-1],target)
                    else:
                        self.assertEqual(report.status, 'UNREACHABLE_CLOSED_COMPONENT')
                self.assertLessEqual(len(self.bridge.snapshot.edges),54)

    def test_explicit_budget_increase_resumes_identical_goal(self):
        self.bridge.snapshot.max_edges = 2
        agent = GoalAgent(self.bridge, (1,2,2))
        self.assertEqual(agent.advance(max_new_edges=12).status, 'UNKNOWN_BUDGET')
        self.assertEqual(len(self.bridge.snapshot.edges), 2)
        agent.authorize_total_edge_budget(6)
        self.assertEqual(agent.advance(max_new_edges=12).status,'COMPLETE_WITNESSED')
        self.assertEqual(agent.advance().path.word, 'AB')

    def test_zero_budget_can_use_cached_observations(self):
        self.bridge.ask('Where do I end up after AB?')
        agent=GoalAgent(self.bridge, (1,0,0))
        result=agent.advance(max_new_edges=0)
        self.assertEqual(result.status,'COMPLETE_WITNESSED')
        self.assertEqual(result.path.word,'A')

    def test_cutoff_is_not_general_unreachability(self):
        agent = GoalAgent(self.bridge, (1,2,2), max_depth=1)
        result = agent.advance(max_new_edges=54)
        self.assertEqual(result.status, 'NO_ROUTE_WITHIN_DEPTH')
        self.assertIsNone(result.path)

    def test_closed_component_is_complete_negative_witness(self):
        h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner.replace(TransportedLaw((0,0,0), h))
        self.bridge.ask('Pin current version')
        # k=0 source orbit cannot reach (0,0,1), even after coordinate shear.
        agent = GoalAgent(self.bridge,(0,0,1),max_depth=26)
        result = agent.advance(max_new_edges=54)
        self.assertEqual(result.status,'UNREACHABLE_CLOSED_COMPONENT')
        self.assertEqual(result.observed_edges, 18)
        self.assertIsNone(result.path)

    def test_explicit_repin_does_not_silently_change_goal(self):
        agent = GoalAgent(self.bridge,(1,2,2))
        agent.advance(max_new_edges=2)
        h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner.replace(TransportedLaw((0,2,0),h))
        self.bridge.ask('Pin current version')
        result = agent.advance(max_new_edges=4)
        self.assertEqual(result.status, 'UNKNOWN_VERSION')
        self.assertEqual(result.observed_edges, 2)

    def test_tampered_step_cannot_be_owner_verified(self):
        original=self.client.request
        def tamper(path):
            result=original(path)
            if path.startswith('/step/'):
                result=dict(result)
                result['output']=[2,2,2]  # valid shape, wrong owner's edge
            return result
        agent=GoalAgent(self.bridge, (1,2,2))
        with patch.object(self.client, 'request', side_effect=tamper):
            result=agent.advance(max_new_edges=4)
        self.assertEqual(result.status,'WALL_OBSERVATION')
        self.assertEqual(result.observed_edges, 0)
        self.assertIsNone(result.path)

    def test_unbound_observer_with_matching_owner_metadata_is_not_verified(self):
        remote=RemoteObserver(self.server.url)
        bridge=LanguageBridge(remote,owner=self.owner)
        self.assertEqual(bridge.origin_scope,'REMOTE_ORIGIN_UNVERIFIED')
        agent=GoalAgent(bridge,(1,0,0))
        result=agent.advance(max_new_edges=2)
        self.assertEqual(result.status, 'COMPLETE_REMOTE_REPORTED')
        self.assertEqual(result.origin_scope, 'REMOTE_ORIGIN_UNVERIFIED')

    def test_binding_requires_actual_local_endpoint(self):
        with self.assertRaises(ValueError):
            RemoteObserver('http://127.0.0.1:1',bound_loopback=self.server)

    def test_full_snapshot_reuses_preloaded_data(self):
        client=RemoteObserver(self.server.url,bound_loopback=self.server)
        bridge=LanguageBridge(client,owner=self.owner,mode='snapshot')
        reads=client.calls
        result=GoalAgent(bridge,(1,2,2)).advance(max_new_edges=0)
        self.assertEqual(result.status,'COMPLETE_WITNESSED')
        self.assertEqual(result.path.word,'AB')
        self.assertEqual(client.calls,reads)

    def test_unverified_source_cannot_be_made_verified_by_label_alone(self):
        # An unrelated observer can copy truthful metadata and serve a fake edge.
        remote=RemoteObserver(self.server.url)
        bridge=LanguageBridge(remote,owner=self.owner)
        original=remote.request
        def fake(path):
            raw=original(path)
            if path.startswith('/step/'):
                raw=dict(raw)
                raw['output']=[2,2,2]
            return raw
        with patch.object(remote,'request',side_effect=fake):
            result=GoalAgent(bridge,(2,2,2)).advance(max_new_edges=2)
        self.assertEqual(result.origin_scope,'REMOTE_ORIGIN_UNVERIFIED')
        self.assertEqual(result.status,'COMPLETE_REMOTE_REPORTED')
        # The path is only a REMOTE-REPORTED observation, not trusted local owner evidence.
        self.assertEqual(result.path.states, ((0,0,0),(2,2,2)))


if __name__ == '__main__':
    unittest.main()
