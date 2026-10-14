"""Exact signed-source declaration -> already-cached CP30 native-edge comparison."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('CP30_NATIVE_SOURCE_DIR', '.')).resolve()
if ROOT.is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.workspace.external_native_binding import bind_external_observation_to_native
from network.tests import test_external_route_mapping as mapping_tests


@unittest.skipUnless((ROOT/'test_ab_chatbot_route_bound_task.py').is_file(),
                     'CP30_NATIVE_SOURCE_DIR must point to reconstructed CP30')
class ExternalNativeBindingTests(unittest.TestCase):
    def setUp(self):
        from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
        self.helper = RouteBoundTaskTests('runTest')
        self.refresh, _, self.left, self.right, *_ = self.helper.fixture()
        self.tasks = {
            'admitted': self.helper.task(self.refresh, 'left',
                         required_edges=[{'state': [1, 0, 0], 'action': 'B'}]),
            'unproved': self.helper.task(self.refresh, 'left',
                         required_edges=[{'state': [0, 1, 2], 'action': 'B'}]),
        }
        self.external = mapping_tests.ExternalRouteMappingTests(
            'test_signed_public_bytes_map_to_declarations_but_never_owner_proof')
        self.external.setUp()
        self.addCleanup(self.external.doCleanups)

    def observation(self, change=None, fingerprint=None):
        scopes = {s: p for s,p in zip(('donor','middle','final'),
                    (self.left.first.donor, self.left.first.recipient, self.left.final))}
        def mutate(scope, data):
            p = scopes[scope]
            for side in ('old', 'new'):
                bridge = getattr(p, side)
                assert bridge.snapshot.edges
                state, action = next(iter(bridge.snapshot.edges))
                target = bridge.snapshot.edges[(state, action)]
                data[side] = {'source_label': bridge.snapshot.claimed_source,
                              'revision': bridge.snapshot.revision,
                              'phi': [0, 0, 0],
                              'claimed_edges': [{'state': list(state),
                                'action': action, 'target': list(target)}]}
            if change:
                change(scope, data)
        with patch.object(mapping_tests, 'ROUTE_FP',
                          fingerprint or self.tasks['admitted'].expected):
            self.external.signed_observation(mutate=mutate)

    def bind(self, *, capture=None, files=None):
        return bind_external_observation_to_native(
            data_dir=self.external.data, challenge=self.external.challenge,
            observation_event=self.external.observation['observation_event'],
            source_files=self.external.files if files is None else files,
            native_source_root=ROOT,
            source_capture=capture or (lambda: self.tasks))

    def test_matching_cached_edges_are_not_full_owner_proof(self):
        self.observation()
        before=(self.external.store.path.read_bytes(),
                tuple(len(getattr(p,side).snapshot.edges) for p in
                      (self.left.first.donor,self.left.first.recipient,self.left.final)
                      for side in ('old','new')))
        r=self.bind()
        self.assertEqual(r['status'], 'EXTERNAL_DECLARED_EDGES_MATCH_NATIVE_LOCAL_CACHE')
        self.assertEqual(r['matched_native_sides'], 6)
        self.assertEqual(r['matched_declared_edges'], 6)
        self.assertEqual(r['route'], 'left')
        self.assertTrue(r['native_in_process_owner_pins_current_at_both_captures'])
        for label in ('external_source_identity_authenticated',
                      'external_owner_equivalence_proved',
                      'full_native_transition_tables_matched',
                      'native_cp30_route_certificate_verified',
                      'fresh_native_two_pass_route_audit',
                      'exact_task_authorized', 'journal_modified',
                      'new_transition_observations'):
            self.assertIs(r[label], False, label)
        after=(self.external.store.path.read_bytes(),
               tuple(len(getattr(p,side).snapshot.edges) for p in
                     (self.left.first.donor,self.left.first.recipient,self.left.final)
                     for side in ('old','new')))
        self.assertEqual(before,after)
        self.assertFalse((self.external.data/'runtime.jsonl').exists())

    def test_no_new_native_edges_requested_to_establish_external_match(self):
        self.observation()
        from ab_chatbot_language_bridge import PinnedEdges
        with patch.object(PinnedEdges, 'step', side_effect=AssertionError('unrequested oracle step')):
            report = self.bind()
        self.assertEqual(report['matched_declared_edges'], 6)

    def test_evidence_journal_update_during_native_capture_rejected(self):
        self.observation()
        called = 0
        def capture():
            nonlocal called
            called += 1
            if called == 2:
                pin = self.external.store._state()[0]['donor']
                self.external.store.revoke(scope='donor',
                    confirm_key_sha256=pin['key_sha256'], operator='test-reader')
            return self.tasks
        with self.assertRaisesRegex(ValueError,'journal changed'):
            self.bind(capture=capture)

    def test_wrong_selected_route_fingerprint_rejected(self):
        self.observation(fingerprint='f'*64)
        with self.assertRaisesRegex(ValueError, 'route referent'):
            self.bind()

    def test_unknown_native_edge_is_not_inferred_from_matching_law(self):
        def change(scope,d):
            if scope=='middle':
                d['old']['claimed_edges']=[{'state':[2,2,2],'action':'A','target':[0,2,2]}]
        self.observation(change)
        with self.assertRaisesRegex(ValueError, 'not witnessed'):
            self.bind()

    def test_wrong_native_source_label_rejected_even_when_signed(self):
        def change(scope,d):
            if scope=='donor':d['old']['source_label']='pretend-other-owner'
        self.observation(change)
        with self.assertRaisesRegex(ValueError,'label or revision'):
            self.bind()

    def test_wrong_native_revision_rejected_even_when_signed(self):
        def change(scope,d):
            if scope=='final':d['new']['revision']+=1
        self.observation(change)
        with self.assertRaisesRegex(ValueError,'label or revision'):
            self.bind()

    def test_claimed_transition_mismatch_rejected_even_when_law_consistent(self):
        def change(scope,d):
            if scope=='donor':
                d['old']['phi']=[2,0,0]
                d['old']['claimed_edges']=[{'state':[0,0,0],'action':'B',
                                            'target':[0,1,2]}]
        self.observation(change)
        with self.assertRaisesRegex(ValueError,'contradicts native'):
            self.bind()

    def test_empty_declared_edge_set_cannot_count_as_mapping(self):
        def change(scope,d):
            if scope=='final':d['old']['claimed_edges']=[]
        self.observation(change)
        with self.assertRaisesRegex(ValueError,'at least one exact'):
            self.bind()

    def test_changed_signed_source_bytes_rejected(self):
        self.observation()
        self.external.files['donor'].write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,'do not match'):
            self.bind()

    def test_revoked_source_owner_pin_rejected(self):
        self.observation()
        pin=self.left.first.recipient
        pin.registry.revoke(pin._base._tokens[0])
        with self.assertRaisesRegex(ValueError,'pin is revoked'):
            self.bind()

    def test_replaced_native_task_between_captures_rejected(self):
        self.observation()
        count=0
        def capture():
            nonlocal count
            count+=1
            if count==2:
                return {**self.tasks,'admitted':self.helper.task(self.refresh,'left',
                                required_edges=[{'state':[1,0,0],'action':'B'}])}
            return self.tasks
        with self.assertRaisesRegex(ValueError,'changed during'):
            self.bind(capture=capture)

    def test_source_owned_callback_is_not_a_serialized_owner(self):
        self.observation()
        with self.assertRaises((ValueError,TypeError,AttributeError)):
            self.bind(capture=lambda:{'pretend':{'native_owner':True}})

    def test_partial_or_wrong_source_file_scope_rejected(self):
        self.observation()
        with self.assertRaisesRegex(ValueError,'exact donor'):
            self.bind(files={'donor':self.external.files['donor']})

    def test_corrupt_evidence_journal_not_ignored(self):
        self.observation()
        with self.external.store.path.open('a') as out:out.write('{bad\n')
        with self.assertRaisesRegex(ValueError,'corrupt'):
            self.bind()


if __name__=='__main__': unittest.main()
