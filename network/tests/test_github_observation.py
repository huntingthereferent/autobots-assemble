"""Public GitHub observer: pinned branch, actual bytes, signed digests and no CP30 proof transfer."""
from __future__ import annotations

import base64
from hashlib import sha1, sha256
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from systems.workspace.external_evidence import (
    SourceEvidenceLedger, SCOPES, CLAIM_KIND, BUNDLE_KIND, _canonical, _utc,
)
from systems.workspace.github_observation import (
    observe_accepted_github_sources, _parse_locator, _file_at_commit,
)

COMMIT = "4" * 40
OTHER = "5" * 40
FILES = {"donor": b"donor observed bytes\n", "middle": b"middle observed bytes\n",
         "final": b"final observed bytes\n"}


def b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


class GitHubObservationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.store = SourceEvidenceLedger(self.root)
        self.keys = {}
        self.request = {"route":"left", "route_fingerprint":"a"*64,
            "witness_sha256":"b"*64,
            "source_digests":{s:sha256(FILES[s]).hexdigest() for s in SCOPES}}

    def enroll(self):
        for scope in SCOPES:
            key=Ed25519PrivateKey.generate(); self.keys[scope]=key
            public=key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                   format=serialization.PublicFormat.Raw)
            self.store.enroll(scope=scope,source_id="src-"+scope,
                public_key=b64(public),locator=f"https://github.com/acme-a/public-states/blob/main/{scope}.json",
                operator="authorized-operator",confirm_key_sha256=sha256(public).hexdigest())

    def accepted(self):
        self.enroll()
        issued = self.store.issue(self.request)
        signed = []
        for scope in SCOPES:
            claim={"kind":CLAIM_KIND,"scope":scope,"source_id":"src-"+scope,
                "challenge":issued["challenge"],"route":issued["route"],
                "route_fingerprint":issued["route_fingerprint"],
                "witness_sha256":issued["witness_sha256"],
                "source_sha256":issued["source_digests"][scope],
                "observed_at":_utc().isoformat()}
            signed.append({"claim":claim,"signature":b64(self.keys[scope].sign(_canonical(claim)))})
        self.store.accept(challenge=issued["challenge"],confirm_challenge=issued["challenge"],
            bundle={"kind":BUNDLE_KIND,"attestations":signed})
        return issued["challenge"]

    def provider(self, *, move_after: bool=False, mismatched_scope: str|None=None,
                 bad_git_blob:bool=False):
        calls=[]
        def fetch(resource):
            calls.append(resource)
            if resource == '/repos/acme-a/public-states/git/ref/heads/main':
                return {'object':{'sha':OTHER if move_after and len(calls)>4 else COMMIT}}
            for scope in SCOPES:
                if resource == f'/repos/acme-a/public-states/contents/{scope}.json?ref={COMMIT}':
                    content = FILES[scope]
                    if scope == mismatched_scope:
                        content = b'altered external source\n'
                    blob = sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()
                    return {'type':'file','path':f'{scope}.json',
                        'size':len(content),'encoding':'base64',
                        'content':b64(content),
                        'sha':('f'*40 if bad_git_blob else blob)}
            raise AssertionError('unexpected endpoint '+resource)
        return fetch, calls

    def run_observer(self, nonce, *, provider=None):
        api, calls = self.provider() if provider is None else provider
        with patch('systems.workspace.github_observation._github_json',side_effect=api):
            result=observe_accepted_github_sources(data_dir=self.root,
                challenge=nonce,confirm_challenge=nonce,allow_network=True)
        return result,calls

    def test_success_is_public_bytes_not_owner_or_cp30_task(self):
        nonce=self.accepted()
        result,calls=self.run_observer(nonce)
        self.assertEqual(result['status'],'PUBLIC_GITHUB_BYTES_MATCH_SIGNED_DIGESTS')
        self.assertEqual(list(result['scopes']),list(SCOPES))
        self.assertTrue(result['external_content_observed'])
        self.assertFalse(result['cp30_route_audited'])
        self.assertFalse(result['exact_task_authorized'])
        self.assertFalse(result['real_world_owners_authenticated'])
        self.assertEqual(result['scopes']['middle']['commit_sha1'],COMMIT)
        self.assertEqual(len(calls),5) # one HEAD, three files at same immutable commit, second HEAD
        self.assertEqual(self.store.status()['source_observations'],1)
        self.assertTrue(SourceEvidenceLedger(self.root).status()['external_content_observed'])
        self.assertFalse((self.root/'runtime.jsonl').exists())

    def test_required_explicit_network_flag_and_confirmation(self):
        nonce=self.accepted()
        with self.assertRaises(PermissionError):
            observe_accepted_github_sources(data_dir=self.root,challenge=nonce,
                confirm_challenge=nonce)
        with self.assertRaises(PermissionError):
            observe_accepted_github_sources(data_dir=self.root,challenge=nonce,
                confirm_challenge='wrong',allow_network=True)
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_signed_claims_required_before_observation(self):
        self.enroll()
        nonce=self.store.issue(self.request)['challenge']
        with self.assertRaisesRegex(ValueError,'already accepted'):
            self.run_observer(nonce)
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_observed_content_must_match_digest(self):
        nonce=self.accepted()
        with self.assertRaisesRegex(ValueError,'middle digest'):
            self.run_observer(nonce,provider=self.provider(mismatched_scope='middle'))
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_invalid_git_blob_digest_never_observed(self):
        nonce=self.accepted()
        with self.assertRaisesRegex(ValueError,'Git blob identifier'):
            self.run_observer(nonce,provider=self.provider(bad_git_blob=True))
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_branch_movement_fails_closed(self):
        nonce=self.accepted()
        with self.assertRaisesRegex(ValueError,'branch changed'):
            self.run_observer(nonce,provider=self.provider(move_after=True))
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_single_observation_consumes_receipt_for_observer(self):
        nonce=self.accepted(); self.run_observer(nonce)
        before=self.store.path.read_bytes()
        with self.assertRaisesRegex(ValueError,'already observed'):
            self.run_observer(nonce)
        self.assertEqual(before,self.store.path.read_bytes())

    def test_old_accepted_receipt_cannot_be_freshly_observed(self):
        nonce=self.accepted()
        with patch('systems.workspace.github_observation._now',return_value=_utc()+timedelta(minutes=11)):
            with self.assertRaisesRegex(ValueError,'too old'):
                self.run_observer(nonce)
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_revoked_enrollment_after_signed_claim_blocks_observation(self):
        nonce=self.accepted()
        old=self.store.status()['scope_enrollments']['final']['key_sha256']
        self.store.revoke(scope='final',confirm_key_sha256=old,operator='authorized-operator')
        with self.assertRaisesRegex(ValueError,'changed since'):
            self.run_observer(nonce)

    def test_untrusted_url_forms_not_accepted(self):
        for url in ('https://evil.example/x','http://github.com/acme-a/public-states/blob/main/x',
                    'https://github.com/acme-a/public-states/blob/main/../secret',
                    'https://github.com/acme-a/public-states/blob/main/x%2fy',
                    'https://github.com/acme-a/public-states/blob/main/x?token=x',
                    'https://github.com/acme-a/public-states/blob/main/x#frag',
                    'https://github.com:443/acme-a/public-states/blob/main/x',
                    'https://github.com/acme-a/public-states/blob/main//x'):
            with self.subTest(url=url),self.assertRaises(ValueError): _parse_locator(url)

    def test_malformed_file_object_and_oversized_data_rejected(self):
        raw=b'abc'; git=sha1(b'blob 3\0'+raw).hexdigest()
        with patch('systems.workspace.github_observation._github_json',return_value={
                'type':'symlink','path':'donor.json','encoding':'base64','size':3,
                'content':b64(raw),'sha':git}):
            with self.assertRaisesRegex(ValueError,'regular file'):
                _file_at_commit('acme-a','public-states','donor.json',COMMIT)
        oversized=b'a'*1_048_577
        with patch('systems.workspace.github_observation._github_json',return_value={
                'type':'file','path':'donor.json','encoding':'base64','size':len(oversized),
                'content':b64(oversized),'sha':sha1(f'blob {len(oversized)}\0'.encode()+oversized).hexdigest()}):
            with self.assertRaises(ValueError):
                _file_at_commit('acme-a','public-states','donor.json',COMMIT)

    def test_local_journal_change_during_network_call_prevents_append(self):
        nonce=self.accepted(); original,_=self.provider(); observed=False
        def moving(resource):
            nonlocal observed
            if not observed:
                observed=True
                self.store.issue(self.request)
            return original(resource)
        with self.assertRaisesRegex(ValueError,'history changed'):
            self.run_observer(nonce,provider=(moving,[]))
        self.assertEqual(self.store.status()['source_observations'],0)

    def test_partial_append_or_corrupt_event_is_not_treated_as_observed(self):
        nonce=self.accepted(); self.run_observer(nonce)
        p=self.store.path
        p.write_bytes(p.read_bytes().replace(b'public-states',b'other--state',1))
        with self.assertRaisesRegex(ValueError,'history invalid'):
            self.store.status()


if __name__ == '__main__':
    unittest.main()
