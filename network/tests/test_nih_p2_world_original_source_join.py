"""Negative controls for real original depositor attribution versus synthetic world."""
from copy import deepcopy
import unittest
from scripts.nih_p2_world_original_source_join import check
def records():
    owner={"schema":"nih-p2-2022-aact-owner-script-date-reference/v1",
      "original_source_owner":"lalagkaspn/mendelian_comorbidity_therapeutics",
      "original_source_2022_date_owner_attested":"2022-11-04",
      "earlier_author_commit":"96ccb828b5118e54c658fc1cd386173de67a4b4",
      "linked_author_commit":"675b7a4992d7e2469d368924f4c1f87d7ca162da",
      "earlier_source_witness":{"git_blob_sha1":"3a5781267f15fa69ae1779e47cdb0b4e1f1f0cb6"},
      "linked_source_witness":{"git_blob_sha1":"3e3f8714df2c037cce24961a57802546ce95f7b4"},
      "owner_attested_source_date":True,
      "2022_download_transaction_independently_timestamped":False,
      "individual_registry_version_publication_instants_authenticated":False}
    game={"schema":"world-nih-p2-synthetic-source-event-chronology/v1",
       "original_native_jobs":12,"source_event_count":3,
       "source_events_are_constructed_not_authenticated":True,
       "source_signature_authenticated":False,
       "original_native_journals_unchanged":True}
    return owner,game
class NativeWorldExternalSourceTest(unittest.TestCase):
    def test_01_preserves_two_distinct_evidence_owners(self):
        x,y=records()
        z=check(x,y)
        self.assertTrue(z["pinned_git_source_file_blobs_verified"])
        self.assertFalse(z["source_owner_statement_joined_to_fictional_game_events"])
        self.assertFalse(z["historical_registry_version_timestamp_verified"])
    def test_02_refuse_unwitnessed_owner_and_timestamp_promotion(self):
        for key,v in (("original_source_2022_date_owner_attested","2022-11-09"),
          ("original_source_owner","unknown"),
          ("linked_author_commit","f"*40),
          ("2022_download_transaction_independently_timestamped",True),
          ("individual_registry_version_publication_instants_authenticated",True),
          ("owner_attested_source_date",False)):
            a,b=records();a[key]=v
            with self.subTest(key=key),self.assertRaises(ValueError):check(a,b)
    def test_03_refuse_fictional_events_relabelled_original(self):
        for key,v in (("source_signature_authenticated",True),
          ("source_events_are_constructed_not_authenticated",False),
          ("original_native_jobs",11),("original_native_journals_unchanged",False),
          ("source_event_count",4)):
            a,b=records();b[key]=v
            with self.subTest(key=key),self.assertRaises(ValueError):check(a,b)
    def test_04_refuse_wrong_original_git_blobs(self):
        for key in ("earlier_source_witness","linked_source_witness"):
            a,b=records()
            a[key]["git_blob_sha1"]="0"*40
            with self.subTest(key=key),self.assertRaises(ValueError):check(a,b)
if __name__=="__main__":unittest.main()
