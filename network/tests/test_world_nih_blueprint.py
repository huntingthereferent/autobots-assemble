"""WORLD Phase 1-contained Phase 2 blueprint semantic falsification tests."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from systems.workspace.world_temporal_blueprint import (
  ROOMS,VERSION,digest,validate,evaluate,graph)

FIXTURE=Path(__file__).resolve().parent/"fixtures/world_nih_phase1_phase2_blueprint_v1.json"

def original():
    return json.loads(FIXTURE.read_text())

class WorldNIHBlueprintTests(unittest.TestCase):
    def test_01_original_w13_rooms_and_five_clocks_preserved(self):
        b=validate(original())
        self.assertEqual(b["schema"],VERSION)
        self.assertEqual(b["base_world"]["rooms"],ROOMS)
        self.assertEqual(len(b["clocks"]),5)
        self.assertEqual(b["base_world"]["advance"],"explicit-only-after-first-collection")
        self.assertEqual(b["research_context"]["phase2"],"planned-implementation-blueprint-in-phase1")

    def test_02_source_change_rebuilds_real_graph_and_temporal_result(self):
        b=original()
        initial=evaluate(b,"synthetic")
        self.assertEqual(initial["eligible"],["prior-note"])
        self.assertEqual(initial["withheld_future"],["delayed-result"])
        self.assertEqual(initial["static_future_leakage"],["delayed-result"])
        nodes=graph(b,"synthetic")
        self.assertEqual(len(nodes["nodes"]),12)
        self.assertEqual(len(nodes["edges"]),10)
        self.assertEqual([n["lane"] for n in nodes["nodes"][:6]],b["graph_layout"]["lanes"])
        old=digest(b)
        b["sample_sets"]["synthetic"][1]["known_day"]="2026-01-03"
        b["sample_sets"]["synthetic"][1]["object"]="different-observation"
        self.assertNotEqual(digest(b),old)
        next=evaluate(b,"synthetic")
        self.assertEqual(next["eligible"],["prior-note","delayed-result"])
        self.assertEqual(next["withheld_future"],[])
        self.assertEqual(next["static_future_leakage"],[])
        self.assertIn("different-observation",graph(b,"synthetic")["nodes"][7]["label"])

    def test_03_half_open_target_and_five_clocks_are_not_interchangeable(self):
        b=original()
        b["queries"]["synthetic"]["valid_target"]="2026-01-10"
        res=evaluate(b,"synthetic")
        self.assertEqual(res["eligible"],[])
        self.assertEqual(res["outside_validity"],["prior-note","delayed-result"])
        b["queries"]["synthetic"]["valid_target"]="2026-01-04"
        b["queries"]["synthetic"]["knowledge_cutoff"]="2026-01-06"
        res=evaluate(b,"synthetic")
        self.assertEqual(res["eligible"],["prior-note","delayed-result"])

    def test_04_original_registry_fields_have_unknown_validity_and_exact_hour(self):
        b=original()
        result=evaluate(b,"registry")
        self.assertEqual(result["eligible"],[])
        self.assertEqual(result["static_union_valid"],[])
        self.assertEqual(result["unresolved_validity"],["ctgov-v94","ctgov-v105"])
        self.assertEqual(result["owner_day_states"],{
            "ctgov-v94":"AFTER_OWNER_REPORTED_DAY",
            "ctgov-v105":"SAME_DAY_TIME_UNRESOLVED"})
        self.assertIs(result["publication_instant_authenticated"],False)
        self.assertTrue(all("UNKNOWN validity" in n["label"] for n in graph(b,"registry")["nodes"]
            if n["lane"]=="valid interval"))

    def test_05_forbid_fake_owner_date_hash_missing_time_and_geometry_promotion(self):
        fixtures=[
          ("sample_sets","registry",0,"posted_day","2019-08-01"),
          ("sample_sets","registry",1,"known_day","2019-11-25"),
          ("sample_sets","registry",1,"source_text_sha256","0"*64),
          ("sample_sets","registry",0,"valid_from","2019-08-02"),
          ("sample_sets","registry",0,"provenance_state","synthetic"),
          ("sample_sets","synthetic",1,"valid_to","2026-01-02"),
        ]
        for group,mode,index,key,val in fixtures:
            b=original();b[group][mode][index][key]=val
            with self.subTest(key=key,mode=mode),self.assertRaises(ValueError):
                validate(b)
        b=original();b["base_world"]["rooms"][0]["spec"]["width"]=6
        with self.assertRaises(ValueError):validate(b)
        b=original();b["queries"]["registry"]["valid_target"]="2019-11-25"
        with self.assertRaises(ValueError):validate(b)
        b=original();b["source_policy"]["strict_original_publication_instant"]="2019-11-25T00:00:00Z"
        with self.assertRaises(ValueError):validate(b)

    def test_06_2d_projection_scale_changes_no_knowledge_graph_semantics(self):
        b=original();base=evaluate(b,"synthetic")
        b["graph_layout"]["columns"]=12
        self.assertEqual(base["eligible"],evaluate(b,"synthetic")["eligible"])
        self.assertEqual(graph(b,"synthetic")["columns"],12)
        for size in (0,2,13,True,"6"):
            c=deepcopy(b);c["graph_layout"]["columns"]=size
            with self.subTest(size=size),self.assertRaises(ValueError):validate(c)
    def test_07_graph_expansion_does_not_expand_physical_rooms(self):
        b=original()
        new=deepcopy(b["sample_sets"]["synthetic"][1])
        new.update(id="synthetic-added-1",source_ref="synthetic-added-source",object="added-observation")
        b["sample_sets"]["synthetic"].append(new)
        validate(b)
        self.assertEqual(len(graph(b,"synthetic")["nodes"]),18)
        self.assertEqual(b["base_world"]["rooms"],ROOMS)
        out=evaluate(b,"synthetic")
        self.assertEqual(out["withheld_future"],["delayed-result","synthetic-added-1"])
        self.assertEqual(out["static_future_leakage"],["delayed-result","synthetic-added-1"])
        b["sample_sets"]["synthetic"].append(deepcopy(new))
        with self.assertRaises(ValueError):validate(b)
if __name__=="__main__":unittest.main()
