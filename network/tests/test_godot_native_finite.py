"""Native-source tests for the Godot A/B finite visual projection.

The Python model is authoritative for this SPECIFIED finite example.
Godot is only allowed to display a matching snapshot; its canvas geometry
and smooth marker interpolation are not mathematical intermediate states.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from work.arc_like_maze.math import World
from views.godot_ab.export_finite import OUT, DEMO, MODEL, manifest, serialized


class GodotFiniteViewTests(unittest.TestCase):
    def test_committed_manifest_exactly_matches_native_source(self):
        self.assertTrue(OUT.is_file())
        source = manifest()
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, source)
        self.assertEqual(OUT.read_text(encoding="utf-8"), serialized())
        self.assertEqual(source["schema"], "ab-native-finite-godot/v1")
        self.assertEqual(source["state_count"], 27)
        self.assertEqual(len(source["nodes"]), 27)
        self.assertEqual(set(tuple(s["state"]) for s in source["nodes"]),
                         MODEL.reachable())

    def test_every_displayed_a_b_edge_is_original_world_step(self):
        data = manifest()
        table = {tuple(n["state"]): n for n in data["nodes"]}
        self.assertEqual(len(table), 27)
        self.assertEqual(sum(bool(n["A"]) + bool(n["B"]) for n in data["nodes"]),
                         54)
        for state, row in table.items():
            for action in "AB":
                with self.subTest(state=state, action=action):
                    self.assertEqual(tuple(row[action]), MODEL.step(state, action))
                    self.assertIn(tuple(row[action]), table)

    def test_every_displayed_layer_is_native_breadth_first_distance(self):
        source = manifest()
        table = {tuple(x["state"]): x for x in source["nodes"]}
        depths = {MODEL.origin: 0}
        queue = [MODEL.origin]
        for state in queue:
            for action in "AB":
                dest = MODEL.step(state, action)
                if dest not in depths:
                    depths[dest] = depths[state] + 1
                    queue.append(dest)
        self.assertEqual(set(depths), MODEL.reachable())
        self.assertEqual([tuple(n["state"]) for n in source["nodes"]], queue)
        for state, depth in depths.items():
            self.assertEqual(table[state]["depth"], depth)

    def test_recorded_demo_is_replayable_without_pixel_inference(self):
        data = manifest()
        self.assertEqual(data["demo_actions"], DEMO)
        current = MODEL.origin
        self.assertEqual(data["demo_states"][0], list(current))
        for action, target in zip(DEMO, data["demo_states"][1:]):
            current = MODEL.step(current, action)
            self.assertEqual(target, list(current))
        self.assertEqual(MODEL.apply(DEMO), current)

    def test_dataset_can_be_verified_without_touching_it(self):
        before = OUT.read_bytes()
        completed = subprocess.run(
            [sys.executable, "-m", "views.godot_ab.export_finite", "--check"],
            cwd=Path(__file__).resolve().parents[2],
            check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("matches native finite World", completed.stdout)
        self.assertEqual(before, OUT.read_bytes())

    def test_presentation_is_explicitly_not_physics_or_universal_definition(self):
        record = manifest()
        self.assertIn("not universal A/B", record["referent"])
        self.assertIn("editorial", record["positions"])
        self.assertIn("no intermediate finite state", record["tween"])
        self.assertIn("not Godot physics", record["native_execution"])
        self.assertNotIn("units", record)
        # Match the original native world configuration, not a made-up
        # 48-anchor model or a claim that finite states *are* A/B itself.
        self.assertEqual((record["depth"], tuple(record["phi"])),
                         (MODEL.depth, MODEL.phi))


if __name__ == "__main__":
    unittest.main()
