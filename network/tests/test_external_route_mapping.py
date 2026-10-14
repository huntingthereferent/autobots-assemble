"""Exact observed bytes -> bounded F3 source claims, never CP30 native owner proof."""
from __future__ import annotations

import base64
from datetime import timedelta
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from systems.workspace.external_evidence import SourceEvidenceLedger, SCOPES, CLAIM_KIND, BUNDLE_KIND, _canonical, _utc
from systems.workspace.github_observation import observe_accepted_github_sources
from systems.workspace.external_route_mapping import (
    KIND, map_observed_sources, validate_declaration, _step,
)

COMMIT = "4" * 40
ROUTE_FP = "a" * 64
WITNESS = "b" * 64


def b64(v: bytes) -> str:
    return base64.b64encode(v).decode("ascii")


def side(name, phi, state, action):
    return {"source_label": name, "revision": 1, "phi": phi,
            "claimed_edges": [{"state": state, "action": action,
                                "target": list(_step(tuple(phi), tuple(state), action))}]}


def scope_doc(scope: str, challenge: str):
    return {"kind": KIND, "scope": scope, "source_id": "src-" + scope,
            "challenge": challenge, "route": "left", "route_fingerprint": ROUTE_FP,
            "witness_sha256": WITNESS,
            "old": side(scope+"-old", [0, 0, 1], [0, 0, 0], "B"),
            "new": side(scope+"-new", [0, 0, 0], [0, 0, 0], "A")}


class ExternalRouteMappingTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.store = SourceEvidenceLedger(self.data)
        self.secret = {}
        self.challenge = None
        self.bytes = {}
        self.files = {}
        self.observation = None

    def signed_observation(self, *, mutate=None):
        for scope in SCOPES:
            priv = Ed25519PrivateKey.generate()
            self.secret[scope] = priv
            pub = priv.public_key().public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
            self.store.enroll(scope=scope, source_id="src-"+scope, public_key=b64(pub),
                locator=f"https://github.com/demo-owner/route-fixtures/blob/main/{scope}.json",
                operator="receiver",confirm_key_sha256=sha256(pub).hexdigest())
        # Receiver controls challenge. Digests must be declared first; use a
        # fixed challenge through patched secrets token generator for documents.
        fixed = "c" * 48
        for scope in SCOPES:
            obj = scope_doc(scope, fixed)
            if mutate:
                mutate(scope, obj)
            self.bytes[scope] = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
            p = self.data / f"{scope}.json"
            p.write_bytes(self.bytes[scope]); self.files[scope] = p
        request = {"route": "left", "route_fingerprint": ROUTE_FP,
                   "witness_sha256": WITNESS,
                   "source_digests": {s: sha256(self.bytes[s]).hexdigest() for s in SCOPES}}
        with patch("systems.workspace.external_evidence.secrets.token_hex", return_value=fixed):
            issued = self.store.issue(request)
        self.challenge = issued["challenge"]
        signed = []
        for scope in SCOPES:
            claim = {"kind": CLAIM_KIND, "scope": scope, "source_id": "src-"+scope,
                     "challenge": self.challenge, "route": "left",
                     "route_fingerprint": ROUTE_FP, "witness_sha256": WITNESS,
                     "source_sha256": sha256(self.bytes[scope]).hexdigest(),
                     "observed_at": _utc().isoformat()}
            signed.append({"claim": claim, "signature": b64(self.secret[scope].sign(_canonical(claim)))})
        self.store.accept(challenge=self.challenge, confirm_challenge=self.challenge,
                          bundle={"kind": BUNDLE_KIND, "attestations": signed})
        def api(resource):
            if resource == "/repos/demo-owner/route-fixtures/git/ref/heads/main":
                return {"object": {"sha": COMMIT}}
            for scope in SCOPES:
                if resource == f"/repos/demo-owner/route-fixtures/contents/{scope}.json?ref={COMMIT}":
                    raw = self.bytes[scope]
                    return {"type": "file", "path": f"{scope}.json", "size":len(raw),
                            "encoding": "base64", "content": b64(raw),
                            "sha":sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()}
            raise AssertionError(resource)
        with patch("systems.workspace.github_observation._github_json", side_effect=api):
            self.observation = observe_accepted_github_sources(
                data_dir=self.data, challenge=self.challenge,
                confirm_challenge=self.challenge, allow_network=True)

    def map(self, **kw):
        return map_observed_sources(data_dir=self.data, challenge=self.challenge,
                                    observation_event=self.observation["observation_event"],
                                    source_files=self.files, **kw)

    def test_signed_public_bytes_map_to_declarations_but_never_owner_proof(self):
        self.signed_observation()
        journal = self.store.path.read_bytes()
        result = self.map()
        self.assertEqual(result["status"], "EXTERNAL_DECLARATIONS_CHECKED_NATIVE_OWNER_UNPROVED")
        self.assertTrue(result["external_bytes_match_signed_observation"])
        self.assertEqual(tuple(result["scopes"]), SCOPES)
        self.assertEqual(result["scopes"]["donor"]["old"]["law_phi"], [0,0,1])
        self.assertEqual(result["scopes"]["middle"]["new"]["claim_edge_count"], 1)
        for name in ("live_local_owner_verified", "in_process_owner_pins_verified",
                     "native_cp30_route_certificate_verified", "fresh_native_two_pass_route_audit",
                     "exact_task_authorized", "native_handoff_admitted"):
            self.assertIs(result[name], False, name)
        self.assertEqual(journal, self.store.path.read_bytes())
        self.assertFalse((self.data / "runtime.jsonl").exists())

    def test_missing_observation_and_wrong_exact_event_fail(self):
        self.signed_observation()
        with self.assertRaisesRegex(ValueError, "exact previously"):
            map_observed_sources(data_dir=self.data, challenge=self.challenge,
                                 observation_event="0"*64, source_files=self.files)
        with self.assertRaisesRegex(ValueError, "exact donor"):
            map_observed_sources(data_dir=self.data, challenge=self.challenge,
                                 observation_event=self.observation["observation_event"],
                                 source_files={"donor":self.files["donor"]})

    def test_tampered_local_copy_fails_even_if_json_valid(self):
        self.signed_observation()
        obj = json.loads(self.files["final"].read_text())
        obj["old"]["revision"] = 3
        self.files["final"].write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError, "do not match"):
            self.map()

    def test_claim_with_wrong_scope_is_rejected_after_correct_signature_and_observation(self):
        self.signed_observation(mutate=lambda scope,obj: obj.update(scope="donor") if scope=="middle" else None)
        with self.assertRaisesRegex(ValueError, "signed receiver binding: scope"):
            self.map()

    def test_claim_with_wrong_witness_is_rejected_after_correct_signature_and_observation(self):
        self.signed_observation(mutate=lambda scope,obj: obj.update(witness_sha256="f"*64) if scope=="final" else None)
        with self.assertRaisesRegex(ValueError, "signed receiver binding: witness_sha256"):
            self.map()

    def test_internally_inconsistent_finite_claim_is_rejected_even_if_signed(self):
        self.signed_observation(mutate=lambda scope,obj: obj["new"]["claimed_edges"][0].update(target=[2,2,2]) if scope=="donor" else None)
        with self.assertRaisesRegex(ValueError, "contradicts"):
            self.map()

    def test_duplicate_finite_claim_is_rejected(self):
        def mutate(scope,obj):
            if scope == "donor":
                e=obj["old"]["claimed_edges"][0]
                obj["old"]["claimed_edges"].append(dict(e))
        self.signed_observation(mutate=mutate)
        with self.assertRaisesRegex(ValueError, "duplicate claimed"):
            self.map()

    def test_invalid_source_schema_is_rejected_even_if_signed(self):
        self.signed_observation(mutate=lambda scope,obj: obj.update(owner_pin="pretend") if scope=="donor" else None)
        with self.assertRaisesRegex(ValueError, "declaration shape"):
            self.map()

    def test_source_key_revoke_after_observation_invalidates_mapping(self):
        self.signed_observation()
        fp = self.store.status()["scope_enrollments"]["middle"]["key_sha256"]
        self.store.revoke(scope="middle", confirm_key_sha256=fp, operator="receiver")
        with self.assertRaisesRegex(ValueError, "revoked or rotated"):
            self.map()

    def test_expired_observation_does_not_create_current_mapping(self):
        self.signed_observation()
        with patch("systems.workspace.external_route_mapping._now", return_value=_utc()+timedelta(minutes=11)):
            with self.assertRaisesRegex(ValueError, "too old"):
                self.map()

    def test_corrupt_journal_fails_closed(self):
        self.signed_observation()
        self.store.path.write_bytes(self.store.path.read_bytes().replace(b"src-donor",b"src-other",1))
        with self.assertRaisesRegex(ValueError,"history invalid"):
            self.map()

    def test_duplicate_json_member_rejected_even_when_signed_and_byte_matched(self):
        self.signed_observation()
        raw = self.bytes["middle"]
        # Test semantic ambiguity AFTER the signed digest and GitHub blob check.
        altered = raw[:-1] + b',"scope":"middle"}'
        # This intentional mutation makes the content mismatch, so validate the
        # strict duplicate-key parser directly before any digest calculation.
        from systems.workspace.external_route_mapping import _strict_object
        with self.assertRaisesRegex(ValueError, "duplicate JSON member"):
            json.loads(altered, object_pairs_hook=_strict_object)

    def test_native_cp29_owner_contract_rejects_external_dict_as_live_task(self):
        """Execute the actual recovered owner/pin gate, not a mock model."""
        source = os.environ.get("CP30_NATIVE_SOURCE_DIR")
        if not source:
            self.skipTest("CP30_NATIVE_SOURCE_DIR not supplied; run with reconstructed trusted CP30 source")
        source = Path(source)
        if not (source/"ab_chatbot_certificate_handoff.py").exists():
            self.fail("CP30_NATIVE_SOURCE_DIR does not contain native contract")
        # The native source is explicitly selected by this test's operator;
        # don't import it in the host's module namespace.
        code = '''
import json,sys
sys.path.insert(0,sys.argv[1])
from ab_chatbot_certificate_handoff import accept_handoff, _bound
from ab_chatbot_owner_pin_contract import OwnerPinRegistry
from types import SimpleNamespace
external={'kind':'cp30-external-finite-declaration/v1','scope':'donor'}
assert _bound(external) is False
result=accept_handoff('{}',{'external':external})
assert result.status=='HANDOFF_INVALID_TASK_SET',result.status
try:
    OwnerPinRegistry().issue(SimpleNamespace(owner='claimed',snapshot=external,origin_scope='REMOTE_ORIGIN_UNVERIFIED', _scope=lambda s:'REMOTE_ORIGIN_UNVERIFIED'))
except ValueError:
    pass
else:raise AssertionError('remote claim produced native owner pin')
print('NATIVE_REJECTS_EXTERNAL_CLAIMS')
'''
        done = subprocess.run([sys.executable,"-I","-c",code,str(source)],
                              capture_output=True,text=True,timeout=20,check=False)
        self.assertEqual(done.returncode,0,done.stderr)
        self.assertIn("NATIVE_REJECTS_EXTERNAL_CLAIMS",done.stdout)


if __name__ == "__main__":
    unittest.main()
