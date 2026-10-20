"""Bounded world construction and separate receipt reconstruction tests."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from work.ab_world.construction import load_json, run_plan, PLAN
from work.ab_world.verify_construction import verify_receipt

SAMPLE = Path(__file__).parent / "fixtures/ab_world_construction_example.json"
D = {"kind": "declared", "source": "test/candidate"}
R = {"kind": "external-report", "source": "test/source-unverified"}


def start(steps, objects=4, relations=4):
    return {"schema": PLAN, "referent": "untyped research referent",
            "limits": {"objects": objects, "relations": relations, "steps": 40},
            "steps": steps}


def obj(ident, state=None):
    return {"op": "introduce", "id": ident, "state": state or {}, "basis": D}


class GeneralConstructionTests(unittest.TestCase):
    def test_01_report_does_not_rewrite_declared_object(self):
        trace = run_plan(load_json(SAMPLE))
        witness = verify_receipt(trace)
        self.assertEqual(witness["steps_verified"], 6)
        self.assertEqual(trace["final"]["objects"]["moving-part"]["angle"]["value"], 30)
        self.assertEqual(trace["final"]["observations"]["angle-reading"]["reading"]["angle"]["value"], 29.8)
        self.assertEqual(trace["final"]["comparisons"]["angle-contrast"]["result"], "DIFFERENT")
        self.assertFalse(witness["physical_behavior_verified"])
        self.assertFalse(witness["external_source_authenticated"])

    def test_02_nonspatial_nih_like_relations(self):
        rows = [obj("clinical-note", {"available_at": "2026-01-01"}),
                obj("snapshot", {"known_at": "2026-01-02"}),
                {"op": "connect", "id": "seen-at", "from": "snapshot", "to": "clinical-note",
                 "label": "knowledge-availability", "state": {"as_of": "2026-01-02"},
                 "basis": D},
                {"op": "revise", "entity": "relation", "id": "seen-at",
                 "after": {"as_of": "2026-01-03", "review": "pending"}, "basis": D}]
        result = run_plan(start(rows))
        self.assertEqual(result["final"]["relations"]["seen-at"]["state"]["review"], "pending")
        self.assertEqual(verify_receipt(result)["relations_live"], 1)
        self.assertNotIn("x", result["final"]["objects"]["snapshot"])

    def test_03_exact_match_and_unit_mismatch_not_converted(self):
        rows = [obj("x"), {"op": "observe", "id": "o", "entity": "object", "subject": "x",
                           "reading": {"distance": {"value": 1, "unit": "m"}}, "basis": R},
                {"op": "compare", "id": "same", "observation": "o",
                 "expected": {"distance": {"value": 1, "unit": "m"}}, "basis": D},
                {"op": "compare", "id": "different-unit", "observation": "o",
                 "expected": {"distance": {"value": 100, "unit": "cm"}}, "basis": D}]
        t = run_plan(start(rows))
        self.assertEqual(t["final"]["comparisons"]["same"]["result"], "MATCH")
        self.assertEqual(t["final"]["comparisons"]["different-unit"]["result"], "DIFFERENT")
        verify_receipt(t)

    def test_04_disconnection_retirement_and_identity_nonreuse(self):
        rows = [obj("a"), obj("b"),
                {"op": "connect", "id": "r", "from": "a", "to": "b", "label": "near",
                 "state": {}, "basis": D},
                {"op": "disconnect", "id": "r", "basis": D},
                {"op": "retire", "id": "a", "basis": D}]
        receipt = run_plan(start(rows))
        self.assertEqual(receipt["final"]["retired_objects"], ["a"])
        self.assertEqual(verify_receipt(receipt)["objects_live"], 1)
        with self.assertRaises(ValueError):
            run_plan(start(rows + [obj("a")]))

    def test_05_live_relation_prevents_dangling_endpoint(self):
        rows = [obj("a"), obj("b"),
                {"op": "connect", "id": "r", "from": "a", "to": "b", "label": "tied",
                 "state": {}, "basis": D}, {"op": "retire", "id": "a", "basis": D}]
        with self.assertRaisesRegex(ValueError, "live relations"):
            run_plan(start(rows))

    def test_06_forward_observation_and_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            run_plan(start([{"op": "observe", "id": "o", "subject": "unknown",
                             "entity": "object", "reading": {}, "basis": R}]))
        with self.assertRaises(ValueError):
            run_plan(start([obj("x"), {"op": "compare", "id": "c",
                                     "observation": "future", "expected": {}, "basis": D}]))
        with self.assertRaises(ValueError):
            run_plan(start([{"op": "introduce", "id": "x", "state": {},
                             "basis": {"kind": "external-report", "source": ""}}]))

    def test_07_limits_schema_nonfinite_rejected(self):
        cases = [start([obj("x"), obj("y")], objects=1),
                 start([obj("x")]) | {"limits": {"objects": 1, "relations": 1, "steps": 0}},
                 start([obj("x")]) | {"physics": "forced"},
                 start([obj("x", {"n": float("nan")})])]
        for case in cases:
            with self.assertRaises(ValueError):
                run_plan(case)
        self.assertTrue(verify_receipt(run_plan(start([obj("x")], objects=1)))["valid"])

    def test_08_tampered_record_or_claim_rejected(self):
        trace = run_plan(load_json(SAMPLE))
        for field, replacement in (("after_state_hash", "0" * 64),
                                   ("effect", {"status": "MATCH"}),
                                   ("previous_hash", "0" * 64)):
            altered = deepcopy(trace)
            altered["events"][4][field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify_receipt(altered)
        altered = deepcopy(trace)
        altered["final"]["objects"]["moving-part"]["angle"]["value"] = 29.8
        with self.assertRaises(ValueError):
            verify_receipt(altered)
        altered = deepcopy(trace)
        altered["evidence_depth"] = "physically-verified"
        with self.assertRaises(ValueError):
            verify_receipt(altered)

    def test_09_generator_does_not_mutate_input(self):
        plan = load_json(SAMPLE)
        original = deepcopy(plan)
        run_plan(plan)
        self.assertEqual(plan, original)

    def test_10_cli_round_trip(self):
        with TemporaryDirectory() as td:
            output = Path(td) / "receipt.json"
            p = subprocess.run([sys.executable, "-m", "work.ab_world.construction",
                                "--plan", str(SAMPLE)], check=True,
                               capture_output=True, text=True)
            output.write_text(p.stdout, encoding="utf-8")
            q = subprocess.run([sys.executable, "-m", "work.ab_world.construction",
                                "--verify", str(output)], check=True,
                               capture_output=True, text=True)
            self.assertTrue(json.loads(q.stdout)["valid"])

    def test_11_duplicate_json_keys_rejected(self):
        with TemporaryDirectory() as td:
            f = Path(td) / "bad.json"
            f.write_text('{"schema":"x","schema":"y"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_json(f)

    def test_12_same_identity_in_separate_worlds_legal(self):
        a = run_plan(start([obj("same", {"kind": "mechanical"})]))
        b = run_plan(start([obj("same", {"kind": "temporal"})]))
        self.assertNotEqual(a["final"], b["final"])
        self.assertTrue(verify_receipt(a)["valid"] and verify_receipt(b)["valid"])


if __name__ == "__main__":
    unittest.main()
