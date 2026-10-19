"""Mock receipts are falsification controls, never original registry evidence."""
from copy import deepcopy
import unittest
from scripts.nih_p2_world_posted_day_cross_witness import (
    join,SCHEMA,KNOWN_BODY_HASHES,EXPECTED_SUBMITTED,EXPECTED_OWNER_FIELD)

def fixture():
    statuses=[]
    dates=[]
    for i,v in enumerate((94,105)):
        h=KNOWN_BODY_HASHES[i]
        day=EXPECTED_OWNER_FIELD[i]
        url=f"https://clinicaltrials.gov/study/NCT00001756?a={v}&tab=history"
        statuses.append({"version":v,"url":url,"version_page_independently_visible":True,
            "version_detail_status_authenticated":True,"version_detail_status":"RECRUITING",
            "original_source_body_sha256":h})
        dates.append({"version":v,"url":url,"original_version_visible":True,
            "owner_browser_visible_body_sha256":h,
            "submission_date_owner_recorded":EXPECTED_SUBMITTED[i],
            "posted_at_authenticated":False,
            "version_submitted_at_is_not_version_posted_at":True,
            "current_header_last_update_posted_cannot_establish_version_posting":True,
            "selected_version_detail_posting_field_label_count":1,
            "selected_version_detail_posting_field_dates":[
                {"label":"Last Update Posted","following_iso_dates":[day]}]})
    return ({"schema":"world-nih-p2-original-version-field-probe/v1",
             "nct_id":"NCT00001756","version_records":statuses,
             "independent_historical_version_status_count":2},
            {"schema":"world-nih-p2-original-version-posting-field-access/v1",
             "study":"NCT00001756","records":dates,
             "history_query_without_posted_at":"BLOCKED_PENDING_OWNER_POSTING_EVIDENCE",
             "original_per_version_first_posted_instants_authenticated":False,
             "admissible_temporal_known_at":None})

class OriginalSourceCrossWitnessTests(unittest.TestCase):
    def test_01_two_original_page_hashes_and_source_named_dates(self):
        a,b=fixture()
        result=join(a,b)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual([x["source_named_last_update_posted_day"]
                          for x in result["source_owner_posted_day_claims"]],list(EXPECTED_OWNER_FIELD))
        self.assertFalse(result["exact_first_publication_UTC_instants_authenticated"])
        self.assertFalse(result["no_intervening_changes_proven"])
        self.assertIsNone(result["executable_source_owned_known_at_instant"])
    def test_02_fake_field_version_hash_and_day_rejected(self):
        for side,index,key,value in (
            ("a",0,"original_source_body_sha256","f"*64),
            ("b",1,"owner_browser_visible_body_sha256","0"*64),
            ("a",1,"version",106),
            ("b",0,"url","https://clinicaltrials.gov/study/NCT00001757?a=94&tab=history"),
            ("b",0,"submission_date_owner_recorded","2019-08-03"),
            ("b",0,"selected_version_detail_posting_field_label_count",0),
            ("b",1,"posted_at_authenticated",True),
            ("a",1,"version_detail_status","COMPLETED"),
            ("a",0,"version_detail_status_authenticated",False),
        ):
            a,b=fixture()
            other=a if side=="a" else b
            other["version_records" if side=="a" else "records"][index][key]=value
            with self.subTest(side=side,index=index,key=key),self.assertRaises(ValueError):
                join(a,b)
    def test_03_current_header_or_fabricated_posted_field_rejected(self):
        for data in (
            [{"label":"Last Update Posted","following_iso_dates":["2026-10-19"]}],
            [{"label":"Date submitted","following_iso_dates":["2019-08-01"]}],
            [{"label":"Last Update Posted","following_iso_dates":[]}],
            [],
        ):
            a,b=fixture()
            b["records"][0]["selected_version_detail_posting_field_dates"]=data
            with self.subTest(fake=data),self.assertRaises(ValueError):join(a,b)
    def test_04_missing_falsifying_source_evidence_refused(self):
        a,b=fixture()
        a["version_records"]=a["version_records"][:1]
        with self.assertRaises(ValueError):join(a,b)
        a,b=fixture()
        b["admissible_temporal_known_at"]="2019-08-02T00:00:00Z"
        with self.assertRaises(ValueError):join(a,b)
if __name__=="__main__":
    unittest.main()
