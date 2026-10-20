"""Falsify false coupling and provenance promotion in the native world probe."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from systems.workspace.nih_prototype_worker_source import prototype_worker
from work.ab_world import cross_referent_probe as probe


class OriginalSourceBoundaryTests(unittest.TestCase):
    def test_01_two_independent_axes_are_four_actual_source_observations(self):
        result = probe.run()
        self.assertEqual(result["schema"], "ab-cross-referent-native-observation/v1")
        self.assertEqual(len(result["cases"]), 4)
        self.assertIsNone(result["world48_optional_observation"])
        rows = result["cases"]
        self.assertEqual(rows[0]["w13"], rows[1]["w13"])
        self.assertEqual(rows[2]["w13"], rows[3]["w13"])
        self.assertEqual(rows[0]["nih"], rows[2]["nih"])
        self.assertEqual(rows[1]["nih"], rows[3]["nih"])
        self.assertNotEqual(rows[0]["w13"], rows[2]["w13"])
        self.assertNotEqual(rows[0]["nih"], rows[1]["nih"])
        self.assertEqual(rows[0]["nih"]["future_leakage_ids"], ["delayed-result"])
        self.assertEqual(rows[1]["nih"]["future_leakage_ids"], [])
        self.assertTrue(result["bounded_observation"])
        self.assertFalse(result["general_world_completed"])
        self.assertFalse(result["physical_measurements_witnessed"])
        self.assertFalse(result["nih_original_historical_versions_authenticated"])
        self.assertEqual(result["new_workstation_jobs"], 0)

    def test_02_world48_is_optional_and_cannot_rewrite_nih_or_w13(self):
        plain = probe.run()
        expanded = probe.run(with_world48=True)
        self.assertEqual(plain["cases"], expanded["cases"])
        self.assertEqual(plain["source_sha256"], expanded["source_sha256"])
        math = expanded["world48_optional_observation"]
        self.assertTrue(math["source_replay"]["valid"])
        self.assertFalse(math["nih_capacity_inferred"])
        self.assertEqual(math["receipt"]["law_ids"], [0, 1])
        from work.arc3.window48_world_export import verify_receipt
        forged = deepcopy(math["receipt"])
        forged["events"][0]["after"][0] = (forged["events"][0]["after"][0] + 1) % 27
        with self.assertRaises(ValueError):
            verify_receipt(forged)

    def test_03_original_emitted_python_mutation_is_not_admitted(self):
        source = prototype_worker.ENGINE
        old = 'if o["known_at"] <= known'
        self.assertIn(old, source)
        mutant = source.replace(old, 'if o["known_at"] > known')
        with patch.object(prototype_worker, "ENGINE", mutant):
            with self.assertRaises(ValueError):
                probe.run()

    def test_04_changed_source_availability_is_not_original_scope(self):
        with TemporaryDirectory() as td:
            altered = Path(td) / "fixture.json"
            data = json.loads(probe.FIXTURE.read_text())
            for record in data["observations"]:
                if record["id"] == "delayed-result":
                    record["known_at"] = "2026-01-04"
            altered.write_text(json.dumps(data), encoding="utf8")
            with patch.object(probe, "FIXTURE", altered):
                with self.assertRaises(ValueError):
                    probe.run()

    def test_05_missing_world48_never_blocks_nih_probe(self):
        with patch.object(probe, "optional_world48", side_effect=AssertionError("not admitted")):
            self.assertEqual(len(probe.run()["cases"]), 4)
            with self.assertRaises(AssertionError):
                probe.run(with_world48=True)


if __name__ == "__main__":
    unittest.main()
