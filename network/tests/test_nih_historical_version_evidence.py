"""Historical version content must come from its matching version endpoint.

These are mock-negative controls. Real source admission requires separate
external GitHub CI fetch; tests alone do not establish historic source access.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_historical_version_evidence import (
    SCHEMA, TRIAL_ID, endpoint, overview, historical_content, execute,
)


def index_bytes(changes=None):
    changes = changes or [
        {"version": 0, "date": "2017-09-20"},
        {"version": 1, "date": "2018-03-20"},
        {"version": 4, "date": "2020-08-11"},
    ]
    return json.dumps({"history": {"changes": changes}}).encode()


def version_bytes(version, *, nct_id=TRIAL_ID, status="RECRUITING"):
    return json.dumps({
        "studyVersion": version,
        "study": {
            "protocolSection": {
                "identificationModule": {"nctId": nct_id},
                "statusModule": {"overallStatus": status},
                "contactsLocationsModule": {"centralContacts": [{"name": "SHOULD NOT ARCHIVE"}]},
            }
        },
    }, sort_keys=True).encode()


class HistoricalVersionTests(unittest.TestCase):
    def test_00_correct_version_url_and_real_index_contract(self):
        self.assertEqual(endpoint(TRIAL_ID),
                         "https://www.clinicaltrials.gov/api/int/studies/NCT03280849?history=true")
        self.assertEqual(endpoint(TRIAL_ID, 4),
                         "https://www.clinicaltrials.gov/api/int/studies/NCT03280849/history/4")
        rows=overview(TRIAL_ID, index_bytes())
        self.assertEqual([r["version"] for r in rows], [0,1,4])
        for bad in ("../secret", "NCT123", ""):
            with self.assertRaises(ValueError):
                endpoint(bad)
        for v in (-1, "4", True, 100001):
            with self.assertRaises(ValueError):
                endpoint(TRIAL_ID,v)

    def test_01_fail_closed_on_malformed_history_dates_versions(self):
        bad = (
            index_bytes([{"version":0,"date":"2020-01-01"}]),
            index_bytes([{"version":0,"date":"2020-01-01"},{"version":0,"date":"2020-02-01"}]),
            index_bytes([{"version":0,"date":"2020-01-02"},{"version":1,"date":"2020-01-01"}]),
            index_bytes([{"version":0,"date":"2020-01"},{"version":1,"date":"2020-02-01"}]),
            b'{"history":{}}',
            b"invalid",
        )
        for source in bad:
            with self.subTest(raw=source[:70]):
                with self.assertRaises(ValueError):
                    overview(TRIAL_ID, source)

    def test_02_reject_current_or_wrong_historic_version(self):
        for raw in (
            version_bytes(2),
            version_bytes(1,nct_id="NCT99999999"),
            b'{"studyVersion":1,"study":{"protocolSection":{"identificationModule":{"nctId":"NCT03280849"}}}}',
            b'{"protocolSection":{"identificationModule":{"nctId":"NCT03280849"}}}',
            b"bad-json",
        ):
            with self.assertRaises(ValueError):
                historical_content(TRIAL_ID,1,"2018-03-20",raw,"2026-10-18T03:00:00Z")

    def test_03_store_only_two_exact_version_content_receipts(self):
        seen=[]
        def fetch(url):
            seen.append(url)
            if url == endpoint(TRIAL_ID):
                return index_bytes()
            if url == endpoint(TRIAL_ID,0):
                return version_bytes(0,status="RECRUITING")
            if url == endpoint(TRIAL_ID,4):
                return version_bytes(4,status="COMPLETED")
            raise AssertionError("no other URL should be fetched")
        with TemporaryDirectory() as folder:
            result=execute(output_dir=folder,fetch=fetch,
                           now=datetime(2026,10,18,3,tzinfo=timezone.utc))
            self.assertEqual(result["schema"],SCHEMA)
            self.assertEqual(len(seen),3)
            self.assertEqual(len(result["historical_version_receipts"]),2)
            self.assertEqual([r["source_version_index"] for r in result["historical_version_receipts"]],[0,4])
            self.assertEqual([r["selected_historical_field_value"] for r in result["historical_version_receipts"]],["RECRUITING","COMPLETED"])
            self.assertFalse(result["per_version_publication_date_proven"])
            self.assertFalse(result["historical_point_in_time_public_visibility_proven"])
            self.assertFalse(result["additional_native_workstation_job"])
            stored=(Path(folder)/"nih-p2-historical-version-receipts.json").read_text()
            self.assertNotIn("SHOULD NOT ARCHIVE",stored)
            self.assertNotIn("contactsLocationsModule",stored)

    def test_04_reject_changed_selected_version_and_identical_bytes(self):
        def fetch(url):
            if url == endpoint(TRIAL_ID):
                return index_bytes()
            return version_bytes(0)
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                execute(output_dir=folder,fetch=fetch)


if __name__ == "__main__":
    unittest.main()
