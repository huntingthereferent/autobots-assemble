"""Read-only live public-source preflight. No real owners are enrolled in tests."""
from __future__ import annotations

from hashlib import sha256,sha1
from datetime import datetime,timedelta,timezone
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch,Mock

from network.tests import test_github_observation as fixture_tests
FILES, COMMIT = fixture_tests.FILES, fixture_tests.COMMIT
from systems.workspace.external_evidence import SCOPES, SourceEvidenceLedger
from systems.workspace.source_origin_authority import SourceOriginPolicy
from systems.workspace.live_source_preflight import readiness, probe_enrolled_public_sources, main
from systems.workspace import live_source_preflight as pf


class PreflightTests(unittest.TestCase):
    def test_absent_credentials_remain_blocked_read_only(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            report=readiness(root)
            self.assertEqual(report['status'],'BLOCKED')
            self.assertEqual(len(report['missing']),7)
            self.assertFalse(report['network_observed'])
            self.assertFalse(report['owner_identity_authenticated'])
            self.assertEqual(list(root.iterdir()),[])
            with self.assertRaises(PermissionError):
                probe_enrolled_public_sources(data_dir=root,challenge='x',confirm_challenge='x')
            self.assertEqual(list(root.iterdir()),[])

    def setUp(self):
        f=fixture_tests.GitHubObservationTests('test_success_is_public_bytes_not_owner_or_cp30_task')
        f.setUp();self.addCleanup(f.doCleanups)
        self.fixture=f
        self.nonce=f.accepted()
        self.root=f.root
        self.policy=SourceOriginPolicy(self.root)
        keys=f.store._state()[0]
        for scope in SCOPES:
            k=keys[scope]
            self.policy.pin(scope=scope,source_id=k['source_id'],locator=k['locator'],
                            repo_id=501,owner_account_id=601,key_sha256=k['key_sha256'],
                            operator='operator',verification_reference='test-only-out-of-band-review')
        self.keys=keys
        self.responses=[]
        self.moved=False
        self.changed_scope=None
        self.pinned_mismatch=False
        self.policy_changed=False

    def patched(self):
        def head(owner,repo,branch):
            self.responses.append('head')
            return '5'*40 if self.moved and self.responses.count('head')>=2 else COMMIT
        def fil(owner,repo,name,commit):
            self.responses.append('file:'+name)
            scope=name.replace('.json','')
            raw=FILES[scope]
            if scope==self.changed_scope:raw+=b'\n'
            if self.policy_changed and scope=='final':
                self.policy.revoke(scope='middle',source_id=self.keys['middle']['source_id'],
                        key_sha256=self.keys['middle']['key_sha256'],operator='operator')
            return {'sha256':sha256(raw).hexdigest(),'size':len(raw),
                    'git_blob_sha1':sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}
        def public(owner,repo):
            self.responses.append('identity')
            return {'repo_id':999 if self.pinned_mismatch else 501,'owner_account_id':601}
        return patch.multiple(pf,_checked_public_repo=public,_head=head,_file_at_commit=fil)

    def probe(self,**changes):
        opts=dict(data_dir=self.root,challenge=self.nonce,
                  confirm_challenge=self.nonce,allow_network=True)
        with self.patched(),patch.object(pf.AuthorityAnchorLedger,'current',return_value={'a':{}}),\
                patch.object(pf.IndependentWitnessLedger,'current',return_value={'w':{}}):
            return probe_enrolled_public_sources(**{**opts,**changes})

    def test_probe_matches_all_scopes_without_journal_write(self):
        original=(self.fixture.store.path.read_bytes(),self.policy.path.read_bytes())
        report=self.probe()
        self.assertEqual(report['status'],'LIVE_PUBLIC_BYTES_MATCH_PRIOR_SIGNED_CLAIMS')
        self.assertEqual(set(report['scopes']),set(SCOPES))
        self.assertEqual(report['scopes']['donor']['repository_id'],501)
        self.assertEqual(self.responses,['identity','head','file:donor.json',
                         'file:middle.json','file:final.json','head'])
        self.assertEqual((self.fixture.store.path.read_bytes(),self.policy.path.read_bytes()),original)
        for field in ('recorded','journal_written','owner_identity_authenticated',
                      'cp30_route_audited','task_authorized'):
            self.assertFalse(report[field])
        self.assertFalse((self.root/'runtime.jsonl').exists())

    def test_exact_network_consent_and_challenge_required(self):
        for arg in ({'allow_network':False},{'confirm_challenge':'different'}):
            with self.subTest(arg=arg),self.assertRaises(PermissionError): self.probe(**arg)
        self.assertEqual(self.responses,[])

    def test_expired_original_challenge_refuses_preflight_even_if_receipt_recent(self):
        issued=self.fixture.store._state()[1][self.nonce]
        old=datetime.fromisoformat(issued['issued_at'])
        with patch.object(pf,'_clock_utc',return_value=old+timedelta(seconds=issued['ttl_seconds']+1)):
            with self.assertRaisesRegex(ValueError,'challenge expired'):self.probe()
        self.assertEqual(self.responses,[])

    def test_challenge_expires_mid_network_probe(self):
        issued=self.fixture.store._state()[1][self.nonce]
        old=datetime.fromisoformat(issued['issued_at'])
        with patch.object(pf,'_clock_utc',side_effect=[old+timedelta(seconds=1),old+timedelta(seconds=issued['ttl_seconds']+1)]):
            with self.assertRaisesRegex(ValueError,'challenge expired'):self.probe()
        self.assertIn('file:final.json',self.responses)
        self.assertFalse((self.root/'runtime.jsonl').exists())

    def test_unpinned_or_replaced_source_refuses_network(self):
        self.policy.revoke(scope='middle',source_id=self.keys['middle']['source_id'],
                           key_sha256=self.keys['middle']['key_sha256'],operator='operator')
        with self.assertRaises(PermissionError):self.probe()
        self.assertEqual(self.responses,[])

    def test_public_id_not_equal_to_policy_is_rejected(self):
        self.pinned_mismatch=True
        with self.assertRaisesRegex(ValueError,'immutable identity'):self.probe()
        self.assertEqual(self.responses,['identity'])

    def test_file_changed_after_signature_rejected(self):
        self.changed_scope='final'
        with self.assertRaisesRegex(ValueError,'differs from signed final'):self.probe()
        self.assertNotIn('head',self.responses[-1:])

    def test_branch_move_after_read_rejected(self):
        self.moved=True
        with self.assertRaisesRegex(ValueError,'branch moved'):self.probe()

    def test_enrollment_revocation_refuses_network(self):
        self.fixture.store.revoke(scope='donor',confirm_key_sha256=self.keys['donor']['key_sha256'],operator='operator')
        with self.assertRaises(ValueError):self.probe()
        self.assertEqual(self.responses,[])

    def test_policy_changed_while_network_read_is_rejected(self):
        self.policy_changed=True
        with self.assertRaisesRegex(ValueError,'policy changed'):self.probe()

    def test_corrupted_policy_is_rejected_not_silently_ignored(self):
        with self.policy.path.open('a') as stream: stream.write('broken\n')
        with self.assertRaises(ValueError):readiness(self.root)
        with self.assertRaises(ValueError):self.probe()
        self.assertEqual(self.responses,[])

    def test_no_public_source_claim_when_anchor_or_witness_missing(self):
        with self.patched():
            with self.assertRaises(PermissionError):
                probe_enrolled_public_sources(data_dir=self.root,challenge=self.nonce,
                    confirm_challenge=self.nonce,allow_network=True)
        self.assertEqual(self.responses,[])

    def test_readiness_never_labels_pins_as_authenticated(self):
        result=readiness(self.root)
        self.assertEqual(result['status'],'BLOCKED') # no real witness/authority anchor yet
        self.assertTrue(all(x['enrollment_matches_repo_policy'] for x in result['scope_status'].values()))
        self.assertFalse(result['owner_identity_authenticated'])

if __name__=='__main__':unittest.main()
