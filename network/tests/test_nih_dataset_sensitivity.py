"""Independent and adversarial tests of NIH P2 synthetic source variations."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.nih_dataset_sensitivity import (
    EXPERIMENT, grid, run_experiment, variants,
)
from systems.workspace.nih_prototype_worker_source.prototype_worker import ENGINE
from systems.workspace.nih_scope_native import validate_scope


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "network/tests/fixtures/nih_scope_example.json"
WORKER = ROOT / "systems/workspace/nih_benchmark_worker_source/benchmark_worker.py"


class DatasetSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = validate_scope(json.loads(FIXTURE.read_text(encoding="utf8")))
        cls.predicates = ["has-status"]
        cls.dataset = {
            "kind": "synthetic-temporal-dataset/v1",
            "synthetic": True,
            "case_id": cls.scope["case_id"],
            "prototype_id": "synthetic-variation-fixture",
            "ontology_sha256": "a" * 64,
            "observations": cls.scope["observations"],
            "functional_predicates": cls.predicates,
        }

    def args(self, output, **changes):
        args = {
            "scope": self.scope,
            "predicates": self.predicates,
            "code": ENGINE,
            "dataset_text": json.dumps(self.dataset, sort_keys=True),
            "worker_source": WORKER,
            "query_history_sha256": "b" * 64,
            "edition_fingerprint": "synthetic-fixture-edition",
            "output_dir": output,
        }
        args.update(changes)
        return args

    def test_00_each_source_mutation_is_independent_and_valid(self):
        family = variants(self.scope, self.predicates)
        self.assertEqual(len(family), 9)
        for name, changed in family.items():
            with self.subTest(variant=name):
                self.assertEqual(validate_scope(changed), changed)
        self.assertEqual(len({json.dumps(v["observations"], sort_keys=True)
                              for v in family.values()}), 9)
        self.assertGreaterEqual(len(grid(family)), 20)

    def test_01_source_worker_and_original_executable_both_match_host_oracle(self):
        with TemporaryDirectory() as td:
            result = run_experiment(**self.args(Path(td)))
            self.assertEqual(result["schema"], EXPERIMENT)
            self.assertEqual(result["variation_count"], 9)
            self.assertGreaterEqual(result["queries_per_variation"], 20)
            self.assertEqual(
                result["total_independent_original_program_executions"],
                9 * result["queries_per_variation"])
            self.assertTrue(all(v["source_worker_matches_original_program_and_oracle"]
                                for v in result["variations"]))
            self.assertTrue((Path(td) / "nih-p2-source-variation-cases.jsonl").is_file())
            self.assertFalse(result["source_owned_native_checkpoint"])
            self.assertFalse(result["official_NIH_submission"])
            self.assertFalse(result["general_biomedical_benchmark"])

    def test_02_reject_different_parent_dataset_or_broken_original_program(self):
        with TemporaryDirectory() as td:
            changed = deepcopy(self.dataset)
            changed["observations"][0]["source_ref"] = "unapproved-input"
            with self.assertRaises(ValueError):
                run_experiment(**self.args(
                    Path(td), dataset_text=json.dumps(changed)))
            with self.assertRaises(ValueError):
                run_experiment(**self.args(
                    Path(td), code="raise ValueError('altered original program')"))

    def test_03_reject_altered_source_worker(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "benchmark_worker.py"
            path.write_text("raise RuntimeError('tampered source')\n", encoding="utf8")
            with self.assertRaises(ValueError):
                run_experiment(**self.args(Path(td), worker_source=path))


if __name__ == "__main__":
    unittest.main()
