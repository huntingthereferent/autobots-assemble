"""Behavioral falsification for the finite A/B source-relationship chain."""
from __future__ import annotations

from copy import deepcopy
from datetime import date,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import ab_time_respecting_source_chain as chain
from systems.workspace import nih_phase2_direct_reproduction as old
from systems.workspace import nih_phase2_time_respecting_chain_trial as trial


class GenericTimeRespectingChainTests(unittest.TestCase):
    def test_01_actual_declared_sequence_has_original_three_source_witnesses(self):
        result=chain.observe(old.BIOMED,trial.STAGES,
            known_at="2026-01-11",target_at="2026-01-11",
            subject="fictional-cohort")
        self.assertTrue(result["path_exists"])
        self.assertTrue(result["exhaustive_within_declared_scope"])
        self.assertEqual(result["witnesses"][0]["evidence_ids"],
                         ["therapy-alpha","response-poor","therapy-beta"])
        self.assertEqual(result["witnesses"][0]["event_starts"],
                         ["2026-01-04","2026-01-06","2026-01-09"])
        self.assertEqual(result["witnesses"][0]["source_references"],
                         ["synthetic-care-sequence"]*3)
        self.assertFalse(result["causal_conclusion"])
        self.assertFalse(result["clinical_validity_independently_authenticated"])

    def test_02_expired_first_event_still_part_of_historical_path(self):
        r=chain.observe(old.BIOMED,trial.STAGES,
            known_at="2026-01-11",target_at="2026-01-11",
            subject="fictional-cohort")
        self.assertTrue(r["path_exists"])
        self.assertLess(old.BIOMED[0]["valid_to"],"2026-01-11")
        selected=old.source_expected(old.BIOMED,
                                    known="2026-01-11",target="2026-01-11")
        self.assertNotIn("therapy-alpha",selected["temporal"])

    def test_03_future_knowledge_or_backdating_refuses_true_path(self):
        for known,target in (
            ("2026-01-07","2026-01-11"),
            ("2026-01-11","2026-01-07"),
            ("2026-01-08","2026-01-08"),
        ):
            with self.subTest(known=known,target=target):
                r=chain.observe(old.BIOMED,trial.STAGES,
                    known_at=known,target_at=target,subject="fictional-cohort")
                self.assertFalse(r["path_exists"])
                self.assertEqual(r["witnesses"],[])
                self.assertTrue(r["exhaustive_within_declared_scope"])

    def test_04_same_day_or_reversed_event_starts_do_not_count_as_chain(self):
        for changed in ("2026-01-06","2026-01-03"):
            rows=deepcopy(old.BIOMED)
            next(x for x in rows if x["id"]=="therapy-beta")["valid_from"]=changed
            report=chain.observe(rows,trial.STAGES,known_at="2026-01-20",
                target_at="2026-01-20",subject="fictional-cohort")
            self.assertFalse(report["path_exists"])
        rows=deepcopy(old.BIOMED)
        next(x for x in rows if x["id"]=="response-poor")["valid_from"]="2026-01-04"
        report=chain.observe(rows,trial.STAGES,known_at="2026-01-20",
            target_at="2026-01-20",subject="fictional-cohort")
        self.assertFalse(report["path_exists"])

    def test_05_subjects_cannot_be_spliced_into_false_path(self):
        rows=deepcopy(old.BIOMED)
        next(x for x in rows if x["id"]=="response-poor")["subject"]="unrelated-cohort"
        result=chain.observe(rows,trial.STAGES,known_at="2026-01-20",
            target_at="2026-01-20")
        self.assertFalse(result["path_exists"])

    def test_06_generic_surveillance_events_not_treatment_hardcoding(self):
        def row(i,stage,start,subject="fictional-region"):
            return old.obs(f"variant-sequence-{i}",stage["predicate"],
                stage["object"],start,"2026-02-01",start,
                source="synthetic-epidemiology",subject=subject)
        data=[row(0,trial.SURVEILLANCE_STAGES[0],"2026-01-03"),
              row(1,trial.SURVEILLANCE_STAGES[1],"2026-01-05"),
              row(2,trial.SURVEILLANCE_STAGES[2],"2026-01-07")]
        r=chain.observe(data,trial.SURVEILLANCE_STAGES,
                        known_at="2026-01-08",target_at="2026-01-08",
                        subject="fictional-region")
        self.assertTrue(r["path_exists"])
        self.assertEqual([w["evidence_ids"] for w in r["witnesses"]],
                         [["variant-sequence-0","variant-sequence-1",
                           "variant-sequence-2"]])
        self.assertTrue(trial.independent_check(data,trial.SURVEILLANCE_STAGES,
            "2026-01-08","2026-01-08",r,subject="fictional-region")["cross_checked"])

    def test_07_exceeding_finite_path_capacity_is_error_not_false(self):
        all_rows=[]
        for idx,stage in enumerate(trial.STAGES):
            for j in range(6):
                day=(date(2026,1,1)+timedelta(days=idx*8+j+1)).isoformat()
                all_rows.append(old.obs(
                    f"witness-{idx}-{j}",stage["predicate"],stage["object"],
                    day,"2026-02-01",day,source="synthetic-many-paths"))
        with self.assertRaisesRegex(ValueError,"path witness limit exceeded"):
            chain.observe(all_rows,trial.STAGES,known_at="2026-01-31",
                          target_at="2026-01-31")

    def test_08_source_schema_dates_id_and_pattern_tampering_rejected(self):
        rows=deepcopy(old.BIOMED)
        bad=[None,"2026-01", "2026-02-30",["2026-01-11"]]
        for cutoff in bad:
            with self.subTest(cutoff=cutoff),self.assertRaises(ValueError):
                chain.observe(rows,trial.STAGES,known_at=cutoff,
                              target_at="2026-01-11")
        mutated=deepcopy(rows)
        mutated[1]["id"]=mutated[0]["id"]
        with self.assertRaises(ValueError):
            chain.observe(mutated,trial.STAGES,
                          known_at="2026-01-11",target_at="2026-01-11")
        mutated=deepcopy(rows)
        mutated[0]["extra"]="danger"
        with self.assertRaises(ValueError):
            chain.observe(mutated,trial.STAGES,
                          known_at="2026-01-11",target_at="2026-01-11")
        mutated=deepcopy(trial.STAGES)
        mutated[0]["object"]="Alpha"
        with self.assertRaises(ValueError):
            chain.observe(rows,mutated,
                          known_at="2026-01-11",target_at="2026-01-11")
        with self.assertRaises(ValueError):
            chain.observe(rows,trial.STAGES[:1],
                          known_at="2026-01-11",target_at="2026-01-11")

    @classmethod
    def setUpClass(cls):
        with TemporaryDirectory() as tmp:
            cls.run=trial.run(output_dir=Path(tmp))
        cls.by_id={t["task"]:t for t in cls.run["original_13_case_results"]}

    def test_09_replay_original_exact_13_question_score_without_modification(self):
        r=self.run
        self.assertEqual(r["original_13_case_scores"],
                         {"W13":8,"static":6,"cases":13})
        self.assertEqual(r["with_bounded_generic_source_chain"],
                         {"passed":11,"cases":13,"improved_by":3})
        self.assertEqual(r["by_kind"]["derived"],
                         {"cases":3,"original_pass":0,"new_pass":3})
        self.assertEqual(r["by_kind"]["rdf"],
                         {"cases":1,"original_pass":0,"new_pass":0})
        self.assertFalse(r["original_native_W13_engine_changed"])
        self.assertFalse(r["Phase2_fully_reproduced"])
        self.assertFalse(r["World48_required"])
        self.assertFalse(r["research_evidence_supersession_supported"])
        self.assertFalse(r["biomedical_OWL_property_chain_supported"])

    def test_10_positive_and_two_negative_derived_answers_have_evidence(self):
        for key,expected in (
            ("infer-sequential-switch",True),
            ("no-premature-sequential-switch",False),
            ("no-backdated-sequential-switch",False),
        ):
            row=self.by_id[key]
            self.assertIs(row["new_source_chain_answer"],expected)
            self.assertIsNone(row["original_native_answer"])
            self.assertTrue(row["new_pass"])
            self.assertTrue(row["evidence"]["original_W13_emitted_Python_still_lacks_this_output"])
        self.assertEqual(len(self.by_id["infer-sequential-switch"]
                             ["evidence"]["witness_paths"]),1)
        self.assertEqual(self.by_id["no-premature-sequential-switch"]
                         ["evidence"]["witness_paths"],[])

    def test_11_unseen_cross_domain_160_cases_have_both_outcomes_and_oracle(self):
        r=self.run["unseen_generated"]
        self.assertEqual(r["cases"],160)
        self.assertEqual(r["verified_by_independent_cartesian_oracle"],160)
        self.assertGreater(r["positive_cases"],0)
        self.assertGreater(r["negative_cases"],0)
        self.assertEqual(r["positive_cases"]+r["negative_cases"],160)
        self.assertEqual(set(x["domain"] for x in r["cases_detail"]),
                         {"care","surveillance"})
        self.assertTrue(all(x["answer"]==x["independent_answer"] for x in r["cases_detail"]))

    def test_12_correction_and_rdf_still_fail_for_correct_reasons(self):
        for key in ("superseded-claim-not-current","rdf-property-chain-inference"):
            item=self.by_id[key]
            self.assertFalse(item["new_pass"])
        self.assertTrue(self.run["longitudinal_observation_supported"])
        self.assertFalse(self.run["causal_therapy_change_inferred"])
        self.assertFalse(self.run["clinical_event_valid_at_authenticated"])


if __name__=="__main__":
    unittest.main()
