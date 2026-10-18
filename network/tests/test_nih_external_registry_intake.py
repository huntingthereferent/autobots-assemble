"""Host-only negative controls for exact ClinicalTrials.gov posting metadata.

All test payloads are MOCKS; only the separately gated live CI fetch uses
the official external registry. Historical trial contents are not reconstructed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from systems.workspace.nih_external_registry_intake import (
    IDS, SCHEMA, execute, extract, events_as_posted_as_of, source_url,
)


def mock(nct_id, *, first="2020-02-01", last="2023-05-04", results=None):
    status = {
        "studyFirstPostDateStruct": {"date": first, "type": "ACTUAL"},
        "lastUpdatePostDateStruct": {"date": last},
        "overallStatus": "COMPLETED",
    }
    if results is not None:
        status["resultsFirstPostDateStruct"] = {"date": results}
    return json.dumps({
        "protocolSection": {
            "identificationModule": {"nctId": nct_id, "briefTitle": "Test-only title"},
            "statusModule": status,
            "contactsLocationsModule": {"centralContacts": [{"name": "MUST NEVER SAVE"}]},
        }
    }, sort_keys=True).encode("utf8")


class ExternalRegistryIntakeTests(unittest.TestCase):
    def test_future_posting_dates_fail_before_receipt_is_written(self):
        for dates in (
            dict(first="2099-01-01", last="2099-01-02"),
            dict(last="2099-01-01"),
            dict(results="2099-01-01"),
        ):
            with self.subTest(dates=dates), TemporaryDirectory() as td:
                with self.assertRaisesRegex(ValueError, "later than the source observation"):
                    execute(output_dir=td, ids=(IDS[0],),
                            fetch=lambda _: mock(IDS[0], **dates),
                            now=datetime(2026, 10, 18, 2, tzinfo=timezone.utc))
                self.assertFalse((Path(td) / "nih-p2-public-registry-intake.json").exists())

    def test_posting_on_observation_date_is_admitted(self):
        record = extract(IDS[0], mock(IDS[0], last="2026-10-18"),
                         retrieved_at="2026-10-18T00:00:00Z")
        self.assertEqual(record["posting_events"][-1]["posted_on"], "2026-10-18")

    def test_00_source_mapping_is_official_and_exact(self):
        self.assertEqual(len(IDS), 3)
        for nct_id in IDS:
            self.assertIn("clinicaltrials.gov/api/v2/studies/" + nct_id,
                          source_url(nct_id))
        for bad in ("../..", "NCT123", "NCT12345678?foo=bar", ""):
            with self.assertRaises(ValueError):
                source_url(bad)

    def test_01_publication_event_ordering_at_exact_date(self):
        record = extract(
            "NCT04852770",
            mock("NCT04852770", results="2022-03-03"),
            retrieved_at="2026-10-18T02:00:00Z",
        )
        self.assertFalse(record["historical_content_available"])
        self.assertFalse(record["patient_data_ingested"])
        self.assertEqual([x["kind"] for x in record["posting_events"]],
                         ["first_posted", "results_first_posted", "last_update_posted"])
        self.assertEqual(events_as_posted_as_of([record], "2020-01-31"), [])
        before = events_as_posted_as_of([record], "2020-02-01")
        self.assertEqual([x["event"] for x in before], ["first_posted"])
        later = events_as_posted_as_of([record], "2023-05-04")
        self.assertEqual(len(later), 3)
        self.assertEqual(len(events_as_posted_as_of([record], "2023-05-03")), 2)
        self.assertFalse(any("overallStatus" in str(event) for event in later))

    def test_02_fail_closed_on_wrong_identity_date_or_broken_metadata(self):
        for data in (
            mock("NCT99999999"),
            mock("NCT04852770", first="2025-01-01", last="2024-12-31"),
            mock("NCT04852770", first="2020-01-01", last="2022-01-01", results="2023-01-01"),
            mock("NCT04852770", first="2020-01", last="2023-05-04"),
            b'{"protocolSection":{"statusModule":{}}}',
        ):
            with self.subTest(data=data[:50]):
                with self.assertRaises(ValueError):
                    extract("NCT04852770", data, retrieved_at="2026-10-18T02:00:00Z")
        with self.assertRaises(ValueError):
            extract("NCT04852770", mock("NCT04852770"),
                    retrieved_at="not a timestamp")
        with self.assertRaises(ValueError):
            extract("NCT04852770", b"x" * 65537,
                    retrieved_at="2026-10-18T02:00:00Z")

    def test_03_mock_intake_preserves_only_public_posting_facts(self):
        def fetch(url):
            nct_id = url.split("?", 1)[0].rsplit("/", 1)[-1]
            return mock(nct_id)
        with TemporaryDirectory() as td:
            report = execute(
                output_dir=td, fetch=fetch, ids=IDS,
                now=datetime(2026, 10, 18, 2, tzinfo=timezone.utc))
            self.assertEqual(report["schema"], SCHEMA)
            self.assertEqual(report["record_count"], 3)
            self.assertFalse(report["patient_data_ingested"])
            self.assertFalse(report["synthetic_observations"])  # live intake mode has no source-driven synthetic graph
            self.assertFalse(report["biomedical_benchmark_complete"])
            self.assertTrue(report["does_not_reconstruct_historical_version_contents"])
            self.assertEqual(len(report["cutoff_frontiers"][-1]["posting_events_visible"]), 6)
            serialized=(Path(td)/"nih-p2-public-registry-intake.json").read_text()
            self.assertNotIn("MUST NEVER SAVE", serialized)
            self.assertNotIn("overallStatus", serialized)

    def test_04_duplicate_and_bad_ids_are_rejected_before_fetch(self):
        with TemporaryDirectory() as td:
            def no_fetch(_):
                raise AssertionError("fetch must not happen")
            for ids in ((IDS[0], IDS[0]), ("not-nct",), ()):
                with self.assertRaises(ValueError):
                    execute(output_dir=td, fetch=no_fetch, ids=ids)


if __name__ == "__main__":
    unittest.main()
