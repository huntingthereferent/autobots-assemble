"""Tests of counterexample sensitivity, not tests that altered source is useful."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_prototype_worker_source.prototype_worker import ENGINE
from systems.workspace.nih_semantic_mutants import (
    SCHEMA, MUTANTS, challenge_scope, mutate, run,
)
from systems.workspace.nih_scope_native import validate_scope

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/"network/tests/fixtures/nih_scope_example.json"


class SemanticMutantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope=validate_scope(json.loads(FIXTURE.read_text(encoding="utf8")))
        cls.dataset={
            "kind":"synthetic-temporal-dataset/v1",
            "synthetic":True,
            "case_id":cls.scope["case_id"],
            "prototype_id":"synthetic-mutant-fixture",
            "ontology_sha256":"a"*64,
            "observations":cls.scope["observations"],
            "functional_predicates":["has-status","has-result"],
        }

    def args(self,out):
        return {
            "code":ENGINE,
            "original_dataset":json.dumps(self.dataset,sort_keys=True),
            "original_observations":self.scope["observations"],
            "source_owner_sha256":"native-original-synthetic-owner",
            "browser_history_sha256":"b"*64,
            "output_dir":out,
        }

    def test_00_mutants_are_explicit_and_original_source_remains_unchanged(self):
        self.assertEqual(len(MUTANTS),8)
        self.assertEqual(len({x[0] for x in MUTANTS}),8)
        self.assertEqual(validate_scope(challenge_scope()),challenge_scope())
        for name,before,after,*rest in MUTANTS:
            with self.subTest(mutant=name):
                mutant=mutate(ENGINE,before,after)
                self.assertNotEqual(ENGINE,mutant)
                self.assertEqual(mutant.count(after),1)
        with self.assertRaises(ValueError):
            mutate(ENGINE,"not a real original-code fragment","unexpected")

    def test_01_all_runnable_semantic_wrong_answers_are_caught(self):
        with TemporaryDirectory() as td:
            result=run(**self.args(Path(td)))
            self.assertEqual(result["schema"],SCHEMA)
            self.assertEqual(result["semantic_mutants_attempted"],8)
            self.assertEqual(result["semantic_mutants_detected"],8)
            self.assertEqual(result["original_program_execution_checks"],8)
            self.assertEqual(result["original_native_jobs"],12)
            self.assertTrue(all(r["mutated_program_executed_successfully"] for r in result["results"]))
            self.assertFalse(result["additional_native_checkpoint"])
            self.assertFalse(result["official_NIH_submission"])
            self.assertTrue((Path(td)/"nih-p2-semantic-mutant-cases.json").is_file())

    def test_02_wrong_parent_dataset_and_modified_original_rejected(self):
        with TemporaryDirectory() as td:
            inp=self.args(Path(td))
            original=json.loads(inp["original_dataset"])
            original["observations"][0]["source_ref"]="tampered-parent"
            with self.assertRaises(ValueError):
                run(**{**inp,"original_dataset":json.dumps(original)})
            with self.assertRaises(ValueError):
                run(**{**inp,"code":"raise ValueError('changed')"})

    def test_03_require_original_browser_source_and_source_edition(self):
        with TemporaryDirectory() as td:
            inp=self.args(Path(td))
            with self.assertRaises(ValueError):
                run(**{**inp,"browser_history_sha256":"x"})
            with self.assertRaises(ValueError):
                run(**{**inp,"source_owner_sha256":""})


if __name__=="__main__":
    unittest.main()
