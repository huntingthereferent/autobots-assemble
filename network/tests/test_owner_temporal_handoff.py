"""Negative controls for the separate-history read-only handoff boundary."""
from hashlib import sha256
import io
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import unittest
import zipfile
from systems.workspace.owner_temporal_handoff import (
    SOURCES, REPO, REPO_ID, OWNER_ID, validate_origin, unpack_zip, unpack_temporal)


def metadata(kind):
    p = SOURCES[kind]
    run = {"id":p["run"], "name":p["workflow"], "head_sha":p["commit"],
           "event":"push", "head_branch":"main", "run_attempt":1,
           "status":"completed", "conclusion":"success",
           "actor":{"id":OWNER_ID, "login":"huntingthereferent"},
           "repository":{"id":REPO_ID},
           "head_repository":{"id":REPO_ID, "full_name":REPO}}
    artifact = {"id":p["artifact"], "name":p["name"], "digest":p["digest"],
                "expired":False, "workflow_run":{"id":p["run"],
                    "head_sha":p["commit"], "repository_id":REPO_ID}}
    return run, artifact


class OwnerTemporalHandoffTests(unittest.TestCase):
    def test_exact_sources_are_distinct_and_metadata_is_required(self):
        self.assertNotEqual(SOURCES["owner"]["run"], SOURCES["temporal"]["run"])
        for kind in SOURCES:
            run, artifact = metadata(kind)
            validate_origin(kind, run, artifact)
            with self.assertRaises(ValueError):
                validate_origin(kind, {}, artifact)

    def test_foreign_owner_run_commit_or_attempt_refused(self):
        for kind in SOURCES:
            for field, value in (("id",1), ("name","other"), ("head_sha","0"*40),
                    ("event","pull_request"), ("head_branch","branch"),
                    ("run_attempt",2), ("status","in_progress"),
                    ("conclusion","failure"), ("actor",{"id":1}),
                    ("repository",{"id":1}), ("head_repository",{"id":1})):
                with self.subTest(kind=kind, field=field):
                    run, artifact = metadata(kind)
                    run[field] = value
                    with self.assertRaises(ValueError):
                        validate_origin(kind, run, artifact)

    def test_changed_expired_or_cross_run_artifact_refused(self):
        for kind in SOURCES:
            for field, value in (("id",1), ("name","other"), ("digest","sha256:"+"0"*64),
                    ("expired",True), ("workflow_run",{"id":1})):
                with self.subTest(kind=kind, field=field):
                    run, artifact = metadata(kind)
                    artifact[field] = value
                    with self.assertRaises(ValueError):
                        validate_origin(kind, run, artifact)

    def test_zip_digest_and_traversal_are_checked_before_use(self):
        for name in ("../escape", "/absolute", "back\\slash"):
            raw = io.BytesIO()
            with zipfile.ZipFile(raw,"w") as z:
                z.writestr(name,"refused")
            data = raw.getvalue()
            with TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    unpack_zip(data, Path(tmp)/"out", "sha256:"+sha256(data).hexdigest())
                self.assertFalse((Path(tmp)/"escape").exists())
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                unpack_zip(data,Path(tmp)/"out","sha256:"+"0"*64)

    def test_duplicate_or_symlink_zip_entries_refused(self):
        for linked in (True, False):
            raw = io.BytesIO()
            with zipfile.ZipFile(raw,"w") as z:
                if linked:
                    entry = zipfile.ZipInfo("link")
                    entry.external_attr = 0o120777 << 16
                    z.writestr(entry,"../outside")
                else:
                    z.writestr("a/b", "one")
                    z.writestr("a//b", "two")
            data = raw.getvalue()
            with TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    unpack_zip(data,Path(tmp)/"out","sha256:"+sha256(data).hexdigest())

    def test_tar_symlink_and_non_native_path_refused(self):
        for name, linked in (("workstation/link",True), ("other",False), ("../outside",False)):
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive = root/"actual-native-workstation.tar.gz"
                with tarfile.open(archive,"w:gz") as stream:
                    entry = tarfile.TarInfo(name)
                    if linked:
                        entry.type = tarfile.SYMTYPE
                        entry.linkname = "../outside"
                    stream.addfile(entry)
                (root/"actual-native-workstation.sha256").write_text(
                    sha256(archive.read_bytes()).hexdigest()+"  archive\n")
                with self.assertRaises(ValueError):
                    unpack_temporal(root, root/"out")


if __name__ == "__main__":
    unittest.main()
