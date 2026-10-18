"""Private continuation codec regression tests: fixtures are NOT owner W13 data."""
from __future__ import annotations
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from systems.workspace.owner_native_evidence_vault import (
    SCHEMA,PARENT_EVENT,PARENT_SOURCE,_path,seal_verified,restore_verified,main)

COMMIT="a"*40
EVENT="evt_"+"b"*32


def mock_finite_source(root):
    # Explicit TEST-ONLY source identity; the production _witness is not mocked.
    return {"parent_event":PARENT_EVENT,"child_event":EVENT,
            "parent_source_fingerprint":PARENT_SOURCE,
            "child_source_fingerprint":"c"*64}


class EncryptedNativeContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.runtime=self.root/"runtime"
        folder=self.runtime/"workstation"/"editions"/"worker"
        folder.mkdir(parents=True)
        (self.runtime/"runtime.jsonl").write_text("private runtime events\n")
        (self.runtime/"coordinator-windows.jsonl").write_text("private coordinator history\n")
        (folder/"source.py").write_text("private source edition\n")
        self.key=X25519PrivateKey.generate()
        pub=self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        self.public=base64.b64encode(pub).decode()
        self.private=self.key.private_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption())
        self.sealed=self.root/"native.enc"
        self.reopened=self.root/"reopened"

    def _seal_mock_only(self):
        with patch("systems.workspace.owner_native_evidence_vault._witness",
                   side_effect=mock_finite_source):
            return seal_verified(data_dir=self.runtime,public_key_b64=self.public,
                owner_execution_commit=COMMIT,output=self.sealed)

    def test_seal_restore_encrypted_bytes_and_private_worker_edition(self):
        outcome=self._seal_mock_only()
        self.assertEqual(outcome["schema"],SCHEMA)
        self.assertTrue(outcome["native_reverified_before_sealing"])
        raw=self.sealed.read_bytes()
        for forbidden in (b"private runtime events",b"private coordinator history",
                          b"private source edition"):
            self.assertNotIn(forbidden,raw)
        self.assertEqual(self.sealed.stat().st_mode & 0o777,0o600)
        with patch("systems.workspace.owner_native_evidence_vault._witness",
                   side_effect=mock_finite_source):
            result=restore_verified(encrypted=self.sealed,private_key_raw=self.private,
                destination=self.reopened,expected_owner_execution_commit=COMMIT,
                expected_child_event=EVENT)
        self.assertEqual(result["state"],"RESTORED_AND_FRESH_NATIVE_REVERIFIED")
        self.assertEqual((self.reopened/"runtime.jsonl").read_bytes(),
                         (self.runtime/"runtime.jsonl").read_bytes())
        self.assertEqual((self.reopened/"workstation/editions/worker/source.py").read_bytes(),
                         (self.runtime/"workstation/editions/worker/source.py").read_bytes())

    def test_production_does_not_seal_nonexistent_native_parent_child(self):
        # Deliberately no mock: actual RuntimeJournal rejects fixture contents.
        with self.assertRaises(Exception):
            seal_verified(data_dir=self.runtime,public_key_b64=self.public,
                owner_execution_commit=COMMIT,output=self.sealed)
        self.assertFalse(self.sealed.exists())

    def test_wrong_key_or_modified_ciphertext_fails_before_restoration(self):
        self._seal_mock_only()
        wrong=X25519PrivateKey.generate().private_bytes(
            encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption())
        with self.assertRaises(InvalidTag):
            restore_verified(encrypted=self.sealed,private_key_raw=wrong,
                destination=self.reopened,expected_owner_execution_commit=COMMIT,
                expected_child_event=EVENT)
        packet=json.loads(self.sealed.read_text())
        packet["ciphertext"]=base64.b64encode(b"tampered").decode()
        self.sealed.write_text(json.dumps(packet))
        with self.assertRaises(InvalidTag):
            restore_verified(encrypted=self.sealed,private_key_raw=self.private,
                destination=self.reopened,expected_owner_execution_commit=COMMIT,
                expected_child_event=EVENT)
        self.assertFalse(self.reopened.exists())

    def test_wrong_provenance_or_event_and_overwrite_are_rejected(self):
        self._seal_mock_only()
        for owner,event in (("d"*40,EVENT),(COMMIT,"evt_"+"d"*32)):
            with self.assertRaises(ValueError):
                restore_verified(encrypted=self.sealed,private_key_raw=self.private,
                    destination=self.reopened,expected_owner_execution_commit=owner,
                    expected_child_event=event)
        self.reopened.mkdir()
        with self.assertRaises(ValueError):
            restore_verified(encrypted=self.sealed,private_key_raw=self.private,
                destination=self.reopened,expected_owner_execution_commit=COMMIT,
                expected_child_event=EVENT)

    def test_path_escapes_symlinks_and_existing_capsules_are_refused(self):
        for forbidden in ("../elsewhere","/root/file","runtime.jsonl/extra",
                          "workstation/../../outside","wrong/source","workstation",
                          "workstation\\escape",""):
            with self.assertRaises(ValueError,msg=forbidden):
                _path(forbidden)
        with patch("systems.workspace.owner_native_evidence_vault._witness",
                   side_effect=mock_finite_source):
            self._seal_mock_only()
            with self.assertRaises(ValueError):
                seal_verified(data_dir=self.runtime,public_key_b64=self.public,
                    owner_execution_commit=COMMIT,output=self.sealed)
        self.sealed.unlink()
        outside=self.root/"elsewhere"
        outside.mkdir()
        (self.runtime/"workstation"/"evil").symlink_to(outside,target_is_directory=True)
        with patch("systems.workspace.owner_native_evidence_vault._witness",
                   side_effect=mock_finite_source):
            with self.assertRaises(ValueError):
                seal_verified(data_dir=self.runtime,public_key_b64=self.public,
                    owner_execution_commit=COMMIT,output=self.sealed)

    def test_cli_private_key_permissions_are_enforced(self):
        self._seal_mock_only()
        keyfile=self.root/"private.raw"
        keyfile.write_bytes(self.private)
        keyfile.chmod(0o644)
        with self.assertRaisesRegex(ValueError,"0600"):
            main(["restore","--sealed-file",str(self.sealed),
                  "--private-key-file",str(keyfile),
                  "--owner-execution-commit",COMMIT,"--child-event",EVENT,
                  "--output-dir",str(self.reopened)])


if __name__=="__main__":
    unittest.main()
