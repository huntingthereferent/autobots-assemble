"""Independent source generation and metamorphic test boundaries."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from systems.workspace.nih_independent_metamo import (
    SCHEMA, SEEDS_AND_SIZES, independent_scope, queries, run_experiment,
)
from systems.workspace.nih_prototype_worker_source.prototype_worker import ENGINE
from systems.workspace.nih_scope_native import validate_scope

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / "network/tests/fixtures/nih_scope_example.json"
WORKER = ROOT / "systems/workspace/nih_benchmark_worker_source/benchmark_worker.py"


class IndependentMetamorphicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = validate_scope(json.loads(SCOPE.read_text(encoding="utf8")))
        cls.dataset = {
            "kind": "synthetic-temporal-dataset/v1",
            "synthetic": True,
            "case_id": cls.parent["case_id"],
            "prototype_id": "synthetic-parent-prototype",
            "ontology_sha256": "a" * 64,
            "observations": cls.parent["observations"],
            "functional_predicates": ["has-status", "has-result"],
        }

    def inputs(self, destination):
        return {
            "code": ENGINE,
            "parent_dataset": json.dumps(self.dataset, sort_keys=True),
            "worker_source": WORKER,
            "original_observations": self.parent["observations"],
            "query_history_sha256": "b" * 64,
            "parent_fingerprint": "synthetic-fixture-pinned-original",
            "output_dir": destination,
        }

    def test_00_fresh_sources_do_not_reuse_original_observations(self):
        parent_ids = {x["id"] for x in self.parent["observations"]}
        self.assertEqual(len(queries()), 25)
        for seed, size in SEEDS_AND_SIZES:
            with self.subTest(seed=seed):
                source = independent_scope(seed, size)
                self.assertEqual(len(source["observations"]), size)
                self.assertEqual(validate_scope(source), source)
                self.assertFalse({x["id"] for x in source["observations"]} & parent_ids)
        with self.assertRaises(ValueError):
            independent_scope(12, 17)

    def test_01_original_python_and_worker_pass_independent_metamo(self):
        with TemporaryDirectory() as td:
            result = run_experiment(**self.inputs(Path(td)))
            self.assertEqual(result["schema"], SCHEMA)
            self.assertEqual(result["independent_source_fixture_count"], 5)
            self.assertEqual(result["independent_query_replays"], 125)
            self.assertEqual(result["original_native_jobs"], 12)
            self.assertFalse(result["additional_native_checkpoint"])
            self.assertFalse(result["official_NIH_submission"])
            self.assertTrue(all(x["source_worker_original_program_and_oracle_agreed"]
                                for x in result["source_cases"]))
            self.assertTrue(all("functional-conflict" in x["metamorphic_properties_checked"]
                                for x in result["source_cases"]))
            self.assertTrue((Path(td) / "nih-p2-independent-metamo-cases.jsonl").is_file())
            self.assertEqual(len(list(Path(td).glob("seed-*-source.json"))), 5)

    def test_02_reject_changed_original_parent_and_executable(self):
        with TemporaryDirectory() as td:
            inp = self.inputs(Path(td))
            changed = [dict(r) for r in self.parent["observations"]]
            changed[0]["source_ref"] = "changed-parent"
            with self.assertRaises(ValueError):
                run_experiment(**{**inp, "original_observations": changed})
            with self.assertRaises(ValueError):
                run_experiment(**{**inp, "code": "raise ValueError('mutated original')"})

    def test_03_reject_tampered_source_worker(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "benchmark_worker.py"
            path.write_text("raise RuntimeError('tampered')\n", encoding="utf8")
            with self.assertRaises(ValueError):
                run_experiment(**{**self.inputs(Path(td)), "worker_source": path})


if __name__ == "__main__":
    unittest.main()
