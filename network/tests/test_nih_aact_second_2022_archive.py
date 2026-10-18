"""Falsification for independently deposited 2022 AACT historical archive.

These fixtures are deliberately synthetic; the actual 236MB whole-source MD5
is verified in the separately executed live Github workflow, not in unittest.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from systems.workspace import nih_aact_second_2022_archive as a


class Reader:
    def __init__(self, content):
        self.bio=BytesIO(content)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.bio.close()
    def read(self,n=-1):
        return self.bio.read(n)


def make_zip(filename="datasets/studies.txt", header="nct_id|overall_status", extra=False):
    bio=BytesIO()
    with ZipFile(bio,"w",compression=ZIP_DEFLATED) as z:
        payload=header + "\n" + "\n".join(
            f"NCT{i:08d}|RECRUITING" for i in range(1100)) + "\n"
        payload+="NCT04153409|COMPLETED\n"
        z.writestr(filename,payload)
        if extra:
            z.writestr("nested/other.txt","not an original study version")
    return bio.getvalue()


def receipt(content):
    return {
        "entire_archive_md5": a.PUBLISHED_MD5,
        "entire_archive_bytes": a.EXPECTED_BYTES,
        "entire_archive_sha256": hashlib.sha256(content).hexdigest(),
    }


class HistoricalSourceTests(unittest.TestCase):
    def test_00_whole_byte_hash_rejects_modified_or_truncated_archive(self):
        data=b"exact fake archive bytes"
        with TemporaryDirectory() as td:
            dest=Path(td)/"archive.zip"
            with patch.object(a,"EXPECTED_BYTES",len(data)),patch.object(
                    a,"PUBLISHED_MD5",hashlib.md5(data).hexdigest()):
                observed=a.verify_download(output=dest,opener=lambda *_args,**_kw:Reader(data))
                self.assertEqual(observed["entire_archive_sha256"],
                                 hashlib.sha256(data).hexdigest())
                with self.assertRaises(ValueError):
                    a.verify_download(output=dest,
                        opener=lambda *_args,**_kw:Reader(data+b"x"))
                self.assertFalse(dest.exists())

    def test_01_only_verified_2022_deposit_can_enter(self):
        data=make_zip()
        with TemporaryDirectory() as td:
            path=Path(td)/"arch.zip"
            path.write_bytes(data)
            good=receipt(data)
            report=a.inspect_verified_archive(path,good)
            self.assertEqual(report["schema"],a.SCHEMA)
            self.assertTrue(report["direct_studies_table_found"])
            self.assertEqual(report["archive_member_layout"],"direct-studies-table")
            self.assertEqual(report["study_rows_examined"],1101)
            self.assertEqual(report["selected_study_records"]["NCT04153409"][
                "overall_status_2022"],"COMPLETED")
            self.assertFalse(report["per_version_original_public_posting_date_proven"])
            self.assertFalse(report["pairwise_2022_2023_status_comparison_proven"])
            self.assertFalse(report["original_twelve_job_workstation_modified"])
            for k,value in (
                ("entire_archive_md5","0"*32),
                ("entire_archive_bytes",123),
                ("entire_archive_sha256",""),
            ):
                tampered=dict(good);tampered[k]=value
                with self.subTest(field=k),self.assertRaises(ValueError):
                    a.inspect_verified_archive(path,tampered)

    def test_02_sql_or_pg_dump_does_not_masquerade_as_studies_table(self):
        for name,kind in (
            ("postgres_data.dmp","postgres-dump-awaiting-reproducible-extraction"),
            ("dump.sql","sql-dump-awaiting-reproducible-extraction"),
        ):
            data=make_zip(filename=name)
            with TemporaryDirectory() as td:
                path=Path(td)/"archive.zip"
                path.write_bytes(data)
                result=a.inspect_verified_archive(path,receipt(data))
                self.assertEqual(result["archive_member_layout"],kind)
                self.assertFalse(result["direct_studies_table_found"])
                self.assertEqual(result["selected_study_records"],{})
                self.assertFalse(result["pairwise_2022_2023_status_comparison_proven"])

    def test_03_reject_zip_member_path_traversal(self):
        for filename in ("../studies.txt","/studies.txt","nested\\studies.txt"):
            with TemporaryDirectory() as td:
                path=Path(td)/"archive.zip"
                path.write_bytes(make_zip(filename=filename))
                with self.subTest(filename=filename),self.assertRaises(ValueError):
                    a.zip_member_inventory(path)

    def test_04_reject_missing_or_duplicated_studies_columns(self):
        for header in ("nct_id|some_other_field","nct_id|overall_status|nct_id"):
            with TemporaryDirectory() as td:
                path=Path(td)/"archive.zip"
                path.write_bytes(make_zip(header=header))
                with self.subTest(header=header),self.assertRaises(ValueError):
                    a.inspect_verified_archive(path,receipt(path.read_bytes()))

    def test_05_reject_duplicate_study_id(self):
        data=make_zip()
        bio=BytesIO()
        with ZipFile(bio,"w",compression=ZIP_DEFLATED) as z:
            with ZipFile(BytesIO(data),"r") as src:
                payload=src.read("datasets/studies.txt")
            z.writestr("studies.txt",payload+b"NCT04153409|RECRUITING\n")
        with TemporaryDirectory() as td:
            path=Path(td)/"archive.zip"
            path.write_bytes(bio.getvalue())
            with self.assertRaises(ValueError):
                a.inspect_verified_archive(path,receipt(path.read_bytes()))

    def test_06_full_archive_replay_never_claims_original_version_history(self):
        self.assertEqual(a.DEPOSIT_DOI,"10.5281/zenodo.10091147")
        self.assertEqual(a.PUBLISHED_MD5,"1d4e6d141f40d300186fdd3d0a5980b1")
        self.assertEqual(a.EXPECTED_BYTES,236_218_508)
        self.assertNotIn("clinical_verdict","ACCURATE")

if __name__ == "__main__":
    unittest.main()
