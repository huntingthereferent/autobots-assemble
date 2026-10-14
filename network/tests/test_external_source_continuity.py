"""Two independently signed, observed public GitHub snapshots are NOT owner pins."""
from __future__ import annotations

import base64
from hashlib import sha1, sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from systems.workspace.external_evidence import (SourceEvidenceLedger, SCOPES,
    BUNDLE_KIND, CLAIM_KIND, _canonical, _utc)
from systems.workspace.github_observation import observe_accepted_github_sources
from systems.workspace.external_source_continuity import compare_external_observations
from network.tests.test_external_route_mapping import scope_doc, b64, ROUTE_FP, WITNESS, _step

COMMITS = ("4"*40, "5"*40)
REPO = "/repos/demo-owner/route-fixtures"


class ExternalSourceContinuityTests(unittest.TestCase):
    def setUp(self):
        td=TemporaryDirectory();self.addCleanup(td.cleanup)
        self.data=Path(td.name)
        self.store=SourceEvidenceLedger(self.data)
        self.priv={}
        for scope in SCOPES:
            key=Ed25519PrivateKey.generate();self.priv[scope]=key
            pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
            self.store.enroll(scope=scope,source_id="src-"+scope,public_key=b64(pub),
                locator=f"https://github.com/demo-owner/route-fixtures/blob/main/{scope}.json",
                operator="receiver",confirm_key_sha256=sha256(pub).hexdigest())
        self.snapshots=[]

    def capture(self, index: int, *, mutate=None, route="left"):
        challenge=("c" if index==0 else "d")*48
        files={};raws={}
        for scope in SCOPES:
            doc=scope_doc(scope,challenge)
            doc["route"]=route
            if mutate:mutate(scope,doc)
            raw=json.dumps(doc,sort_keys=True,separators=(",", ":")).encode()
            path=self.data/f"{index}-{scope}.json";path.write_bytes(raw)
            files[scope]=path;raws[scope]=raw
        req={"route":route,"route_fingerprint":ROUTE_FP,"witness_sha256":WITNESS,
             "source_digests":{s:sha256(raws[s]).hexdigest() for s in SCOPES}}
        with patch("systems.workspace.external_evidence.secrets.token_hex",return_value=challenge):
            issued=self.store.issue(req)
        attestations=[]
        for scope in SCOPES:
            claim={"kind":CLAIM_KIND,"scope":scope,"source_id":"src-"+scope,
                "challenge":challenge,"route":route,"route_fingerprint":ROUTE_FP,
                "witness_sha256":WITNESS,"source_sha256":sha256(raws[scope]).hexdigest(),
                "observed_at":_utc().isoformat()}
            attestations.append({"claim":claim,"signature":b64(self.priv[scope].sign(_canonical(claim)))})
        self.store.accept(challenge=challenge,confirm_challenge=challenge,
            bundle={"kind":BUNDLE_KIND,"attestations":attestations})
        def get(resource):
            if resource == REPO+"/git/ref/heads/main":return {"object":{"sha":COMMITS[index]}}
            for scope in SCOPES:
                if resource==f"{REPO}/contents/{scope}.json?ref={COMMITS[index]}":
                    raw=raws[scope]
                    return {"type":"file","path":f"{scope}.json", "size":len(raw),
                            "encoding":"base64","content":b64(raw),
                            "sha":sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()}
            raise AssertionError(resource)
        with patch("systems.workspace.github_observation._github_json",side_effect=get):
            seen=observe_accepted_github_sources(data_dir=self.data,challenge=challenge,
                               confirm_challenge=challenge,allow_network=True)
        self.snapshots.append((challenge,seen["observation_event"],files))
        return self.snapshots[-1]

    def capture_pair(self,mutate_second=None,route2="left"):
        self.capture(0)
        self.capture(1,mutate=mutate_second,route=route2)

    def compare(self,*,network=False,confirm=True,first=0,second=1):
        a=self.snapshots[first];b=self.snapshots[second]
        return compare_external_observations(data_dir=self.data,
            earlier_challenge=a[0],earlier_event=a[1],
            later_challenge=b[0],later_event=b[1],
            earlier_files=a[2],later_files=b[2],allow_network=network,
            confirm_later_challenge=b[0] if confirm else "wrong")

    def github(self,*,status="ahead",head=COMMITS[1],mutate_journal=False):
        calls=[]
        def api(resource):
            calls.append(resource)
            if resource==REPO+"/git/ref/heads/main":
                return {"object":{"sha":head}}
            if resource==REPO+f"/compare/{COMMITS[0]}...{COMMITS[1]}":
                if mutate_journal:self.store._append("KEY_REVOKED",{
                    "scope":"donor", "key_sha256":self.store.status()["scope_enrollments"]["donor"]["key_sha256"],
                    "operator":"tester", "revoked_at":_utc().isoformat()})
                return {"status":status,"ahead_by":1,"behind_by":0,
                    "base_commit":{"sha":COMMITS[0]},
                    "merge_base_commit":{"sha":COMMITS[0]},
                    "commits":[{"sha":COMMITS[1]}]}
            raise AssertionError(resource)
        return api,calls

    def test_offline_pair_is_read_only_and_never_upgrades_cp30_proof(self):
        self.capture_pair()
        before=self.store.path.read_bytes()
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=AssertionError("network forbidden")):
            result=self.compare()
        self.assertEqual(result["status"],"EXTERNAL_SIGNED_OBSERVATION_PAIR_NATIVE_OWNER_UNPROVED")
        self.assertFalse(result["online_ancestry_checked"])
        self.assertEqual(len(result["scopes"]),3)
        for flag in ("live_local_owner_verified","native_owner_pins_verified","native_route_reaudited",
                     "exact_task_authorized","native_handoff_admitted"):
            self.assertIs(result[flag],False)
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertFalse((self.data/"runtime.jsonl").exists())

    def test_explicit_online_comparison_reports_descendants_only(self):
        self.capture_pair()
        api,calls=self.github()
        before=self.store.path.read_bytes()
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=api), \
             patch("systems.workspace.external_source_continuity._branch_sha",return_value=COMMITS[1]):
            outcome=self.compare(network=True)
        self.assertTrue(outcome["github_reported_descendant_commits"])
        self.assertEqual(outcome["status"],"EXTERNAL_GITHUB_LINEAGE_REPORTED_NATIVE_OWNER_UNPROVED")
        self.assertEqual(calls,[REPO+f"/compare/{COMMITS[0]}...{COMMITS[1]}"])
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_no_network_without_confirmation(self):
        self.capture_pair()
        with self.assertRaises(PermissionError):self.compare(network=True,confirm=False)

    def test_two_distinct_challenges_required(self):
        self.capture_pair()
        with self.assertRaisesRegex(ValueError,"two independently"):
            self.compare(first=0,second=0)

    def test_reverse_observation_order_rejected(self):
        self.capture_pair()
        with self.assertRaisesRegex(ValueError,"not forward"):
            self.compare(first=1,second=0)

    def test_wrong_event_id_rejected(self):
        self.capture_pair()
        a,b=self.snapshots
        with self.assertRaisesRegex(ValueError,"exact previously"):
            compare_external_observations(data_dir=self.data,
                earlier_challenge=a[0],earlier_event="0"*64,later_challenge=b[0],later_event=b[1],
                earlier_files=a[2],later_files=b[2])

    def test_local_file_mutation_rejected(self):
        self.capture_pair()
        self.snapshots[1][2]["donor"].write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,"do not match"):
            self.compare()

    def test_key_rotation_or_revocation_breaks_pair(self):
        self.capture_pair()
        k=self.store.status()["scope_enrollments"]["donor"]["key_sha256"]
        self.store.revoke(scope="donor",confirm_key_sha256=k,operator="tester")
        with self.assertRaisesRegex(ValueError,"revoked or rotated"):
            self.compare()

    def test_branch_head_advanced_requires_new_observation(self):
        self.capture_pair()
        api,_=self.github(head="7"*40)
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=api), \
             patch("systems.workspace.external_source_continuity._branch_sha",return_value="7"*40):
            with self.assertRaisesRegex(ValueError,"head moved"):
                self.compare(network=True)

    def test_diverged_git_history_rejected(self):
        self.capture_pair()
        api,_=self.github(status="diverged")
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=api), \
             patch("systems.workspace.external_source_continuity._branch_sha",return_value=COMMITS[1]):
            with self.assertRaisesRegex(ValueError,"descendant"):
                self.compare(network=True)

    def test_claimed_revision_regression_rejected(self):
        self.capture_pair(mutate_second=lambda s,d: d["new"].update(revision=0) if s=="donor" else None)
        with self.assertRaisesRegex(ValueError,"regressed"):self.compare()

    def test_changed_declaration_with_unbumped_revision_rejected(self):
        def edit(scope,doc):
            if scope=="donor":
                doc["new"]["phi"]=[0,0,2]
                edge=doc["new"]["claimed_edges"][0]
                edge["target"]=list(_step((0,0,2),tuple(edge["state"]),edge["action"]))
        self.capture_pair(mutate_second=edit)
        with self.assertRaisesRegex(ValueError,"without a revision change"):
            self.compare()

    def test_revision_increment_can_be_claimed_not_verified_as_owner(self):
        self.capture_pair(mutate_second=lambda s,d: d["new"].update(revision=2))
        row=self.compare()
        self.assertEqual(row["scopes"]["donor"]["new_side_revisions"],[1,2])
        self.assertFalse(row["live_local_owner_verified"])

    def test_source_label_change_breaks_identity(self):
        self.capture_pair(mutate_second=lambda s,d: d["old"].update(source_label="other") if s=="middle" else None)
        with self.assertRaisesRegex(ValueError,"source label"):
            self.compare()

    def test_route_change_requires_new_referent(self):
        self.capture_pair(route2="right")
        with self.assertRaisesRegex(ValueError,"route or witness referent changed"):
            self.compare()

    def test_invalid_github_compare_merge_base_rejected(self):
        self.capture_pair()
        def api(resource):
            return {"status":"ahead","ahead_by":1,"behind_by":0,
                    "base_commit":{"sha":COMMITS[0]},
                    "merge_base_commit":{"sha":"e"*40},
                    "commits":[{"sha":COMMITS[1]}]}
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=api), \
             patch("systems.workspace.external_source_continuity._branch_sha",return_value=COMMITS[1]):
            with self.assertRaisesRegex(ValueError,"descendant"):
                self.compare(network=True)

    def test_online_journal_change_detected(self):
        self.capture_pair()
        api,_=self.github(mutate_journal=True)
        with patch("systems.workspace.external_source_continuity._github_json",side_effect=api), \
             patch("systems.workspace.external_source_continuity._branch_sha",return_value=COMMITS[1]):
            with self.assertRaisesRegex(ValueError,"journal changed"):
                self.compare(network=True)

    def test_missing_scope_files_refused(self):
        self.capture_pair()
        old,new=self.snapshots
        with self.assertRaisesRegex(ValueError,"exact two complete"):
            compare_external_observations(data_dir=self.data,earlier_challenge=old[0],earlier_event=old[1],
                later_challenge=new[0],later_event=new[1],
                earlier_files={"donor":old[2]["donor"]},later_files=new[2])


if __name__=="__main__":unittest.main()
