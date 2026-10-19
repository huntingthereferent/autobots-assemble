"""Negative controls are fabricated; they never authenticate real registry versions."""
import unittest
from copy import deepcopy
from scripts.nih_p2_world_history_field_probe import candidate,verify_receipt,exact_url
def text(v,field="Overall Status\nCOMPLETED"):
    return (f"Study of Mast Cell Precursors NCT00001756 Recruitment Status Recruiting\n"
        "Record History Study Record Versions\n"
        f"Viewing V{v} (2019-01-01)\n"
        "Study Details\n"+field+"\n")
def page(v,content=None,status=200):
    return candidate(url=exact_url(v),status=status,
        body=text(v) if content is None else content,version=v,
        page_title="Original record history",observed="2026-10-19T08:00:00+00:00")

class OfficialHistoryFieldTests(unittest.TestCase):
    def test_01_real_version_details_field_is_distinct_from_current_header(self):
        p=page(94)
        self.assertTrue(p["version_detail_status_authenticated"])
        self.assertEqual(p["version_detail_status"],"COMPLETED")
        self.assertFalse(p["per_version_original_posting_date_authenticated"])
        self.assertNotEqual(p["version_detail_status"],"RECRUITING")
    def test_02_version_banner_and_details_required_not_current_header(self):
        scenarios=[
            text(94).replace("Viewing V94","Viewing V105"),
            text(94).replace("Study Details","Other Details"),
            text(94).replace("Study Details\nOverall Status\nCOMPLETED","Study Details"),
            text(94).replace("NCT00001756","NCT00000000"),
            text(94).replace("Study Record Versions","Current Record"),
        ]
        for c in scenarios:
            with self.subTest(c=c[:60]):
                self.assertFalse(page(94,c)["version_detail_status_authenticated"])
        self.assertFalse(page(94,text(94),403)["version_detail_status_authenticated"])
    def test_03_ambiguous_old_fields_not_authenticated(self):
        q=page(94,text(94,"Overall Status\nCOMPLETED\nRecruitment Status\nRECRUITING"))
        self.assertEqual(q["recruitment_field_candidates_in_details"],2)
        self.assertFalse(q["version_detail_status_authenticated"])
        # A coincident current header cannot substitute for absent old field
        self.assertFalse(page(94,text(94,"Not published"))["version_detail_status_authenticated"])
    def test_04_two_exact_version_ids_and_time_boundary(self):
        r=verify_receipt([page(94),page(105)])
        self.assertEqual(r["independent_historical_version_status_count"],2)
        self.assertFalse(r["per_version_first_public_posting_instants_authenticated"])
        with self.assertRaises(ValueError):verify_receipt([page(94)])
        with self.assertRaises(ValueError):verify_receipt([page(105),page(94)])
        bad=page(105)
        bad["per_version_original_posting_date_authenticated"]=True
        with self.assertRaises(ValueError):verify_receipt([page(94),bad])
    def test_05_version_url_cannot_be_replaced_or_forged(self):
        for ver in ("94",93,106,1,0,None):
            with self.subTest(version=ver),self.assertRaises(ValueError):
                exact_url(ver)
        wrong=page(94);wrong["url"]=exact_url(105)
        with self.assertRaises(ValueError):verify_receipt([wrong,page(105)])
if __name__=="__main__":unittest.main()
