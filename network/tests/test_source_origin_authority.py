"""Source-repository countersignature is checkable publication, not legal identity."""
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

ROOT=Path(os.environ.get('CP30_NATIVE_SOURCE_DIR','.')).resolve()
if ROOT.is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from network.tests import test_independent_authority_source as previous_tests
from systems.workspace.external_evidence import SCOPES,_canonical
from systems.workspace.source_origin_authority import (
    SourceOriginPolicy,verify_source_origin_authorizations,KIND,STATUS,_authorization_path
)
from systems.workspace import source_origin_authority as origin
from systems.workspace import independent_authority_source as witness
from systems.workspace import github_observation as gh
from systems.workspace import external_source_continuity as lineage


@unittest.skipUnless((ROOT/'test_ab_chatbot_route_bound_task.py').is_file(),
                     'CP30_NATIVE_SOURCE_DIR must point to reconstructed CP30 source')
class SourceOriginAuthorityTests(unittest.TestCase):
    def setUp(self):
        previous=previous_tests.IndependentAuthoritySourceTests('test_separate_witness_publication_rechecks_original_live_native_grant')
        previous.setUp();self.addCleanup(previous.doCleanups)
        self.previous=previous
        self.store=previous.earlier.earlier.external.store
        self.data=previous.data
        self.policy=SourceOriginPolicy(self.data)
        self.active=self.store._state()[0]
        for scope in SCOPES:
            p=self.active[scope]
            self.policy.pin(scope=scope,source_id=p['source_id'],locator=p['locator'],
                key_sha256=p['key_sha256'],repo_id=201,owner_account_id=301,
                operator='receiver',verification_reference='fixture-out-of-band-ids')
        self.source_head='6'*40
        self.moved=False;self.changed_original=False;self.changed_id=False
        self.wrong_signature=False;self.wrong_witness=False;self.expires=False
        self.wrong_source_id=False;self.wrong_digest=False;self.add_scope=False
        self.change_policy=False
        self._publications()
        self.calls=[]

    def _publications(self):
        p=self.previous
        grant=p.grant['statement']
        now=datetime.now(timezone.utc)
        expires=datetime.fromisoformat(grant['expires_at'])
        self.pubs={}
        for scope in SCOPES:
            enrol=self.active[scope]
            obs=p.earlier.earlier.external.observation['scopes'][scope]
            statement={
                'kind':KIND,'scope':scope,'source_id':enrol['source_id'],
                'source_locator':enrol['locator'],'source_key_sha256':enrol['key_sha256'],
                'source_repo_id':201,'source_owner_account_id':301,
                'source_observed_commit':obs['commit_sha1'],
                'source_observed_sha256':obs['sha256'],
                'authority_grant_sha256':sha256(_canonical(p.grant)).hexdigest(),
                'witness_id':'outside-reviewer',
                'witness_publication_commit':p.commit,
                'witness_publication_sha256':sha256(_canonical(p.publication)).hexdigest(),
                'observation_event':grant['observation_event'],
                'native_evidence_sha256':grant['native_evidence_sha256'],
                'authorization_scope':'external-evidence-corroboration-only',
                'issued_at':now.isoformat(),
                'expires_at':min(expires,now+timedelta(seconds=75)).isoformat(),
            }
            signer=p.earlier.earlier.external.secret[scope]
            self.pubs[scope]={'statement':statement,
                'signature':base64.b64encode(signer.sign(_canonical(statement))).decode('ascii')}

    def _api(self,resource):
        self.calls.append(resource)
        if resource.startswith('/repos/separate-reviewer/'):
            return self.previous.api(resource)
        if resource=='/repos/demo-owner/route-fixtures':
            return {'id':202 if self.changed_id else 201,'full_name':'demo-owner/route-fixtures',
                    'private':False,'owner':{'id':301,'login':'demo-owner'}}
        if resource=='/repos/demo-owner/route-fixtures/git/ref/heads/main':
            return {'object':{'type':'commit','sha':'7'*40 if self.moved and len(self.calls)>9 else self.source_head}}
        if resource==f'/repos/demo-owner/route-fixtures/compare/{"4"*40}...{self.source_head}':
            return {'status':'ahead','ahead_by':1,'behind_by':0,
                    'base_commit':{'sha':'4'*40},'merge_base_commit':{'sha':'4'*40},
                    'commits':[{'sha':self.source_head}]}
        for scope in SCOPES:
            path=_authorization_path(scope)
            if resource==f'/repos/demo-owner/route-fixtures/contents/{path}?ref={self.source_head}':
                document=dict(self.pubs[scope])
                if self.wrong_signature and scope=='middle':
                    document['signature']=base64.b64encode(b'x'*64).decode('ascii')
                raw=_canonical(document)
                return {'type':'file','path':path,'encoding':'base64','size':len(raw),
                        'content':base64.b64encode(raw).decode('ascii'),
                        'sha':sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}
            original=f'{scope}.json'
            if resource==f'/repos/demo-owner/route-fixtures/contents/{original}?ref={self.source_head}':
                raw=self.previous.earlier.earlier.external.bytes[scope]
                if self.changed_original and scope=='final':raw+=b'\n'
                return {'type':'file','path':original,'encoding':'base64','size':len(raw),
                        'content':base64.b64encode(raw).decode('ascii'),
                        'sha':sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}
        return self.previous.api(resource)

    def verify(self,**overrides):
        p=self.previous
        params=p.earlier.params();params.pop('data_dir')
        options={'data_dir':self.data,'signed_grant':p.grant,'native_binding':params,
            'witness_id':'outside-reviewer','confirm_grant_sha256':sha256(_canonical(p.grant)).hexdigest(),
            'confirm_observation_event':p.grant['statement']['observation_event'],
            'allow_network':True}
        # Each module has an intentionally separate production GitHub GET entry.
        with patch.object(witness,'_github_json',side_effect=self._api), \
             patch.object(origin,'_checked_public_repo',side_effect=lambda o,r: witness._checked_public_repo(o,r)), \
             patch.object(origin,'_head',side_effect=lambda o,r,b:witness._head(o,r,b)), \
             patch.object(origin,'_witness_file',side_effect=lambda o,r,path,ref:witness._witness_file(o,r,path,ref)), \
             patch.object(gh,'_github_json',side_effect=self._api), \
             patch.object(lineage,'_github_json',side_effect=self._api):
            return verify_source_origin_authorizations(**{**options,**overrides})

    def test_three_current_source_keys_countersign_exact_witness_and_grant(self):
        before=(self.store.path.read_bytes(),self.policy.path.read_bytes())
        result=self.verify()
        self.assertEqual(result['status'],STATUS)
        self.assertEqual(set(result['source_origin_publications']),set(SCOPES))
        self.assertTrue(result['native_snapshot_authority_reverified'])
        self.assertEqual(result['review_receipt_sha256'],
                         sha256(_canonical(result['review_receipt'])).hexdigest())
        self.assertFalse(result['review_receipt']['native_cp30_task_authorized'])
        self.assertIn('/blob/',result['source_origin_publications']['donor']['authorization_url'])
        for key in ('real_world_owner_identity_proved','legal_authority_proved',
                    'github_account_control_is_legal_authority','cp30_fresh_route_audit',
                    'exact_task_authorized','native_handoff_admitted','new_transitions_observed',
                    'journal_modified'):
            self.assertFalse(result[key])
        self.assertEqual(before,(self.store.path.read_bytes(),self.policy.path.read_bytes()))
        self.assertFalse((self.data/'runtime.jsonl').exists())

    def test_explicit_network_grant_and_observation_confirmation_required(self):
        for kwargs in ({'allow_network':False},{'confirm_grant_sha256':'a'*64},
                       {'confirm_observation_event':'f'*64}):
            with self.subTest(kwargs=kwargs),self.assertRaises(PermissionError):self.verify(**kwargs)
        self.assertEqual(self.calls,[])

    def test_all_three_source_origins_must_be_pinned(self):
        self.policy.revoke(scope='middle',source_id='src-middle',
                           key_sha256=self.active['middle']['key_sha256'],operator='receiver')
        with self.assertRaises(PermissionError):self.verify()
        self.assertEqual(self.calls,[])

    def test_source_origin_cannot_be_pinned_without_existing_source_key(self):
        with self.assertRaises(PermissionError):
            SourceOriginPolicy(self.data).pin(scope='donor',source_id='wrong',
                locator=self.active['donor']['locator'],key_sha256=self.active['donor']['key_sha256'],
                repo_id=201,owner_account_id=301,operator='receiver',verification_reference='case')

    def test_key_mismatch_is_rejected_even_with_valid_git_blob(self):
        self.wrong_signature=True
        with self.assertRaisesRegex(ValueError,'countersignature'):self.verify()

    def test_changed_source_bytes_are_rejected_despite_same_delegation(self):
        self.changed_original=True
        with self.assertRaisesRegex(ValueError,'file changed'):self.verify()

    def test_repository_immutable_id_mismatch(self):
        self.changed_id=True
        with self.assertRaisesRegex(ValueError,'identity differs'):self.verify()

    def test_unexpected_native_observation_digest_cannot_be_authorized(self):
        self.pubs['final']['statement']['source_observed_sha256']='a'*64
        with self.assertRaisesRegex(ValueError,'does not bind exact'):self.verify()

    def test_source_published_wrong_witness_commit_does_not_transfer(self):
        self.pubs['donor']['statement']['witness_publication_commit']='0'*40
        with self.assertRaisesRegex(ValueError,'does not bind exact'):self.verify()

    def test_scope_cannot_claim_cp30_route_proof(self):
        self.pubs['donor']['statement']['authorization_scope']='all-cp30-tasks'
        with self.assertRaisesRegex(ValueError,'does not bind exact'):self.verify()

    def test_source_revocation_blocks_fresh_check(self):
        self.store.revoke(scope='middle',confirm_key_sha256=self.active['middle']['key_sha256'],operator='receiver')
        with self.assertRaisesRegex(PermissionError,'source origin enrollment'):self.verify()

    def test_authority_revocation_blocks_original_grant(self):
        grant=self.previous.grant['statement']
        self.previous.earlier.anchors.revoke(authority_id=grant['authority_id'],
                    confirm_fingerprint=grant['authority_key_sha256'],operator='receiver')
        with self.assertRaises((ValueError,PermissionError)):self.verify()

    def test_cannot_silently_change_source_branch_after_observation(self):
        self.moved=True
        with self.assertRaisesRegex(ValueError,'branch moved'):self.verify()

    def test_corrupt_origin_policy_is_not_ignored(self):
        with self.policy.path.open('a') as f:f.write('invalid\n')
        with self.assertRaisesRegex(ValueError,'source origin'):self.verify()

    def test_publication_expired_or_future_is_rejected(self):
        self.pubs['donor']['statement']['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError,'stale'):self.verify()

    def test_policy_changes_mid_check_fail_closed(self):
        old=self._api
        def changing(resource):
            if resource==f'/repos/demo-owner/route-fixtures/contents/{_authorization_path("final")}?ref={self.source_head}':
                self.policy.revoke(scope='middle',source_id='src-middle',
                    key_sha256=self.active['middle']['key_sha256'],operator='receiver')
            return old(resource)
        self._api=changing
        with self.assertRaisesRegex(ValueError,'polic|journal|changed'):self.verify()

if __name__=='__main__':unittest.main()
