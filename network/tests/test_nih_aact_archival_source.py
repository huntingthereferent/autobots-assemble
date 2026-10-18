"""Independent negative controls for a real published AACT snapshot gate.

These tests use a tiny synthetic local CSV *only to test parsing and
rejection*. The CI live step separately downloads and fully verifies the
289.6 MB 2023 archived file before admitting actual public study statuses.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import md5
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_aact_archival_source import (
    SCHEMA, ARCHIVE_MD5, ARCHIVE_RECORD, IDS, assemble, current_url,
    execute, parse_current, verify_extract_archive,
)


HEADER = "nct_id|overall_status|study_first_posted_date|last_update_posted_date\n"
ROWS = (
    "NCT03280849|RECRUITING|2017-09-21|2022-12-31\n"
    "NCT04153409|COMPLETED|2019-12-31|2022-01-03\n"
)


class ActualArchiveSourceTests(unittest.TestCase):
    @staticmethod
    def sample(path, *, content=HEADER+ROWS):
        raw = content.encode("utf8")
        Path(path).write_bytes(raw)
        return md5(raw).hexdigest()

    def test_00_official_sources_are_fixed_and_distinct(self):
        self.assertEqual(ARCHIVE_MD5, "d043fb7704bcff8cfb5be95d4f5ced85")
        self.assertEqual(len(IDS), 2)
        self.assertEqual(ARCHIVE_RECORD,
                         "https://zenodo.org/records/10058991")
        for nct in IDS:
            self.assertIn("clinicaltrials.gov/api/v2/studies/" + nct,
                          current_url(nct))
        with self.assertRaises(ValueError):
            current_url("../other-host")

    def test_01_reject_tampered_archival_content_and_malformed_source(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "studies.txt"
            digest = self.sample(p)
            evidence = verify_extract_archive(p, expected_md5=digest)
            self.assertEqual(evidence["dataset_md5"], digest)
            self.assertEqual(set(evidence["observed_source_rows"]), set(IDS))
            with self.assertRaises(ValueError):
                verify_extract_archive(p)  # fake fixture not pinned real file
            with self.assertRaises(ValueError):
                verify_extract_archive(p, target_ids=(IDS[0], IDS[0]),
                                       expected_md5=digest)
            self.sample(p, content=HEADER+ROWS+"NCT03280849|COMPLETED|2017-09-21|2023-01-01\n")
            with self.assertRaises(ValueError):
                verify_extract_archive(p, expected_md5=md5(p.read_bytes()).hexdigest())
            self.sample(p, content=HEADER+"NCT03280849|COMPLETED|2017-09-21|2023-01-01\n")
            with self.assertRaises(ValueError):
                verify_extract_archive(p, expected_md5=md5(p.read_bytes()).hexdigest())

    def test_02_current_registry_identity_and_status_must_match(self):
        for bad in (
            b'{"protocolSection":{"identificationModule":{"nctId":"NCT99999999"},"statusModule":{"overallStatus":"RECRUITING"}}}',
            b'{"protocolSection":{"identificationModule":{"nctId":"NCT03280849"}}}',
            b"{}",
        ):
            with self.assertRaises(ValueError):
                parse_current(IDS[0], bad)
        response = {
            "protocolSection": {
                "identificationModule": {"nctId": IDS[0]},
                "statusModule": {"overallStatus": "COMPLETED"},
            },
        }
        self.assertEqual(parse_current(IDS[0], json.dumps(response).encode())["overall_status"],
                         "COMPLETED")

    def test_03_mock_chain_records_only_archive_and_current_observations(self):
        def archive_fetch(path):
            self.sample(path)
        def current_fetch(nct):
            status = "COMPLETED" if nct == IDS[0] else "RECRUITING"
            content = {
                "protocolSection": {
                    "identificationModule": {"nctId": nct},
                    "statusModule": {"overallStatus": status},
                }
            }
            return parse_current(nct, json.dumps(content).encode())
        with TemporaryDirectory() as td:
            expected_md5 = md5((HEADER+ROWS).encode()).hexdigest()
            result = execute(
                output_dir=td, archive_fetch=archive_fetch,
                official_fetch=current_fetch,
                now=datetime(2026, 10, 18, 3, tzinfo=timezone.utc),
                expected_md5=expected_md5,
            )
            self.assertEqual(result["schema"], SCHEMA)
            self.assertEqual(result["case_count"], 2)
            self.assertTrue(all(x["status_values_differ"] for x in result["cases"]))
            self.assertFalse(result["exact_per_study_version_number_proven"])
            self.assertFalse(result["archive_date_is_individual_study_post_date"])
            self.assertFalse(result["additional_native_workstation_job"])
            self.assertFalse(result["official_NIH_submission"])
            text = (Path(td)/"nih-p2-archived-aact-source-receipt.json").read_text()
            self.assertIn("2023-10-31", text)
            self.assertNotIn("clinical trial outcome verified", text)

    def test_04_reject_current_archive_identity_mismatch(self):
        source = {
            "observed_source_rows": {
                IDS[0]: {"nct_id": IDS[0], "overall_status": "RECRUITING",
                         "source_column": "overall_status"},
            },
            "dataset_md5": "a"*32, "dataset_sha256": "b"*64,
            "dataset_size_bytes": 1024,
        }
        with self.assertRaises(ValueError):
            assemble(source, {}, retrieved_at="2026-10-18T03:00:00Z")


if __name__ == "__main__":
    unittest.main()
