"""Direct Phase 2 reproduction trial: executable results, not a readiness checklist."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import nih_phase2_direct_reproduction as p


class DirectPhaseTwoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TemporaryDirectory() as td:
            cls.result=p.trial(output_dir=Path(td))
        cls.by_id={case["task"]:case for case in cls.result["cases"]}

    def test_01_actual_original_native_runs_and_fails_hard_phase2_tasks(self):
        r=self.result
        self.assertEqual(r["scored_cases"],13)
        self.assertEqual(r["native_pass"],8)
        self.assertEqual(r["native_fail"],5)
        self.assertEqual(r["static_pass"],6)
        self.assertEqual(r["by_kind"]["fact"]["native_pass"],8)
        self.assertEqual(r["by_kind"]["derived"]["native_pass"],0)
        self.assertEqual(r["by_kind"]["rdf"]["native_pass"],0)
        self.assertFalse(r["phase2_reproduced_in_full"])
        self.assertTrue(r["native_game_control"]["different_from_KG_reasoning"])
        self.assertEqual(r["native_game_control"]["result"],"moved")

    def test_02_original_temporal_program_rejects_future_records(self):
        c=self.by_id["no-future-beta"]
        self.assertTrue(c["native_pass"])
        self.assertFalse(c["native_answer"])
        self.assertFalse(c["static_pass"])
        self.assertTrue(c["static_answer"])
        self.assertIn("therapy-beta",c["original_native_future_leakage_ids"])
        late=self.by_id["care-late"]
        self.assertTrue(late["native_pass"])
        self.assertTrue(late["native_answer"])

    def test_03_original_executable_cannot_infer_actual_sequential_path(self):
        for name in ("infer-sequential-switch","no-premature-sequential-switch",
                     "no-backdated-sequential-switch"):
            r=self.by_id[name]
            self.assertFalse(r["native_pass"])
            self.assertIsNone(r["native_answer"])
            self.assertFalse(r["native_supported"])
        self.assertEqual(self.by_id["infer-sequential-switch"]["expected_answer"],True)

    def test_04_original_executable_leaves_retracted_source_claim_active(self):
        corrected=self.by_id["superseded-claim-not-current"]
        self.assertEqual(corrected["expected_answer"],False)
        self.assertTrue(corrected["native_answer"])
        self.assertFalse(corrected["native_pass"])
        self.assertTrue(self.by_id["correction-present"]["native_pass"])
        self.assertIn("claim-original",corrected["original_native_temporal_ids"])
        self.assertIn("claim-correction",corrected["original_native_temporal_ids"])

    def test_05_rdf_graph_is_measured_by_harness_not_w13_inference(self):
        self.assertFalse(self.result["RDF_output_produced_by_unchanged_native_temporal_executable"])
        rdf=self.by_id["rdf-property-chain-inference"]
        self.assertFalse(rdf["native_supported"])
        self.assertEqual(self.result["RDF_structural_metrics"]["static_KG"]
                         ["logical_inconsistencies_unsatisfiable_classes"],
                         "NOT_MEASURED_NO_OWL_REASONER")
        for side in ("static_KG","temporal_KG_harness_only"):
            m=self.result["RDF_structural_metrics"][side]
            self.assertGreater(m["number_of_triples"],0)
            self.assertGreaterEqual(m["interlinking_completeness_subjects_with_resource_links"],0)
            self.assertLessEqual(m["interlinking_completeness_subjects_with_resource_links"],1)
            self.assertEqual(m["measurement_owner"],
                             "phase2-rehearsal-profiler-not-native-W13")
        self.assertFalse(self.result["all_official_Phase2_metrics_implemented"])

    def test_06_second_biomedical_domain_runs_same_original_executable(self):
        transferred=self.by_id["surveillance-domain-transfer"]
        self.assertTrue(transferred["native_pass"])
        self.assertTrue(transferred["native_answer"])
        self.assertTrue(self.by_id["earlier-guideline"]["native_pass"])
        self.assertTrue(self.by_id["later-guideline"]["native_pass"])

    def test_07_unsupported_capabilities_cannot_be_claimed_as_passed(self):
        r=self.result
        self.assertFalse(r["full_OWL_reasoner_present"])
        self.assertFalse(r["tested_uncertain_source_publication_interval_supported"])
        self.assertFalse(r["real_clinical_benchmark"])
        self.assertFalse(r["official_NIH_shared_benchmark_used"])
        self.assertFalse(r["real_world_clinical_valid_at_authenticated"])
        self.assertFalse(r["official_NIH_phase2_eligibility_or_award"])
        self.assertFalse(r["W13_native_journal_mutated"])
        self.assertFalse(r["World48_required"])

    def test_08_invalid_observations_and_temporal_intervals_refused(self):
        data=deepcopy(p.BIOMED)
        data[0]["valid_to"]=data[0]["valid_from"]
        with self.assertRaises(ValueError):
            p.validated(data)
        data=deepcopy(p.BIOMED)
        data[1]["id"]=data[0]["id"]
        with self.assertRaises(ValueError):
            p.validated(data)
        data=deepcopy(p.BIOMED)
        data[1]["known_at"]="2026-02-30"
        with self.assertRaises(ValueError):
            p.validated(data)
        data=deepcopy(p.BIOMED)
        data[1]["known_at"]=["2026-01-01","2026-01-13"]
        with self.assertRaises(ValueError):
            p.validated(data)

    def test_09_counterfactual_reordering_cannot_fake_sequential_inference(self):
        # Mutating the declared input must not be confused with a native
        # inference from temporal snapshots or path order.
        d=deepcopy(p.BIOMED)
        for row in d:
            if row["id"]=="therapy-beta":
                row["valid_from"]="2026-01-03"
                row["known_at"]="2026-01-03"
        known=p.source_expected(d,known="2026-01-04",target="2026-01-04")
        self.assertIn("therapy-beta",known["temporal"])
        # A row's presence is NOT proof that beta followed inadequate response.
        self.assertNotIn("sequential-switch-inferred",known)


if __name__=="__main__":
    unittest.main()
