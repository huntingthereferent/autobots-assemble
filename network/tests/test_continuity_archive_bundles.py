"""Regression for original Continuity/Cyclic research archives.

Archives are historical evidence, not active engine modules. This checks exact
bytes, ZIP readability and safe inventory without altering a checkout.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from research.continuity_archive_import import inventory, run

ROOT = Path(__file__).resolve().parents[2]
BUNDLES = ROOT / "research/continuity_engine/collected/archive_bundles"
MANIFEST = BUNDLES / "MANIFEST.json"


class OriginalArchiveIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_covers_all_original_archives(self):
        files = self.manifest["files"]
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["total_archive_count"], 16)
        self.assertEqual(self.manifest["continuity_research_bundles"], 15)
        self.assertEqual(self.manifest["adjacent_prototypes"], 1)
        self.assertEqual(len(files), 16)
        paths = [x["path"] for x in files]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(sum(x["bytes"] for x in files), self.manifest["total_bytes"])
        self.assertEqual(self.manifest["total_bytes"], 780414)

    def test_original_archive_bytes_and_zip_crc(self):
        for item in self.manifest["files"]:
            with self.subTest(archive=item["filename"]):
                file = ROOT / item["path"]
                raw = file.read_bytes()
                self.assertEqual(len(raw), item["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256"])
                git_header = b"blob " + str(len(raw)).encode("ascii") + b"\x00"
                self.assertEqual(hashlib.sha1(git_header + raw).hexdigest(), item["git_blob_sha1"])
                with zipfile.ZipFile(file) as archive:
                    self.assertIsNone(archive.testzip())

    def test_research_bundle_inventory_is_safe_and_complete(self):
        rows, blobs = inventory(BUNDLES)
        self.assertEqual(len(rows), 304)
        self.assertEqual(len(blobs), 304)
        self.assertEqual(len(set(x["archive"] for x in rows)), 15)
        self.assertEqual(len(set(x["sha256"] for x in rows)), 171)
        self.assertEqual(len(set(x["target"] for x in rows)), 304)

    def test_staged_extraction_remains_isolated_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            first = run(BUNDLES, path)
            self.assertEqual((first["pending_files"], first["staged"]), (304, False))
            staged = run(BUNDLES, path, stage=True)
            self.assertEqual(staged["pending_files"], 304)
            repeated = run(BUNDLES, path)
            self.assertEqual((repeated["pending_files"], repeated["staged"]), (0, False))


if __name__ == "__main__":
    unittest.main()