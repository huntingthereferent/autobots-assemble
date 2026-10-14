"""Socket-level tests for the one finite mathematical observation interface."""
import unittest
from itertools import product
from urllib.error import HTTPError

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import DOMAIN, discover
from ab_chatbot_pinned_identity import KEYS, table_digest
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_http_snapshot import (
    LoopbackHTTP, RemoteObserver, SourceOwnedHTTP,
)


class HTTPWitnessTests(unittest.TestCase):
    def setUp(self):
        self.src = FiniteSystem((0,0,0))
        self.h = tuple((i,j,(k+i*j)%3) for i,j,k in DOMAIN)
        self.owner = SourceOwnedHTTP(TransportedLaw(self.src.phi,self.h))
        self.service = LoopbackHTTP(self.owner)
        self.service.__enter__()
        self.addCleanup(self.service.__exit__,None,None,None)
        self.client = RemoteObserver(self.service.url)

    def full(self):
        snap=self.client.snapshot()
        prior=discover(self.src,lambda s,a:self.client.edge(s,a,snap.revision)[0],full=True)
        self.assertEqual(prior.status,'FULL_CONJUGACY')
        bound=self.owner.bind(self.src,prior,snap)
        return snap,prior,bound

    def test_real_socket_http_and_owner_captured_snapshot(self):
        raw=self.client.request('/snapshot/current')
        self.assertEqual(raw['revision'],0)
        self.assertEqual(len(raw['values']),54)
        self.assertEqual(self.client.head()['digest'],raw['digest'])

    def test_remote_full_discovery_is_witnessed_over_network(self):
        snap,prior,bound=self.full()
        self.assertEqual(prior.calls,54)
        self.assertEqual(self.owner.reenter(self.src,prior,bound,snap).status,'SAME_PINNED_VERSION')
        self.assertGreaterEqual(self.client.calls,55)

    def test_source_ownership_prevents_witness_transfer_to_other_source(self):
        snap,prior,bound=self.full()
        alien=SourceOwnedHTTP(TransportedLaw(self.src.phi,self.h))
        self.assertEqual(alien.reenter(self.src,prior,bound,snap).status,'UNKNOWN_UNBOUND')
        with self.assertRaises(ValueError):
            alien.bind(self.src,prior,snap)

    def test_local_source_update_preserves_historical_revision(self):
        snap,prior,bound=self.full()
        self.owner.replace(TransportedLaw((0,1,0),self.h))
        historical=self.client.snapshot(0)
        current=self.client.snapshot()
        self.assertEqual(historical,snap)
        self.assertEqual(current.revision,1)
        self.assertEqual(self.owner.reenter(self.src,prior,bound,historical).status,'SAME_PINNED_VERSION')
        self.assertEqual(self.owner.reenter(self.src,prior,bound,current).status,'CHANGED')

    def test_source_owned_aba_history_keeps_revisions_distinct(self):
        snap,prior,bound=self.full()
        self.owner.replace(TransportedLaw((0,1,0),self.h))
        self.owner.replace(TransportedLaw(self.src.phi,self.h))
        now=self.client.snapshot()
        self.assertEqual(now.digest,snap.digest)
        self.assertEqual(now.revision,2)
        self.assertEqual(self.owner.reenter(self.src,prior,bound,now).status,'SAME_ENDPOINT_LAW_NEW_VERSION')

    def test_repeated_live_reads_single_revision_are_only_observed_match(self):
        scan=self.client.live_scan()
        self.assertEqual(scan.status,'OBSERVED_SINGLE_REVISION')
        self.assertEqual(scan.calls,54)
        self.assertEqual(set(scan.revisions),{0})

    def test_live_scan_mutates_after_first_read_and_detects_revision_change(self):
        def hook(i):
            if i==0:
                self.owner.replace(TransportedLaw((0,1,0),self.h))
        scan=self.client.live_scan(after=hook)
        self.assertEqual(scan.status,'MIXED_REVISIONS')
        self.assertEqual(scan.revisions[0],0)
        self.assertEqual(set(scan.revisions[1:]),{1})

    def test_live_scan_budget_never_promotes_partial_observation(self):
        scan=self.client.live_scan(budget=3)
        self.assertEqual(scan.status,'UNKNOWN_BUDGET')
        self.assertEqual(scan.calls,3)

    def test_snapshot_captured_before_update_serializes_original(self):
        events=[]
        def hook():
            self.owner.after_capture=None
            self.owner.replace(TransportedLaw((0,1,0),self.h))
            events.append(True)
        self.owner.after_capture=hook
        snap=self.client.snapshot()
        self.assertEqual(events,[True])
        self.assertEqual(snap.revision,0)
        self.assertEqual(self.client.head()['revision'],1)
        self.assertNotEqual(self.client.snapshot().digest,snap.digest)

    def test_revision_specific_edges_never_follow_current_head(self):
        old=self.client.snapshot()
        self.owner.replace(TransportedLaw((0,1,0),self.h))
        for state,action in KEYS:
            output,revision=self.client.edge(state,action,0)
            self.assertEqual(revision,0)
            self.assertEqual(output,old.step(state,action))

    def test_hash_only_checks_internal_coherence_not_origin(self):
        raw=self.client.request('/snapshot/current')
        fake=dict(raw)
        fake['source']='completely different source'
        claim=self.client.decode_snapshot(fake)
        self.assertEqual(claim.digest,table_digest(claim.values))
        self.assertIsNone(self.owner.owned_view(claim))

    def test_mutated_table_without_new_digest_rejected(self):
        raw=self.client.request('/snapshot/current')
        raw['values'][0][0]=(raw['values'][0][0]+1)%3
        with self.assertRaises(ValueError):
            self.client.decode_snapshot(raw)

    def test_truncated_or_bad_data_is_rejected(self):
        raw=self.client.request('/snapshot/current')
        raw['values']=raw['values'][:-1]
        with self.assertRaises(ValueError):
            self.client.decode_snapshot(raw)
        raw=self.client.request('/snapshot/current')
        raw['values'][0]=[3,0,0]
        with self.assertRaises(ValueError):
            self.client.decode_snapshot(raw)

    def test_invalid_revision_and_invalid_edge_fail_safely(self):
        with self.assertRaises(HTTPError):
            self.client.request('/snapshot/999')
        with self.assertRaises(HTTPError):
            self.client.request('/step/0?state=3,0,0&action=A')
        with self.assertRaises(ValueError):
            self.client.edge((3,0,0),'A')

    def test_read_only_routes_do_not_mutate_owner_head(self):
        before=self.client.head()
        for _ in range(4):
            self.client.snapshot()
            self.client.edge((0,0,0),'A')
        self.assertEqual(self.client.head(),before)

    def test_all_27_constructed_finite_laws_have_consistent_remote_snapshot(self):
        hashes=set()
        for phi in product(range(3),repeat=3):
            self.owner.replace(TransportedLaw(phi,self.h))
            snap=self.client.snapshot()
            self.assertEqual(snap.values,tuple(TransportedLaw(phi,self.h).step(s,a) for s,a in KEYS))
            hashes.add(snap.digest)
        self.assertEqual(len(hashes),27)


if __name__ == '__main__':
    unittest.main()
