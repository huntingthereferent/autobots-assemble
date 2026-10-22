"""Historical source first-public absence is an explicit falsifiable wall."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import unittest
from systems.workspace import nih_p2_original_first_public_gate as gate
from systems.workspace import nih_p2_two_original_source_clocks as parent

REG=os.environ.get("NIH_P2_ORIGINAL_REGISTRY_JSON")
AACT=os.environ.get("NIH_P2_ORIGINAL_AACT_JSON")


def observed_clock():
    return {
        "schema":parent.SCHEMA,
        "real_as_known_at_independently_authenticated":False,
        "real_clinical_valid_at_known":False,
        "historical_NIH_P2_benchmark_completed":False,
        "original_W13_journal_modified":False,
        "conditional_assumption":"source-reported-last-update-posted-only",
        "original_source_version_observations":[{
            "source_version":259,"first_public_version_at":"UNAVAILABLE",
            "clinical_valid_at":"UNAVAILABLE",
            "source_reported_posted_date":"2022-10-27",
            "original_version_source_url":"https://clinicaltrials.gov/example/259",
            "source_retrieved_utc":"2026-10-20T00:00:00Z",
        },{
            "source_version":260,"first_public_version_at":"UNAVAILABLE",
            "clinical_valid_at":"UNAVAILABLE",
            "source_reported_posted_date":"2022-11-07",
            "original_version_source_url":"https://clinicaltrials.gov/example/260",
            "source_retrieved_utc":"2026-10-20T00:00:00Z",
        }],
        "independent_aact_owner_attested_archive_checks":[
            {"original_archive_is_time_authority":False},
            {"original_archive_is_time_authority":False},
        ],
        "conditional_registry_publication_queries":[{},{}],
    }


class HistoricalFirstPublicGateTests(unittest.TestCase):
    def test_conditional_posted_dates_are_not_authenticated_first_public(self):
        result=gate.inspect_source_clock(observed_clock())
        self.assertEqual(result["original_record_versions"],[259,260])
        self.assertEqual(result["real_historical_as_known_at_admission"],
                         "REFUSED_MISSING_INDEPENDENT_WITNESS")
        self.assertEqual(result["independent_exact_version_first_public_at"],
                         "UNAVAILABLE")
        self.assertFalse(result["source_reported_posted_is_independent_first_public_witness"])

    def test_cannot_sneak_in_independent_release_claim_as_json(self):
        with self.assertRaisesRegex(ValueError,"no independent"):
            gate.inspect_source_clock(observed_clock(),
                independent_release_evidence={"claimed_first_public":"2022-11-07"})

    def test_false_first_public_and_archive_clock_promotion_refused(self):
        for changed in (
            ("original_source_version_observations",0,"first_public_version_at",
             "2022-10-27"),
            ("independent_aact_owner_attested_archive_checks",0,
             "original_archive_is_time_authority",True),
        ):
            obj=deepcopy(observed_clock())
            key,index,field,value=changed
            obj[key][index][field]=value
            with self.assertRaises(ValueError):
                gate.inspect_source_clock(obj)

    def test_broken_original_provenance_and_wrong_version_rejected(self):
        for kind in ("bad_version","promote_benchmark","change_assumption"):
            obj=deepcopy(observed_clock())
            if kind=="bad_version":
                obj["original_source_version_observations"][0]["source_version"]=258
            elif kind=="promote_benchmark":
                obj["historical_NIH_P2_benchmark_completed"]=True
            else:
                obj["conditional_assumption"]="authenticated"
            with self.assertRaises(ValueError):
                gate.inspect_source_clock(obj)

    @unittest.skipUnless(REG and AACT,"requires original pinned real-source artifacts")
    def test_live_source_receipts_are_reverified_before_refusal(self):
        result=gate.execute(Path(REG).read_bytes(),Path(AACT).read_bytes())
        self.assertEqual(result["original_record_versions"],[259,260])
        self.assertEqual(result["source_reported_posted_dates"],
                         ["2022-10-27","2022-11-07"])
        self.assertEqual(result["real_historical_as_known_at_admission"],
                         "REFUSED_MISSING_INDEPENDENT_WITNESS")
        self.assertFalse(result["original_W13_modified"])
        self.assertFalse(result["official_NIH_benchmark"])

if __name__=="__main__":
    unittest.main()
