"""Independent tests for larger synthetic source layouts and original replay."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from systems.workspace.nih_scope_native import validate_scope
from systems.workspace.nih_source_families import SCHEMA, LABEL, FAMILY_SIZES, families
from systems.workspace.nih_dataset_sensitivity import grid, run_experiment
from systems.workspace.nih_prototype_worker_source.prototype_worker import ENGINE

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "network/tests/fixtures/nih_scope_example.json"
WORKER = ROOT / "systems/workspace/nih_benchmark_worker_source/benchmark_worker.py"


class SourceFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = validate_scope(json.loads(FIXTURE.read_text(encoding="utf8")))
        cls.preds = ["has-status"]
        cls.dataset = {
            "kind": "synthetic-temporal-dataset/v1",
            "synthetic": True,
            "case_id": cls.scope["case_id"],
            "prototype_id": "synthetic-source-family-fixture",
            "ontology_sha256": "a" * 64,
            "observations": cls.scope["observations"],
            "functional_predicates": cls.preds,
        }

    def params(self, out):
        return {
            "scope": self.scope,
            "predicates": self.preds,
            "code": ENGINE,
            "dataset_text": json.dumps(self.dataset, sort_keys=True),
            "worker_source": WORKER,
            "query_history_sha256": "b" * 64,
            "edition_fingerprint": "synthetic-source-family-test",
            "sources": families(self.scope),
            "label": LABEL,
            "experiment_schema": SCHEMA,
            "output_dir": out,
        }

    def test_00_distinct_valid_source_layouts(self):
        groups = families(self.scope)
        self.assertEqual(len(groups), len(FAMILY_SIZES) + 1)
        self.assertEqual(len(groups["original"]["observations"]), 2)
        self.assertEqual([len(groups[name]["observations"]) for name, _ in FAMILY_SIZES],
                         [n for _, n in FAMILY_SIZES])
        self.assertTrue(all(validate_scope(scope) == scope for scope in groups.values()))
        self.assertGreaterEqual(len(grid(groups)), 20)
        # The larger layouts must introduce new subjects, evidence sources
        # and multiple known-at cutovers, rather than clone one pair.
        biggest = groups["sixteen-sources"]["observations"]
        self.assertGreater(len({x["subject"] for x in biggest}), 3)
        self.assertGreater(len({x["source_ref"] for x in biggest}), 4)
        self.assertGreater(len({x["known_at"] for x in biggest}), 4)

    def test_01_source_worker_original_python_and_oracle_agree(self):
        with TemporaryDirectory() as td:
            result = run_experiment(**self.params(Path(td)))
            self.assertEqual(result["schema"], SCHEMA)
            self.assertEqual(result["variation_count"], 6)
            self.assertGreaterEqual(result["queries_per_variation"], 20)
            self.assertEqual(result["total_independent_original_program_executions"],
                             result["variation_count"] * result["queries_per_variation"])
            self.assertTrue(all(x["source_worker_matches_original_program_and_oracle"]
                                for x in result["variations"]))
            self.assertTrue((Path(td) / (LABEL + "-cases.jsonl")).exists())
            self.assertFalse(result["official_NIH_submission"])
            self.assertFalse(result["source_owned_native_checkpoint"])
            self.assertFalse(result["general_biomedical_benchmark"])

    def test_02_changed_baseline_parent_rejected(self):
        with TemporaryDirectory() as td:
            params = self.params(Path(td))
            changed = dict(params["sources"])
            changed["original"] = changed["four-mixed"]
            params["sources"] = changed
            with self.assertRaises(ValueError):
                run_experiment(**params)


if __name__ == "__main__":
    unittest.main()
