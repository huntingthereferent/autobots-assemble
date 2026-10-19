"""Negative controls for original-world joint evidence; mocks are not live witnesses."""
from copy import deepcopy
import unittest

from scripts.nih_p2_original_world_joint_witness import relate, SCHEMA

C=("2026-01-03","2026-01-04","2026-01-06","2026-01-07")
P=("original","later-knowledge","additional-conflict")

def originals():
    src=[]
    bounds=[]
    for t in range(5):
        known="2026-01-04" if t<2 else "2026-01-06"
        for p in P:
            admitted=["prior-note"]
            withheld=["delayed-result"]
            conflict=[]
            if p=="original" and t>=2:
                admitted=["delayed-result","prior-note"]
                withheld=[]
            if p=="additional-conflict":
                admitted+=["synthetic-extra-conflict"]
                conflict=[["prior-note","synthetic-extra-conflict"]]
                if t>=2:
                    admitted.insert(0,"delayed-result")
                    withheld=[]
            src.append({
                "turn":t,"profile":p,"known_at":known,"target_at":"2026-01-04",
                "temporal_ids":admitted,"future_leakage_ids":withheld,
                "declared_conflicts":conflict,
                "source_program_sha256":"e"*64,
                "source_dataset_sha256":{"original":"a"*64,
                    "later-knowledge":"b"*64,"additional-conflict":"c"*64}[p],
                "independent_source_oracle_agreed":True})
        for k in C:
            bounds.append({
                "turn":t,"known_at":k,"native_game_known_at":known,
                "target_at":"2026-01-04","source_program_sha256":"e"*64,
                "independent_source_policy_agreement":True,
                "static_valid_ids":["delayed-result","prior-note"],
                "indeterminate_ids":["delayed-result"] if k in C[1:3] else [],
                "admitted_ids":["delayed-result","prior-note"] if k==C[3] else ["prior-note"],
                "definitely_withheld_ids":["delayed-result"] if k==C[0] else []})
    motion={"schema":"nih-phase1-original-world-source-motion/v1",
        "native_jobs":12,"actual_world_solved":True,
        "original_journals_preserved":True,"source_partition_verified":True,
        "new_native_job":False,"new_NIH_checkpoint":False,
        "real_historical_registry_version_authenticated":False,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "official_NIH_submission":False,"actual_world_actions":4,
        "selected_counterfactual_profiles":list(P),
        "original_emitted_python_sha256":"e"*64,
        "source_profile_sha256":{"original":"a"*64,"later-knowledge":"b"*64,
                                "additional-conflict":"c"*64},
        "actual_browser_source_frames":src,
        "independently_verified_original_python_calls":[{}]*15}
    uncertainty={"schema":"nih-phase1-original-world-publication-uncertainty/v1",
        "original_native_jobs":12,"played_original_game_solved":True,
        "original_native_journals_preserved":True,
        "independent_three_state_policy_verified":True,
        "new_native_job":False,"new_NIH_checkpoint":False,
        "real_historical_publication_authenticated":False,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "official_NIH_submission":False,"world_actions":4,
        "cutoff_choices":list(C),
        "original_emitted_python_sha256":"e"*64,
        "observed_browser_frames":bounds,
        "actual_original_python_calls":[{}]*20}
    return motion,uncertainty

class JointWorldWitnessTests(unittest.TestCase):
    def test_01_distinguish_exact_synthetic_status_from_unknown_publication(self):
        a,b=originals()
        r=relate(a,b)
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["source_browser_frames"],15)
        self.assertEqual(r["publication_browser_frames"],20)
        self.assertEqual(r["new_original_python_calls"],35)
        self.assertEqual(r["native_cutover_turn"],2)
        self.assertEqual([x["exact_synthetic_known_at_projection"]
                          for x in r["exact_vs_unknown_publication_counterexamples"]],
                         ["WITHHELD","ADMITTED"])
        self.assertEqual({x["bounded_hypothetical_publication_projection"]
                          for x in r["exact_vs_unknown_publication_counterexamples"]},
                         {"INDETERMINATE"})
        self.assertFalse(r["real_historical_publication_authenticated"])
        self.assertEqual(r["new_native_jobs"],0)

    def test_02_refute_fake_lineage_fields_and_promoted_claims(self):
        for source,field,val in (
            ("a","native_jobs",11),("a","new_NIH_checkpoint",True),
            ("a","source_partition_verified",False),
            ("a","real_historical_registry_version_authenticated",True),
            ("b","independent_three_state_policy_verified",False),
            ("b","original_native_jobs",11),("b","official_NIH_submission",True),
            ("b","real_historical_publication_authenticated",True),
            ("b","world_actions",3),
            ("b","original_emitted_python_sha256","0"*64)):
            a,b=originals()
            obj=a if source=="a" else b
            obj[field]=val
            with self.subTest(source=source,field=field),self.assertRaises(ValueError):
                relate(a,b)

    def test_03_refute_mismatched_frames_and_false_clock(self):
        for source,i,key,value in (
            ("a",0,"source_program_sha256","0"*64),
            ("a",0,"source_dataset_sha256","0"*64),
            ("a",0,"independent_source_oracle_agreed",False),
            ("a",1,"known_at","2026-01-06"),
            ("a",2,"declared_conflicts",[]),
            ("a",6,"temporal_ids",["prior-note"]),
            ("b",0,"native_game_known_at","2026-01-06"),
            ("b",1,"indeterminate_ids",[]),
            ("b",0,"independent_source_policy_agreement",False)):
            a,b=originals()
            obj=a if source=="a" else b
            rows=obj["actual_browser_source_frames" if source=="a" else "observed_browser_frames"]
            rows[i][key]=value
            with self.subTest(source=source,index=i,key=key),self.assertRaises(ValueError):
                relate(a,b)

    def test_04_missing_and_duplicate_browser_evidence_refused(self):
        for source in ("a","b"):
            a,b=originals()
            rows=(a if source=="a" else b)[
                "actual_browser_source_frames" if source=="a" else "observed_browser_frames"]
            rows.pop()
            with self.assertRaises(ValueError): relate(a,b)
            a,b=originals()
            rows=(a if source=="a" else b)[
                "actual_browser_source_frames" if source=="a" else "observed_browser_frames"]
            rows[1]=deepcopy(rows[0])
            with self.assertRaises(ValueError): relate(a,b)

if __name__=="__main__":
    unittest.main()
