"""Independently runnable CP-30 signature/nonce verification tests."""
import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from finite_process_attestation import (
    SCOPES, generate_fixture_keys, make_claims, sign_scopes, verify_scopes,
    raw_b64, canonical,
)

NONCE='ab'*24
FINGERPRINT='12'*32
WITNESS='34'*32
DIGESTS={'donor':'56'*32,'middle':'78'*32,'final':'9a'*32}

class ProcessAttestationTests(unittest.TestCase):
    def setUp(self):
        self.secret,self.trust=generate_fixture_keys()
        self.claims=make_claims(challenge=NONCE,route='left',fingerprint=FINGERPRINT,
                                witness=WITNESS,source_digests=DIGESTS)
        self.bundle=sign_scopes(self.claims,self.secret)
        self.expected={'challenge':NONCE,'route':'left','fingerprint':FINGERPRINT,
                       'witness':WITNESS,'source_digests':DIGESTS}
    def verify(self,bundle=None,trust=None,**update):
        return verify_scopes(self.bundle if bundle is None else bundle,
            self.trust if trust is None else trust,**{**self.expected,**update})
    def test_three_distinct_signing_keys(self):
        self.assertEqual(len(set(self.trust.values())),3)
        self.assertEqual(self.verify().verified_scopes,SCOPES)
    def test_receipt_has_no_private_material(self):
        raw=canonical(self.bundle).decode()
        self.assertTrue(all(key not in raw for key in self.secret.values()))
    def test_wrong_challenge(self):
        self.assertEqual(self.verify(challenge='cd'*24).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_wrong_route(self):
        self.assertEqual(self.verify(route='right').status,'ATTESTATION_CLAIM_MISMATCH')
    def test_wrong_witness(self):
        self.assertEqual(self.verify(witness='00'*32).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_wrong_fingerprint(self):
        self.assertEqual(self.verify(fingerprint='00'*32).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_wrong_one_scope_digest(self):
        other=dict(DIGESTS);other['middle']='00'*32
        self.assertEqual(self.verify(source_digests=other).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_wrong_pretrusted_key(self):
        _,other=generate_fixture_keys()
        trust=dict(self.trust);trust['middle']=other['middle']
        self.assertEqual(self.verify(trust=trust).status,'ATTESTATION_SIGNATURE_UNPROVED')
    def test_signature_tamper(self):
        wire=copy.deepcopy(self.bundle)
        wire['attestations'][0]['signature']=raw_b64(b'\x00'*64)
        self.assertEqual(self.verify(bundle=wire).status,'ATTESTATION_SIGNATURE_UNPROVED')
    def test_claim_tamper(self):
        wire=copy.deepcopy(self.bundle)
        wire['attestations'][0]['claim']['source_sha256']='ff'*32
        self.assertEqual(self.verify(bundle=wire).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_scope_swapped(self):
        wire=copy.deepcopy(self.bundle)
        wire['attestations'][0],wire['attestations'][1]=wire['attestations'][1],wire['attestations'][0]
        self.assertEqual(self.verify(bundle=wire).status,'ATTESTATION_CLAIM_MISMATCH')
    def test_missing_signature(self):
        wire=copy.deepcopy(self.bundle);wire['attestations'].pop()
        self.assertEqual(self.verify(bundle=wire).status,'ATTESTATION_MALFORMED')
    def test_missing_trust(self):
        trust=dict(self.trust);del trust['donor']
        self.assertEqual(self.verify(trust=trust).status,'ATTESTATION_TRUST_MISSING')
    def test_extraneous_signature_field(self):
        wire=copy.deepcopy(self.bundle);wire['attestations'][0]['untrusted']=1
        self.assertEqual(self.verify(bundle=wire).status,'ATTESTATION_MALFORMED')
    def test_bad_nonce_format_is_invalid_expectation(self):
        self.assertEqual(self.verify(challenge='abc').status,'ATTESTATION_INVALID_EXPECTATION')
    def test_actual_separate_signer_and_verifier_pids(self):
        script=str(Path(__file__).with_name('finite_process_attestation.py'))
        def run(mode,request):
            p=subprocess.run([sys.executable,script,mode],input=json.dumps(request),
                             text=True,capture_output=True,check=True,timeout=15)
            self.assertFalse(p.stderr)
            return json.loads(p.stdout)
        signed=run('sign',{'claims':self.claims,'private_keys':self.secret})
        self.assertEqual(signed['status'],'ATTESTATIONS_SIGNED')
        checked=run('verify',{'bundle':signed['bundle'],'trust':self.trust,
                              'expect':self.expected})
        self.assertEqual(checked['status'],'ATTESTATIONS_VERIFIED')
        self.assertNotEqual(signed['pid'],os.getpid())
        self.assertNotEqual(checked['pid'],os.getpid())
        self.assertNotEqual(signed['pid'],checked['pid'])
    def test_receiver_key_not_sourced_from_bundle(self):
        swapped=dict(self.trust)
        swapped['donor']=swapped['middle']
        self.assertEqual(self.verify(trust=swapped).status,'ATTESTATION_SIGNATURE_UNPROVED')

if __name__=='__main__':unittest.main()
