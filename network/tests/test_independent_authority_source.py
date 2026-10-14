"""Separate public witness publication, exact native grant replay, no external identity leap."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT=Path(os.environ.get('CP30_NATIVE_SOURCE_DIR','.')).resolve()
if ROOT.is_dir() and str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from network.tests import test_external_authority_binding as previous_authority_tests
from systems.workspace.external_evidence import _canonical
from systems.workspace.github_observation import _parse_locator
from systems.workspace.independent_authority_source import (
    IndependentWitnessLedger,verify_published_authority,KIND,
)
from systems.workspace import independent_authority_source as subject


@unittest.skipUnless((ROOT/'test_ab_chatbot_route_bound_task.py').is_file(),
                     'CP30_NATIVE_SOURCE_DIR must point to reconstructed native CP30')
class IndependentAuthoritySourceTests(unittest.TestCase):
    def setUp(self):
        earlier=previous_authority_tests.ExternalAuthorityBindingTests('test_pinned_external_authority_can_attest_exact_six_snapshots_without_native_upgrade')
        earlier.setUp();self.addCleanup(earlier.doCleanups)
        self.earlier=earlier
        self.grant=earlier.signed()
        self.witness_key=Ed25519PrivateKey.generate()
        raw=self.witness_key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                        format=serialization.PublicFormat.Raw)
        self.witness_public=base64.b64encode(raw).decode('ascii')
        self.fp=sha256(raw).hexdigest()
        self.data=earlier.earlier.external.data
        self.ledger=IndependentWitnessLedger(self.data)
        self.pin()
        self.commit='a'*40
        self._make_publication()
        active=earlier.earlier.external.store._state()[0]
        self.source_pairs=sorted({_parse_locator(e['locator'])[:2] for e in active.values()})
        self.source_repo_ids={v:idx+201 for idx,v in enumerate(self.source_pairs)}
        self.source_owner_ids={v:idx+301 for idx,v in enumerate(self.source_pairs)}
        self.moved=False
        self.change_identity=False
        self.same_owner_account=False
        self.invalid_blob=False
        self.on_second=False
        self.calls=0

    def pin(self,**changes):
        p=dict(witness_id='outside-reviewer',owner='separate-reviewer',repo='authority-documents',
               branch='main',path='statements/authority.json',repo_id=801,owner_account_id=901,
               public_key=self.witness_public,confirm_fingerprint=self.fp,
               operator='test-reviewer',verification_reference='out-of-band synthetic-publication-test')
        return self.ledger.pin(**{**p,**changes})

    def _make_publication(self,**changes):
        g=self.grant['statement']
        now=datetime.now(timezone.utc)
        end=datetime.fromisoformat(g['expires_at'])
        statement=dict(kind=KIND,witness_id='outside-reviewer',authority_id=g['authority_id'],
                       authority_key_sha256=g['authority_key_sha256'],
                       grant_sha256=sha256(_canonical(self.grant)).hexdigest(),
                       observation_event=g['observation_event'],
                       native_evidence_sha256=g['native_evidence_sha256'],
                       native_process_identity_sha256=g['native_process_identity_sha256'],
                       review_reference='fixture-review-001',review_method='independent-document-review',
                       issued_at=now.isoformat(),expires_at=min(end,now+timedelta(seconds=80)).isoformat())
        statement.update(changes)
        self.statement=statement
        signature=base64.b64encode(self.witness_key.sign(_canonical(statement))).decode('ascii')
        self.publication={'statement':statement,'signature':signature}

    def api(self, resource):
        self.calls+=1
        if resource.startswith('/repos/') and resource.count('/')==3:
            _,r,owner,repo=resource.split('/')
            if owner=='separate-reviewer' and repo=='authority-documents':
                return {'id':802 if self.change_identity else 801,'full_name':f'{owner}/{repo}',
                        'private':False,'owner':{'id':901,'login':owner}}
            pair=(owner,repo)
            if pair in self.source_repo_ids:
                return {'id':self.source_repo_ids[pair],'full_name':f'{owner}/{repo}',
                        'private':False,'owner':{'id':901 if self.same_owner_account else self.source_owner_ids[pair],
                                                 'login':owner}}
        if resource=='/repos/separate-reviewer/authority-documents/git/ref/heads/main':
            self.on_second=True if self.calls>5 else self.on_second
            return {'object':{'type':'commit','sha':'b'*40 if self.moved and self.on_second else self.commit}}
        if resource==f'/repos/separate-reviewer/authority-documents/contents/statements/authority.json?ref={self.commit}':
            raw=_canonical(self.publication)
            blob=sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            return {'type':'file','path':'statements/authority.json','encoding':'base64',
                    'content':base64.b64encode(raw).decode('ascii'),'size':len(raw),
                    'sha':'f'*40 if self.invalid_blob else blob}
        raise AssertionError('Unexpected mocked GitHub API resource '+resource)

    def run_verify(self,**changes):
        native=self.earlier.params();native.pop('data_dir')
        kwargs=dict(data_dir=self.data,witness_id='outside-reviewer',
                    signed_grant=self.grant,native_binding=native,
                    allow_network=True,confirm_grant_sha256=sha256(_canonical(self.grant)).hexdigest())
        with patch.object(subject,'_github_json',side_effect=self.api):
            return verify_published_authority(**{**kwargs,**changes})

    def test_separate_witness_publication_rechecks_original_live_native_grant(self):
        before=(self.earlier.earlier.external.store.path.read_bytes(),
                self.earlier.anchors.path.read_bytes(),self.ledger.path.read_bytes())
        done=self.run_verify()
        self.assertEqual(done['status'],'SEPARATE_GITHUB_WITNESS_PUBLICATION_VERIFIED')
        self.assertEqual(done['witness_repo_id'],801)
        self.assertTrue(done['exact_signed_grant_revalidated'])
        for flag in ('independent_organization_authenticated','legal_ownership_proved',
                     'real_world_identity_proved','cp30_fresh_route_audit',
                     'exact_cp30_task_authorized','native_handoff_admitted','journal_modified'):
            self.assertFalse(done[flag],flag)
        self.assertEqual(before,(self.earlier.earlier.external.store.path.read_bytes(),
                                self.earlier.anchors.path.read_bytes(),self.ledger.path.read_bytes()))
        self.assertFalse((self.data/'runtime.jsonl').exists())

    def test_network_is_explicit_and_exact_digest_confirmed(self):
        with self.assertRaises(PermissionError):self.run_verify(allow_network=False)
        with self.assertRaises(PermissionError):self.run_verify(confirm_grant_sha256='a'*64)
        self.assertEqual(self.calls,0)

    def test_wrong_publication_signature_rejected(self):
        self.publication['signature']=base64.b64encode(Ed25519PrivateKey.generate().sign(_canonical(self.statement))).decode()
        with self.assertRaisesRegex(ValueError,'signature unproved'):self.run_verify()

    def test_witness_cannot_publish_different_native_evidence(self):
        self._make_publication(native_evidence_sha256='f'*64)
        with self.assertRaisesRegex(ValueError,'does not bind exact'):self.run_verify()

    def test_witness_cannot_publish_another_authority_key(self):
        self._make_publication(authority_key_sha256='b'*64)
        with self.assertRaisesRegex(ValueError,'does not bind exact'):self.run_verify()

    def test_malformed_or_extra_publication_claim_rejected(self):
        self._make_publication(legal_owner_proved=True)
        with self.assertRaisesRegex(ValueError,'invalid independent publication'):self.run_verify()

    def test_witness_pub_repo_identity_substitution_rejected(self):
        self.change_identity=True
        with self.assertRaisesRegex(ValueError,'repository identity'):self.run_verify()

    def test_witness_owner_is_not_independent_by_login_alone(self):
        self.same_owner_account=True
        with self.assertRaisesRegex(ValueError,'same GitHub account ID'):self.run_verify()

    def test_changed_github_branch_after_read_rejected(self):
        self.moved=True
        with self.assertRaisesRegex(ValueError,'changed during'):self.run_verify()

    def test_github_file_blob_integrity_rechecked(self):
        self.invalid_blob=True
        with self.assertRaisesRegex(ValueError,'blob content mismatch'):self.run_verify()

    def test_witness_revocation_invalidates_publication(self):
        self.ledger.revoke(witness_id='outside-reviewer',confirm_fingerprint=self.fp,operator='test-reviewer')
        with self.assertRaises(PermissionError):self.run_verify()

    def test_witness_key_rotation_does_not_borrow_old_signature(self):
        self.ledger.revoke(witness_id='outside-reviewer',confirm_fingerprint=self.fp,operator='test-reviewer')
        new=Ed25519PrivateKey.generate().public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                                    format=serialization.PublicFormat.Raw)
        self.pin(public_key=base64.b64encode(new).decode(),confirm_fingerprint=sha256(new).hexdigest())
        with self.assertRaisesRegex(ValueError,'signature unproved'):self.run_verify()

    def test_native_source_revocation_blocks_even_valid_external_publication(self):
        pin=self.earlier.earlier.left.first.recipient
        pin.registry.revoke(pin._base._tokens[0])
        with self.assertRaisesRegex(ValueError,'pin is revoked'):self.run_verify()

    def test_authority_rotation_invalidates_valid_external_publication(self):
        self.earlier.anchors.revoke(authority_id='independent-policy-authority',
                                    confirm_fingerprint=self.earlier.fp,operator='test-reviewer')
        with self.assertRaises(PermissionError):self.run_verify()

    def test_witness_stale_expired_publication_rejected(self):
        ago=datetime.now(timezone.utc)-timedelta(minutes=2)
        self._make_publication(issued_at=ago.isoformat(),expires_at=(ago+timedelta(seconds=60)).isoformat())
        with self.assertRaisesRegex(ValueError,'expired|within original'):self.run_verify()

    def test_witness_invalid_claimed_review_method_rejected(self):
        self._make_publication(review_method='court-order-proven')
        with self.assertRaisesRegex(ValueError,'review method'):self.run_verify()

    def test_witness_journal_modification_detected_during_network(self):
        old=self.api
        def mutate(resource):
            if resource.startswith('/repos/separate-reviewer/authority-documents/contents/'):
                self.ledger.revoke(witness_id='outside-reviewer',confirm_fingerprint=self.fp,operator='test-reviewer')
            return old(resource)
        with patch.object(subject,'_github_json',side_effect=mutate):
            with self.assertRaisesRegex(ValueError,'changed during'): 
                native=self.earlier.params();native.pop('data_dir')
                verify_published_authority(data_dir=self.data,witness_id='outside-reviewer',
                    signed_grant=self.grant,native_binding=native,allow_network=True,
                    confirm_grant_sha256=sha256(_canonical(self.grant)).hexdigest())

    def test_no_new_native_transitions_requested(self):
        from ab_chatbot_language_bridge import PinnedEdges
        with patch.object(PinnedEdges,'step',side_effect=AssertionError('new transition forbidden')):
            self.assertTrue(self.run_verify()['live_native_snapshot_revalidated'])

    def test_replaced_live_native_task_detected(self):
        native=self.earlier.params();native.pop('data_dir')
        native['source_capture']=lambda: {**self.earlier.earlier.tasks,
                 'admitted':self.earlier.earlier.helper.task(self.earlier.earlier.refresh,'left',
                                 required_edges=[{'state':[1,0,0],'action':'B'}])}
        with self.assertRaisesRegex(ValueError,'differs from current|changed during external binding'):
            self.run_verify(native_binding=native)

    def test_receiver_will_not_accept_arbitrary_native_verdict_callback(self):
        with self.assertRaisesRegex(ValueError,'exact native authority verification parameters'):
            self.run_verify(native_binding={'return_fake_result':lambda:{'status':'OPERATOR_ANCHORED_SNAPSHOT_DELEGATION_VERIFIED'}})

    def test_revoked_source_signer_blocks_even_valid_publication(self):
        state=self.earlier.earlier.external.store._state()[0]
        self.earlier.earlier.external.store.revoke(
            scope='donor',confirm_key_sha256=state['donor']['key_sha256'],operator='receiver')
        with self.assertRaisesRegex(ValueError,'missing enrolled signed source'):
            self.run_verify()

    def test_private_witness_repository_is_not_public_evidence(self):
        original=self.api
        def swapped(resource):
            response=original(resource)
            if resource=='/repos/separate-reviewer/authority-documents':
                response={**response,'private':True}
            return response
        with patch.object(subject,'_github_json',side_effect=swapped):
            native=self.earlier.params();native.pop('data_dir')
            with self.assertRaisesRegex(ValueError,'repository identity unverified'):
                verify_published_authority(data_dir=self.data,witness_id='outside-reviewer',
                    signed_grant=self.grant,native_binding=native,allow_network=True,
                    confirm_grant_sha256=sha256(_canonical(self.grant)).hexdigest())

    def test_signed_publication_outside_grant_window_rejected(self):
        end=datetime.fromisoformat(self.grant['statement']['expires_at'])
        self._make_publication(expires_at=(end+timedelta(seconds=1)).isoformat())
        with self.assertRaisesRegex(ValueError,'within original authority grant'):
            self.run_verify()

    def test_noncommit_git_reference_rejected(self):
        original=self.api
        def tagged(resource):
            response=original(resource)
            if resource=='/repos/separate-reviewer/authority-documents/git/ref/heads/main':
                response={'object':{'type':'tag','sha':self.commit}}
            return response
        with patch.object(subject,'_github_json',side_effect=tagged):
            native=self.earlier.params();native.pop('data_dir')
            with self.assertRaisesRegex(ValueError,'branch head invalid'):
                verify_published_authority(data_dir=self.data,witness_id='outside-reviewer',
                    signed_grant=self.grant,native_binding=native,allow_network=True,
                    confirm_grant_sha256=sha256(_canonical(self.grant)).hexdigest())

    def test_corrupt_witness_history_rejected(self):
        self.ledger.path.write_text(self.ledger.path.read_text().replace('test-reviewer','hacker',1))
        with self.assertRaisesRegex(ValueError,'invalid witness policy chain'):self.run_verify()

if __name__=='__main__':unittest.main()
