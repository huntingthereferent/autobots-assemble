"""Falsification controls: fabricated fixtures are NOT source evidence."""
import unittest
from copy import deepcopy
from scripts.nih_p2_world_calendar_day_model import (
    CUTOFFS,AFTER,NOT_YET,MAYBE,validate_source,projection,independent_oracle,verify_grid)
from network.tests.test_nih_p2_world_posted_day_cross_witness import fixture,join

def case():
    a,b=fixture()
    return join(a,b)

class CalendarDaySourceModelTests(unittest.TestCase):
    def test_01_six_date_only_hypotheses_against_independent_histories(self):
        src=case()
        values=verify_grid(src)
        self.assertEqual([v["day"] for v in values],list(CUTOFFS))
        self.assertEqual([v["possible_latest_versions"] for v in values],
                         [[None],[None,94],[94],[94],[94,105],[105]])
        self.assertEqual([v["statuses"]["105"] for v in values],
                         [NOT_YET,NOT_YET,NOT_YET,NOT_YET,MAYBE,AFTER])
        self.assertTrue(all(v["exact_known_at_utc"] is None for v in values))
    def test_02_same_day_not_midnight_and_static_has_future_leakage(self):
        src=case()
        on=projection(src,"2019-08-02")
        self.assertEqual(on["statuses"]["94"],MAYBE)
        self.assertIn(None,on["possible_latest_versions"])
        self.assertIsNone(on["latest_guaranteed_version"])
        early=projection(src,"2019-08-03")
        self.assertEqual(early["possible_latest_versions"],[94])
        self.assertEqual(early["static_latest_version"],105)
        later=projection(src,"2019-11-25")
        self.assertEqual(later["statuses"]["105"],MAYBE)
        self.assertEqual(later["possible_latest_versions"],[94,105])
    def test_03_denies_unsupported_source_version_or_UTC_certainty(self):
        src=case()
        for key,value in (
            ("exact_first_publication_UTC_instants_authenticated",True),
            ("independently_witnessed_original_public_posting_transactions",True),
            ("no_intervening_changes_proven",True),
            ("executable_source_owned_known_at_instant","2019-08-02T00:00:00Z"),
            ("source_event_2026_fictional_game_chronology_is_separate",False),
            ("original_twelve_job_native_journals_modified",True),
        ):
            bad=deepcopy(src);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_source(bad)
        for day in ("2019-08-02T00:00:00Z","2019-08-04","2026-10-19",None,0):
            with self.subTest(day=day),self.assertRaises(ValueError):
                projection(src,day)
    def test_04_denies_changed_owner_post_day_and_wrong_body_hash(self):
        src=case()
        for index,key,value in (
            (0,"source_named_last_update_posted_day","2019-08-01"),
            (1,"source_named_last_update_posted_day","2019-11-22"),
            (0,"original_page_text_sha256","0"*64),
            (1,"historical_status","COMPLETED"),
            (1,"actual_first_public_instant_and_timezone_authenticated",True),
        ):
            bad=deepcopy(src)
            bad["source_owner_posted_day_claims"][index][key]=value
            with self.subTest(index=index,key=key),self.assertRaises(ValueError):
                validate_source(bad)
    def test_05_no_old_version_can_become_proven_absent_on_same_day(self):
        src=case()
        prev=[]
        for day in CUTOFFS:
            result=projection(src,day)
            oracle=independent_oracle(src,day)
            self.assertEqual(result["possible_latest_versions"],oracle["possible_latest_versions"])
            self.assertTrue(all(x in (NOT_YET,MAYBE,AFTER)
                       for x in result["statuses"].values()))
            self.assertIsNone(result["exact_known_at_utc"])
if __name__=="__main__":unittest.main()
