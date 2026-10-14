"""Operator-pinned external signature boundaries: no synthetic CP30 proof transfer."""
from __future__ import annotations

from datetime import timedelta
import base64
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from systems.workspace.external_evidence import (
    SourceEvidenceLedger, SCOPES, _canonical, _utc, CLAIM_KIND, BUNDLE_KIND,
)

REQUEST = {"route":"left", "route_fingerprint":"a"*64,
           "witness_sha256":"b"*64, "source_digests":{
               "donor":"c"*64, "middle":"d"*64, "final":"e"*64}}


def b64(value):
    return base64.b64encode(value).decode("ascii")


class ExternalEvidenceTests(unittest.TestCase):
    def setUp(self):
        td = TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.data = Path(td.name)
        self.store = SourceEvidenceLedger(self.data)
        self.keys = {}

    def enroll_all(self):
        for scope in SCOPES:
            key = Ed25519PrivateKey.generate()
            self.keys[scope] = key
            public = key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
            self.store.enroll(scope=scope, source_id="src-"+scope, public_key=b64(public),
                locator=f"https://source.example/{scope}/record.json",
                operator="explicit-local-operator", confirm_key_sha256=sha256(public).hexdigest())

    def bundle(self, issued, *, keys=None, alter=None):
        signers = keys or self.keys
        rows = []
        for scope in SCOPES:
            claim = {"kind":CLAIM_KIND,"scope":scope,
                     "source_id":issued["pinned_keys"][scope]["source_id"],
                     "challenge":issued["challenge"],"route":issued["route"],
                     "route_fingerprint":issued["route_fingerprint"],
                     "witness_sha256":issued["witness_sha256"],
                     "source_sha256":issued["source_digests"][scope],
                     "observed_at":_utc().isoformat()}
            if alter and scope == "middle":
                claim.update(alter)
            rows.append({"claim":claim,"signature":b64(signers[scope].sign(_canonical(claim)))})
        return {"kind":BUNDLE_KIND,"attestations":rows}

    def test_no_implicit_enrollment(self):
        self.assertEqual(self.store.status()["scope_enrollments"], {})
        self.assertFalse(self.store.path.exists())
        with self.assertRaisesRegex(ValueError, "three explicitly enrolled"):
            self.store.issue(REQUEST)
        self.assertFalse(self.store.path.exists())

    def test_full_key_fingerprint_confirmation_and_explicit_https(self):
        key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
        opts = dict(scope="donor", source_id="source", public_key=b64(key), operator="operator")
        with self.assertRaises(PermissionError):
            self.store.enroll(**opts, locator="https://example.com/key", confirm_key_sha256="0"*64)
        for loc in ("http://example.com", "https://admin:pass@example.com/key", "https://example.com/x?token=abc"):
            with self.assertRaises(ValueError):
                self.store.enroll(**opts, locator=loc, confirm_key_sha256=sha256(key).hexdigest())
        self.assertFalse(self.store.path.exists())

    def test_three_signatures_are_bound_to_fresh_receiver_nonce(self):
        self.enroll_all()
        issued = self.store.issue(REQUEST)
        b = self.bundle(issued)
        row = self.store.accept(challenge=issued["challenge"],bundle=b,
                                confirm_challenge=issued["challenge"])
        self.assertEqual(row["status"],"SIGNED_SOURCE_CLAIMS_ACCEPTED")
        self.assertEqual(row["verified_scopes"], list(SCOPES))
        self.assertFalse(row["external_content_observed_by_receiver"])
        self.assertFalse(row["real_world_owners_authenticated"])
        self.assertFalse(row["cp30_route_audited"])
        with self.assertRaisesRegex(ValueError,"already consumed"):
            self.store.accept(challenge=issued["challenge"],bundle=b,
                              confirm_challenge=issued["challenge"])
        self.assertEqual(self.store.status()["accepted_receipts"], 1)
        self.assertEqual(len(SourceEvidenceLedger(self.data).history()),5)

    def test_bundle_replay_against_new_challenge_denied(self):
        self.enroll_all()
        first = self.store.issue(REQUEST)
        second = self.store.issue(REQUEST)
        with self.assertRaisesRegex(ValueError, "receiver declaration"):
            self.store.accept(challenge=second["challenge"],bundle=self.bundle(first),
                              confirm_challenge=second["challenge"])
        self.assertEqual(self.store.status()["accepted_receipts"],0)

    def test_claim_digest_mismatch_even_with_valid_signature_denied(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST)
        with self.assertRaisesRegex(ValueError, "receiver declaration"):
            self.store.accept(challenge=issued["challenge"],
                bundle=self.bundle(issued,alter={"source_sha256":"f"*64}),
                confirm_challenge=issued["challenge"])

    def test_unrecognized_signing_key_denied(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST)
        different=dict(self.keys)
        different["middle"]=Ed25519PrivateKey.generate()
        with self.assertRaisesRegex(ValueError,"signature unproved"):
            self.store.accept(challenge=issued["challenge"],
                bundle=self.bundle(issued,keys=different),
                confirm_challenge=issued["challenge"])

    def test_scope_rotation_revokes_pending_challenge(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST)
        fp=self.store.status()["scope_enrollments"]["middle"]["key_sha256"]
        self.store.revoke(scope="middle",confirm_key_sha256=fp,operator="operator")
        replacement=Ed25519PrivateKey.generate()
        pub=replacement.public_key().public_bytes_raw()
        self.store.enroll(scope="middle",source_id="src-middle-new",public_key=b64(pub),
            locator="https://source.example/middle/new",operator="operator",
            confirm_key_sha256=sha256(pub).hexdigest())
        with self.assertRaisesRegex(ValueError,"revoked or rotated"):
            self.store.accept(challenge=issued["challenge"],bundle=self.bundle(issued),
                              confirm_challenge=issued["challenge"])

    def test_implicit_rotation_rejected(self):
        self.enroll_all()
        p=self.store.status()["scope_enrollments"]["donor"]
        with self.assertRaisesRegex(ValueError,"revoke existing"):
            self.store.enroll(scope="donor",source_id="other",public_key=b64(self.keys["donor"].public_key().public_bytes_raw()),
                locator="https://different.example/",operator="operator",
                confirm_key_sha256=p["key_sha256"])

    def test_confirmation_and_expiration_enforced(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST,ttl_seconds=30)
        with self.assertRaises(PermissionError):
            self.store.accept(challenge=issued["challenge"],bundle=self.bundle(issued),confirm_challenge="x")
        with patch("systems.workspace.external_evidence._utc",return_value=_utc()+timedelta(seconds=31)):
            with self.assertRaisesRegex(ValueError,"expired"):
                self.store.accept(challenge=issued["challenge"],bundle=self.bundle(issued),
                                  confirm_challenge=issued["challenge"])

    def test_observed_at_is_challenge_window_claim_not_external_truth(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST)
        old=(_utc()-timedelta(hours=2)).isoformat()
        with self.assertRaisesRegex(ValueError,"observation time"):
            self.store.accept(challenge=issued["challenge"],
                bundle=self.bundle(issued,alter={"observed_at":old}),
                confirm_challenge=issued["challenge"])

    def test_corrupted_history_rejected_not_silently_reset(self):
        self.enroll_all()
        raw=self.store.path.read_bytes()
        self.store.path.write_bytes(raw.replace(b"src-donor",b"src-other",1))
        with self.assertRaisesRegex(ValueError,"history invalid"):
            self.store.status()

    def test_distinct_tasks_not_authorized_by_signed_source_claim(self):
        self.enroll_all()
        issued=self.store.issue(REQUEST)
        before=self.store.status()["events"]
        self.assertEqual(before,4)
        self.assertFalse(self.store.status()["cp30_route_audited"])
        self.store.accept(challenge=issued["challenge"],bundle=self.bundle(issued),
                          confirm_challenge=issued["challenge"])
        self.assertFalse(self.store.status()["cp30_route_audited"])
        self.assertFalse((self.data/"runtime.jsonl").exists())

if __name__=="__main__":unittest.main()
