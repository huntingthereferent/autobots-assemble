"""Out-of-band trust anchor relative to exact signed/observed CP30-native snapshots."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(os.environ.get('CP30_NATIVE_SOURCE_DIR', '.')).resolve()
if ROOT.is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.workspace.external_authority_binding import (
    prepare_authority_binding, verify_authority_binding, AuthorityAnchorLedger,
)
from systems.workspace.external_evidence import _canonical
from network.tests import test_external_native_binding as previous_tests


@unittest.skipUnless((ROOT/'test_ab_chatbot_route_bound_task.py').is_file(),
                     'CP30_NATIVE_SOURCE_DIR must point to reconstructed CP30')
class ExternalAuthorityBindingTests(unittest.TestCase):
    def setUp(self):
        previous = previous_tests.ExternalNativeBindingTests('test_matching_cached_edges_are_not_full_owner_proof')
        previous.setUp()
        self.addCleanup(previous.doCleanups)
        self.earlier = previous
        previous.observation()
        self.native_root = ROOT
        self.authority = Ed25519PrivateKey.generate()
        self.public_raw = self.authority.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        self.public = base64.b64encode(self.public_raw).decode('ascii')
        self.fp = sha256(self.public_raw).hexdigest()
        self.anchors = AuthorityAnchorLedger(previous.external.data)
        self.anchors.pin(authority_id="independent-policy-authority",
                         public_key=self.public, confirm_fingerprint=self.fp,
                         operator="reviewer", verification_reference="out-of-band/test-fixture-root")

    def params(self):
        return dict(data_dir=self.earlier.external.data,
                    challenge=self.earlier.external.challenge,
                    observation_event=self.earlier.external.observation['observation_event'],
                    source_files=self.earlier.external.files,
                    native_source_root=self.native_root,
                    source_capture=lambda: self.earlier.tasks,
                    authority_id='independent-policy-authority',
                    authority_public_key=self.public,
                    anchor_fingerprint=self.fp)

    def unsigned(self):
        return prepare_authority_binding(**self.params())

    def signed(self, statement=None):
        statement = statement if statement is not None else self.unsigned()
        return {'statement':statement,
                'signature':base64.b64encode(self.authority.sign(_canonical(statement))).decode('ascii')}

    def verify(self, grant=None, **changes):
        return verify_authority_binding(**{**self.params(), **changes},
                                        signed_grant=grant if grant is not None else self.signed())

    def test_pinned_external_authority_can_attest_exact_six_snapshots_without_native_upgrade(self):
        store = self.earlier.external.store
        journal = store.path.read_bytes()
        edge_counts = self._edge_counts()
        intent = self.unsigned()
        self.assertEqual(tuple(intent['scopes']), ('donor','middle','final'))
        for scope in intent['scopes']:
            self.assertEqual(set(intent['scopes'][scope]['native_sides']), {'old','new'})
            for side in intent['scopes'][scope]['native_sides'].values():
                self.assertEqual(len(side['snapshot_digest']),64)
        verdict = self.verify(self.signed(intent))
        self.assertEqual(verdict['status'],'OPERATOR_ANCHORED_SNAPSHOT_DELEGATION_VERIFIED')
        self.assertEqual(verdict['verified_native_snapshot_sides'],6)
        for key in ('out_of_band_trust_anchor_authenticated_by_module',
                    'real_world_external_owner_authenticated', 'legal_ownership_proved',
                    'cp30_independent_process_attestation_verified',
                    'fresh_native_route_audit', 'cp29_receipt_revalidated',
                    'exact_task_authorized','native_handoff_admitted',
                    'new_transitions_observed','journal_modified'):
            self.assertIs(verdict[key],False,key)
        self.assertEqual(store.path.read_bytes(),journal)
        self.assertEqual(self._edge_counts(),edge_counts)
        self.assertFalse((self.earlier.external.data/'runtime.jsonl').exists())

    def _edge_counts(self):
        chain=self.earlier.left
        return tuple(len(getattr(pin,side).snapshot.edges) for pin in
                     (chain.first.donor,chain.first.recipient,chain.final)
                     for side in ('old','new'))

    def test_wrong_confirmed_anchor_fingerprint_is_not_trusted(self):
        with self.assertRaises(PermissionError):
            prepare_authority_binding(**{**self.params(),'anchor_fingerprint':'0'*64})
        with self.assertRaises(PermissionError):
            self.verify(self.signed(), anchor_fingerprint='0'*64)

    def test_unenrolled_authority_signature_forgery_rejected(self):
        grant=self.signed()
        wrong=Ed25519PrivateKey.generate()
        grant['signature']=base64.b64encode(wrong.sign(_canonical(grant['statement']))).decode()
        with self.assertRaisesRegex(ValueError,'signature unproved'):self.verify(grant)

    def test_authority_grant_signed_by_same_enrolled_source_key_is_not_independent(self):
        source_private=self.earlier.external.secret['donor']
        raw=source_private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        self.anchors.pin(authority_id='other-authority',
                         public_key=base64.b64encode(raw).decode(),
                         confirm_fingerprint=sha256(raw).hexdigest(),
                         operator='reviewer',verification_reference='fixture-key')
        with self.assertRaisesRegex(ValueError,'must differ'):
            prepare_authority_binding(**{**self.params(),
                   'authority_id':'other-authority',
                   'authority_public_key':base64.b64encode(raw).decode(),
                   'anchor_fingerprint':sha256(raw).hexdigest()})

    def test_reissued_grant_for_fake_native_digest_fails_despite_valid_signature(self):
        changed=self.unsigned()
        changed['scopes']['middle']['native_sides']['new']['snapshot_digest']='f'*64
        with self.assertRaisesRegex(ValueError,'differs from current'):
            self.verify(self.signed(changed))

    def test_modified_declared_witness_with_resigned_grant_is_refused(self):
        changed=self.unsigned(); changed['witness_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'differs from current'):
            self.verify(self.signed(changed))

    def test_changed_signed_observed_file_after_issue_rejected(self):
        grant=self.signed()
        target=self.earlier.external.files['final']
        target.write_text(target.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'do not match'):
            self.verify(grant)

    def test_changed_live_task_object_after_issue_rejected(self):
        grant=self.signed()
        helper=self.earlier.helper
        self.earlier.tasks['admitted']=helper.task(self.earlier.refresh,'left',
            required_edges=[{'state':[1,0,0],'action':'B'}])
        with self.assertRaisesRegex(ValueError,'differs from current|changed'):
            self.verify(grant)

    def test_revoked_native_source_pin_after_issue_rejected(self):
        grant=self.signed()
        pin=self.earlier.left.first.recipient
        pin.registry.revoke(pin._base._tokens[0])
        with self.assertRaisesRegex(ValueError,'pin is revoked'):
            self.verify(grant)

    def test_revoked_signing_source_key_after_issue_rejected(self):
        grant=self.signed()
        active=self.earlier.external.store._state()[0]
        self.earlier.external.store.revoke(scope='middle',
            confirm_key_sha256=active['middle']['key_sha256'],operator='receiver')
        with self.assertRaisesRegex(ValueError,'revoked or rotated'):
            self.verify(grant)

    def test_grant_with_missing_scope_or_extra_field_fails(self):
        broken=self.unsigned();del broken['scopes']['donor']
        with self.assertRaisesRegex(ValueError,'differs from current'):
            self.verify(self.signed(broken))
        broken=self.unsigned(); broken['automatic_task_admission']=True
        with self.assertRaisesRegex(ValueError,'invalid fields'):
            self.verify(self.signed(broken))

    def test_grant_expiry_and_future_issue_rejected(self):
        statement=self.unsigned()
        past=datetime.now(timezone.utc)-timedelta(hours=1)
        statement['issued_at']=past.isoformat()
        statement['expires_at']=(past+timedelta(minutes=2)).isoformat()
        with self.assertRaisesRegex(ValueError,'lifetime'):
            self.verify(self.signed(statement))
        statement=self.unsigned()
        soon=datetime.now(timezone.utc)+timedelta(minutes=1)
        statement['issued_at']=soon.isoformat()
        statement['expires_at']=(soon+timedelta(minutes=2)).isoformat()
        with self.assertRaisesRegex(ValueError,'lifetime'):
            self.verify(self.signed(statement))

    def test_long_lived_grant_forbidden(self):
        statement=self.unsigned()
        issued=datetime.fromisoformat(statement['issued_at'])
        statement['expires_at']=(issued+timedelta(hours=1)).isoformat()
        with self.assertRaisesRegex(ValueError,'lifetime'):
            self.verify(self.signed(statement))

    def test_wrong_authority_id_and_key_are_rejected(self):
        grant=self.signed()
        with self.assertRaisesRegex(PermissionError,'no current operator-pinned'):
            self.verify(grant,authority_id='other-authority')
        changed=self.unsigned();changed['authority_scope']='proof of all route tasks'
        with self.assertRaisesRegex(ValueError,'unsupported scope'):
            self.verify(self.signed(changed))

    def test_no_native_transition_step_is_invoked(self):
        from ab_chatbot_language_bridge import PinnedEdges
        with patch.object(PinnedEdges,'step',side_effect=AssertionError('new edge forbidden')):
            verified=self.verify()
        self.assertTrue(verified['native_cached_transitions_matched'])

    def test_changed_journal_between_authority_snapshots_is_rejected(self):
        grant=self.signed()
        called=0
        def moving():
            nonlocal called
            called+=1
            if called==4:
                active=self.earlier.external.store._state()[0]
                self.earlier.external.store.revoke(scope='final',
                    confirm_key_sha256=active['final']['key_sha256'],operator='receiver')
            return self.earlier.tasks
        with self.assertRaises(ValueError):
            self.verify(grant,source_capture=moving)

    def test_source_capture_cannot_be_serialized_json(self):
        grant=self.signed()
        with self.assertRaises((ValueError,TypeError,AttributeError)):
            self.verify(grant,source_capture=lambda: {'fake':{'snapshot':True}})

    def test_unpinned_anchor_not_accepted_even_with_matching_supplied_fingerprint(self):
        raw=Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        with self.assertRaisesRegex(PermissionError,'no current operator-pinned'):
            prepare_authority_binding(**{**self.params(),
                'authority_public_key':base64.b64encode(raw).decode(),
                'anchor_fingerprint':sha256(raw).hexdigest()})

    def test_operator_revocation_revokes_previous_signed_authority_grant(self):
        grant=self.signed()
        self.anchors.revoke(authority_id='independent-policy-authority',
                            confirm_fingerprint=self.fp,operator='reviewer')
        with self.assertRaisesRegex(PermissionError,'no current operator-pinned'):
            self.verify(grant)

    def test_rotating_anchor_does_not_revalidate_historical_signature(self):
        grant=self.signed()
        self.anchors.revoke(authority_id='independent-policy-authority',
                            confirm_fingerprint=self.fp,operator='reviewer')
        new=Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        self.anchors.pin(authority_id='independent-policy-authority',
            public_key=base64.b64encode(new).decode(),confirm_fingerprint=sha256(new).hexdigest(),
            operator='reviewer',verification_reference='new-root')
        with self.assertRaisesRegex(PermissionError,'no current operator-pinned'):
            self.verify(grant)

    def test_corrupt_or_self_rewritten_anchor_history_fails_closed(self):
        grant=self.signed()
        self.anchors.path.write_bytes(self.anchors.path.read_bytes().replace(b'reviewer',b'intruder',1))
        with self.assertRaisesRegex(ValueError,'journal history'):
            self.verify(grant)

    def test_explicit_operator_anchor_confirmation_required(self):
        raw=Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        with self.assertRaises(PermissionError):
            self.anchors.pin(authority_id='new-root',public_key=base64.b64encode(raw).decode(),
                confirm_fingerprint='0'*64,operator='reviewer',verification_reference='offline')
        with self.assertRaisesRegex(ValueError,'reference'):
            self.anchors.pin(authority_id='new-root',public_key=base64.b64encode(raw).decode(),
                confirm_fingerprint=sha256(raw).hexdigest(),operator='reviewer',verification_reference='')

    def test_process_restart_or_new_pid_rejects_old_snapshot_grant(self):
        grant=self.signed()
        from systems.workspace import external_authority_binding as authority
        real_pid=authority.os.getpid()
        with patch.object(authority.os,'getpid',return_value=real_pid+1):
            with self.assertRaisesRegex(ValueError,'differs from current'):
                self.verify(grant)

    def test_authority_policy_mutation_during_verified_capture_is_rejected(self):
        grant=self.signed()
        called=0
        def moving():
            nonlocal called
            called+=1
            if called==3:
                self.anchors.revoke(authority_id='independent-policy-authority',
                                    confirm_fingerprint=self.fp,operator='reviewer')
            return self.earlier.tasks
        with self.assertRaisesRegex(ValueError,'anchor journal changed'):
            self.verify(grant,source_capture=moving)

    def test_wrong_observation_identity_never_inherits_authority(self):
        grant=self.signed()
        with self.assertRaisesRegex(ValueError,'exact previously'):
            self.verify(grant,observation_event='a'*64)

if __name__=='__main__':unittest.main()
