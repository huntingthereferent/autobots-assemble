"""Negative controls: never treat fixtures as original version publication evidence."""
from copy import deepcopy
import unittest
from scripts.nih_p2_world_version_posting_probe import (
    VERSIONS,SCHEMA,exact_url,SUBMITTED,selected_version_dates,verify_pair)

def page(v,*,old_post=None,header_post="2026-10-01",submitted=None):
    day=submitted or SUBMITTED[v]
    details="Study Details\nStudy Status\nOverall Status\nRecruiting\n"
    if old_post is not None:
        details+="Study Record Dates\nLast Update Posted\n"+old_post+"\n"
    body=(f"Study of Mast Cell Precursors\nNCT00001756\n"
          f"Last Update Posted\n{header_post}\n"
          "Study Record Versions\nDate submitted\n"
          f"Viewing V{v} ({day})\n"+details)
    title=f"Record History | ver. {v}: {day} | NCT00001756 | ClinicalTrials.gov"
    return selected_version_dates(version=v,url=exact_url(v),status=200,title=title,
        body=body,observed="2026-10-19T08:00:00+00:00")

class VersionPostingFieldNegativeTests(unittest.TestCase):
    def test_01_current_study_header_never_becomes_historical_posted_at(self):
        v=page(94,header_post="2026-10-01")
        self.assertTrue(v["original_version_visible"])
        self.assertEqual(v["current_or_history_header_last_update_posted_label_count"],1)
        self.assertEqual(v["selected_version_detail_posting_field_label_count"],0)
        self.assertFalse(v["posted_at_authenticated"])
        self.assertTrue(v["version_submitted_at_is_not_version_posted_at"])
    def test_02_selected_version_label_does_not_independently_prove_public_access(self):
        v=page(105,old_post="2019-11-25")
        self.assertEqual(v["selected_version_detail_posting_field_dates"],
             [{"label":"Last Update Posted","following_iso_dates":["2019-11-25"]}])
        self.assertFalse(v["posted_at_authenticated"])
        self.assertFalse(v["exact_first_publication_instant_authenticated"])
    def test_03_missing_or_wrong_original_selected_version_blocks(self):
        with self.assertRaises(ValueError):
            page(94,submitted="2019-08-02")
        for v in (1,93,106,"94"):
            with self.subTest(version=v),self.assertRaises(ValueError):
                exact_url(v)
    def test_04_refuse_promoted_submission_date_and_invented_time(self):
        a,b=page(94),page(105)
        r=verify_pair([a,b])
        self.assertEqual(r["schema"],SCHEMA)
        self.assertIsNone(r["admissible_temporal_known_at"])
        self.assertFalse(r["original_per_version_first_posted_instants_authenticated"])
        for key,val in (("posted_at_authenticated",True),
                        ("version_submitted_at_is_not_version_posted_at",False),
                        ("submission_date_owner_recorded","2019-11-22"),
                        ("current_header_last_update_posted_cannot_establish_version_posting",False)):
            fake=deepcopy(a);fake[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify_pair([fake,b])
        with self.assertRaises(ValueError):verify_pair([b,a])
        with self.assertRaises(ValueError):verify_pair([a])
    def test_05_source_route_and_status_cannot_be_forged(self):
        v=page(94)
        tampered=deepcopy(v);tampered["url"]=exact_url(105)
        with self.assertRaises(ValueError):verify_pair([tampered,page(105)])
if __name__=="__main__":
    unittest.main()
