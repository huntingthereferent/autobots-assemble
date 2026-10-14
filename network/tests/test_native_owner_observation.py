"""Native live-source interface tests against recovered CP30's actual objects."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(os.environ.get('CP30_NATIVE_SOURCE_DIR', '.')).resolve()
if ROOT.is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.workspace.native_owner_observation import observe_native_owners


@unittest.skipUnless(ROOT.is_dir() and (ROOT/'test_ab_chatbot_route_bound_task.py').exists(),
                     'recovered CP30 source required; provide CP30_NATIVE_SOURCE_DIR')
class NativeOwnerObservationTests(unittest.TestCase):
    def setUp(self):
        from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
        self.helper=RouteBoundTaskTests('runTest')
        self.refresh,self.comparison,self.left,self.right,*_=self.helper.fixture()
        self.tasks={"admitted":self.helper.task(self.refresh,'left',required_edges=[
            {"state":[1,0,0],"action":"B"}]),
            "missing":self.helper.task(self.refresh,'left',required_edges=[
            {"state":[0,1,2],"action":"B"}])}

    def observe(self,**kwargs):
        return observe_native_owners(native_source_root=ROOT,
                                     source_capture=lambda:self.tasks,**kwargs)

    def test_read_only_native_capture_does_not_audit(self):
        from ab_chatbot_shared_route_certificate import audit_route
        with patch('ab_chatbot_shared_route_certificate.audit_route',side_effect=AssertionError('no audit')):
            row=self.observe()
        self.assertEqual(row['status'],'NATIVE_LOCAL_PINNED_SOURCE_OBSERVED')
        self.assertFalse(row['fresh_native_two_pass_route_audit'])
        self.assertFalse(row['all_declared_tasks_completed'])
        self.assertTrue(row['local_owner_pins_verified'])
        self.assertFalse(row['cp30_independent_process_attestation_verified'])

    def test_opt_in_exact_tasks_keep_missing_edge_unproved(self):
        row=self.observe(allow_native_audit=True)
        self.assertEqual(row['native_audit_status'],'TWO_HOP_CHAIN_WITNESSED')
        self.assertTrue(row['fresh_native_two_pass_route_audit'])
        self.assertEqual({t['name']:t['status'] for t in row['task_results']}, {
            'admitted':'TASK_COMPLETED_ON_SELECTED_ROUTE',
            'missing':'ROUTE_TASK_REQUIREMENTS_UNPROVED'})
        self.assertFalse(row['all_declared_tasks_completed'])
        self.assertFalse(row['external_signed_observation_mapped_to_native'])
        self.assertFalse(row['runtime_handoff_admitted'])

    def test_no_implicit_owner_construction_from_serialized_data(self):
        for payload in ({'route':'left','tasks':[]},'https://github.com/test/repo',[]):
            with self.subTest(payload=payload):
                with self.assertRaises((ValueError,AttributeError,TypeError)):
                    observe_native_owners(native_source_root=ROOT,source_capture=lambda:payload)

    def test_wrong_native_source_directory_fails_closed(self):
        with self.assertRaises(ValueError):
            observe_native_owners(native_source_root=ROOT.parent,source_capture=lambda:self.tasks)

    def test_revoked_selected_pin_blocks_capture(self):
        pin=self.left.first.recipient
        pin.registry.revoke(pin._base._tokens[0])
        with self.assertRaisesRegex(ValueError,'pin is revoked'):
            self.observe()

    def test_neighbor_revocation_does_not_poison_selected_route(self):
        right=self.right.first.recipient
        right.registry.revoke(right._base._tokens[0])
        row=self.observe(allow_native_audit=True)
        self.assertTrue(row['fresh_native_two_pass_route_audit'])

    def test_replaced_task_between_captures_rejected(self):
        calls=0
        def supplier():
            nonlocal calls
            calls+=1
            if calls==1:return self.tasks
            return {**self.tasks,'admitted':self.helper.task(self.refresh,'left',required_edges=[
                {'state':[1,0,0],'action':'B'}])}
        with self.assertRaisesRegex(ValueError,'changed during'):
            observe_native_owners(native_source_root=ROOT,source_capture=supplier)

    def test_mutated_snapshot_between_captures_rejected(self):
        calls=0
        def capture():
            nonlocal calls
            calls+=1
            if calls==2:
                pin=self.left.first.donor
                pin.registry.revoke(pin._base._tokens[0])
            return self.tasks
        with self.assertRaisesRegex(ValueError,'pin is revoked'):
            observe_native_owners(native_source_root=ROOT,source_capture=capture)

    def test_different_route_in_one_portfolio_rejected(self):
        self.tasks['right']=self.helper.task(self.refresh,'right',required_edges=[
            {'state':[0,1,2],'action':'B'}])
        with self.assertRaisesRegex(ValueError,'one exact'):
            self.observe()

    def test_duplicate_native_task_objects_rejected(self):
        self.tasks['alias']=self.tasks['admitted']
        with self.assertRaisesRegex(ValueError,'distinct task objects'):
            self.observe()

    def test_external_claim_flags_are_never_inferred(self):
        r=self.observe(allow_native_audit=True)
        for field in ['external_owner_identity_authenticated',
                      'external_signed_observation_mapped_to_native',
                      'cp30_independent_process_attestation_verified',
                      'cp29_receipt_revalidated','runtime_handoff_admitted']:
            self.assertIs(r[field],False)

    def test_repeated_capture_does_not_record_native_transition(self):
        pin=self.left.first.donor
        before=(len(pin.old.snapshot.edges),len(pin.new.snapshot.edges))
        self.observe()
        self.assertEqual(before,(len(pin.old.snapshot.edges),len(pin.new.snapshot.edges)))


if __name__=='__main__': unittest.main()
