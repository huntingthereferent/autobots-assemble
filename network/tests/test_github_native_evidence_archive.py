"""Offline adversarial tests; fixtures are NOT original native observations."""
import io
import json
import unittest
from zipfile import ZipFile
from systems.workspace.github_native_evidence_archive import (
    REPO, SOURCES, SCHEMA, inspect_zip, prepare
)


def archive(files):
    buf = io.BytesIO()
    with ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


PATH = ".github/workflows/arc3-sp80-stage3-right-catcher-edge.yml"
SPEC = SOURCES[PATH]
RUN = {
    "id": 39616395169, "run_attempt": 1,
    "path": PATH, "name": SPEC[0],
    "repository": {"full_name": REPO},
    "head_repository": {"full_name": REPO},
    "actor": {"login": "huntingthereferent"},
    "status": "completed", "conclusion": "success",
    "event": "pull_request", "head_sha": "a" * 40,
    "html_url": "https://github.com/huntingthereferent/autobots-assemble/actions/runs/39616395169",
}
LISTING = {
    "total_count": 1,
    "artifacts": [{"id": 12352298969, "name": SPEC[1],
                   "expired": False, "size_in_bytes": 500}],
}
DATA = archive({name: b"witness-test-only" for name in SPEC[2]})


class NativeArchiveTests(unittest.TestCase):
    def test_exact_original_bytes_and_source_are_preserved(self):
        tag, record = prepare(RUN, LISTING, DATA)
        self.assertEqual(record["schema"], SCHEMA)
        self.assertEqual(record["run_id"], RUN["id"])
        self.assertEqual(record["source_commit"], "a" * 40)
        self.assertEqual(record["original_conclusion"], "success")
        self.assertEqual(record["artifact_id"], 12352298969)
        self.assertEqual(len(record["members"]), 2)
        self.assertIn(str(RUN["id"]), tag)

    def test_failure_is_preserved_as_failure(self):
        run = {**RUN, "conclusion": "failure"}
        _, record = prepare(run, LISTING, DATA)
        self.assertEqual(record["original_conclusion"], "failure")
        self.assertIn("no new native execution", record["claim"])

    def test_wrong_source_or_fork_rejected(self):
        for run in (
            {**RUN, "path": "other.yml"},
            {**RUN, "actor": {"login": "foreign"}},
            {**RUN, "head_repository": {"full_name": "other/repo"}},
            {**RUN, "head_sha": "not-a-real-commit"},
            {**RUN, "status": "in_progress"},
            {**RUN, "event": "issue_comment"},
        ):
            with self.subTest(run=run), self.assertRaises(ValueError):
                prepare(run, LISTING, DATA)

    def test_missing_expired_or_ambiguous_artifact_rejected(self):
        for listing in (
            {"total_count": 0, "artifacts": []},
            {"total_count": 101, "artifacts": LISTING["artifacts"]},
            {"total_count": 2, "artifacts": LISTING["artifacts"] * 2},
            {"total_count": 1, "artifacts": [{**LISTING["artifacts"][0], "expired": True}]},
        ):
            with self.subTest(listing=listing), self.assertRaises(ValueError):
                prepare(RUN, listing, DATA)

    def test_archive_member_change_or_unsafe_path_rejected(self):
        bad = [
            archive({"other.json": b"unexpected"}),
            archive({"../escape.json": b"unexpected"}),
            archive({name: b"test" for name in [*SPEC[2], "extra.txt"]}),
            b"not-a-zip",
        ]
        for data in bad:
            with self.subTest(data=data[:8]), self.assertRaises((ValueError, Exception)):
                inspect_zip(data, SPEC[2])

    def test_w13_bounded_source_member_family(self):
        members = inspect_zip(archive({
            "witness_real_browser_success.json": b"{}",
            "witness_real_chromium_complete.png": b"png-test-not-real",
        }), None)
        self.assertEqual(len(members), 2)
        with self.assertRaises(ValueError):
            inspect_zip(archive({"unknown.txt": b"test"}), None)


if __name__ == "__main__":
    unittest.main()
