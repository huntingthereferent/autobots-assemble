"""Negative controls for the AACT depositor's actual Git source/date link.

Fixtures do not authenticate external date claims. Dedicated CI fetches the
exact historical owner Git blobs and verifies Git identities independently.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from systems.workspace import nih_p2_aact_owner_date_link as r


def example(load):
    return (
        "## clinical trials data\n"
        "## downloaded from the AACT: https://aact.ctti-clinicaltrials.org/\n"
        "## data of download: November 4, 2022\n"
        "## due to large file size, it was uploaded to Zenodo\n"
        f"{load}\n"
    ).encode("utf8")


class Reader:
    def __init__(self, content):
        self.buffer=BytesIO(content)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.buffer.close()
    def read(self, n=-1):
        return self.buffer.read(n)


class OwnerDateProvenanceTests(unittest.TestCase):
    def test_00_git_blob_sha_checks_entire_author_source_not_keyword(self):
        src=example(r.LINKED_LOAD)
        digest=r.github_blob_sha1(src)
        self.assertEqual(len(digest),40)
        self.assertNotEqual(digest,r.github_blob_sha1(src+b"# changed\n"))
        self.assertEqual(r.witness_source(src,expected_blob_sha=digest,
                                        expected_load=r.LINKED_LOAD)["source_date_claim"],
                         "2022-11-04")
        with self.assertRaises(ValueError):
            r.witness_source(src+b"# changed\n",expected_blob_sha=digest,
                             expected_load=r.LINKED_LOAD)

    def test_01_nearby_date_and_executable_url_are_required(self):
        src=example(r.LINKED_LOAD)
        mutations=(
            src.replace(b"November 4, 2022",b"November 4, 2023"),
            src.replace(b"ctti-clinicaltrials.org",b"some-other-source.org"),
            src.replace(b"zenodo.org/records/10058991",b"zenodo.org/records/99999999"),
            src.replace(b'ct = fread(',b'other = fread('),
            src.replace(b"## data of download: November 4, 2022\n",b""),
            src.replace(b"## clinical trials data\n",b"## data of download: November 4, 2022\n"),
            src.replace(b"## due to large file size, it was uploaded to Zenodo\n",
                        b"\n"*8),
        )
        for broken in mutations:
            with self.subTest(source=repr(broken[:100])),self.assertRaises(ValueError):
                r.witness_source(broken,expected_blob_sha=r.github_blob_sha1(broken),
                                 expected_load=r.LINKED_LOAD)

    def test_02_original_local_and_later_linked_date_match_but_not_actual_timestamp(self):
        raw_earlier=example(r.EARLIER_LOAD)
        raw_linked=example(r.LINKED_LOAD)
        with patch.object(r,"EARLIER_BLOB_SHA1",r.github_blob_sha1(raw_earlier)),\
             patch.object(r,"LINKED_BLOB_SHA1",r.github_blob_sha1(raw_linked)):
            receipt=r.compare_source_owner_statements(raw_earlier,raw_linked)
        self.assertEqual(receipt["schema"],r.SCHEMA)
        self.assertEqual(receipt["original_source_2022_date_owner_attested"],"2022-11-04")
        self.assertTrue(receipt["later_code_links_same_date_claim_to_exact_deposited_file_url"])
        self.assertFalse(receipt["2022_download_transaction_independently_timestamped"])
        self.assertFalse(receipt["underlying_snapshot_date_cryptographically_verified"])
        self.assertFalse(receipt["zenodo_file_SHA256_is_embedded_in_original_owner_script"])
        self.assertFalse(receipt["individual_registry_version_publication_instants_authenticated"])
        self.assertFalse(receipt["native_twelve_job_workstation_modified"])
        with patch.object(r,"EARLIER_BLOB_SHA1",r.github_blob_sha1(raw_earlier)),\
             patch.object(r,"LINKED_BLOB_SHA1",r.github_blob_sha1(raw_linked)):
            with self.assertRaises(ValueError):
                r.compare_source_owner_statements(raw_earlier,raw_linked+b"changed")

    def test_03_exact_original_zenodo_url_and_both_source_git_revisions_pinned(self):
        self.assertEqual(r.EARLIER_COMMIT,"96ccb828b5118e54c658fc1cd386173de67a4b4")
        self.assertEqual(r.LINKED_COMMIT,"675b7a4992d7e2469d368924f4c1f87d7ca162da")
        self.assertEqual(r.LINKED_BLOB_SHA1,"3e3f8714df2c037cce24961a57802546ce95f7b4")
        self.assertEqual(r.EXACT_ZENODO_URL,
                         "https://zenodo.org/records/10058991/files/AACT_studies.txt?download=1")
        self.assertEqual(r.ALREADY_VERIFIED_ZENODO_FILE_SHA256,
                         "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49")
        with self.assertRaises(ValueError):
            r.download_script("main", opener=lambda *_a,**_kw:Reader(b"irrelevant"))

    def test_04_short_source_fetch_fails_closed_on_identity_mismatch(self):
        local=example(r.LINKED_LOAD)
        with patch.object(r,"EARLIER_BLOB_SHA1",r.github_blob_sha1(local)),\
             patch.object(r,"LINKED_BLOB_SHA1",r.github_blob_sha1(local)):
            with TemporaryDirectory() as td:
                result=r.execute(output_dir=Path(td),
                    opener=lambda *_args,**_kwargs:Reader(local))
                self.assertTrue(result["owner_attested_source_date"])
                self.assertTrue((Path(td)/"nih-p2-aact-owner-script-date-link.json").exists())
        with self.assertRaises(ValueError):
            r.execute(output_dir="/tmp/unused",
                      opener=lambda *_a,**_kw:Reader(b"not the owner's original file"))

if __name__=="__main__":
    unittest.main()
