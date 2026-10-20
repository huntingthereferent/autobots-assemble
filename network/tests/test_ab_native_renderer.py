"""A/B's OWN finite renderer: verify facts before rendering on canvas.

Unlike the abandoned Godot viewer this uses only original Python projection,
native Canvas2D JavaScript, and the existing source-owned finite verifier.
"""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from work.arc_like_maze.math import World
from systems.workspace.ab_relational_cluster import _independent_step
from views.renderer_native.scene import OUT, SOURCE, scene, encoded, main

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "docs/live/ab-renderer.html"
JS = ROOT / "docs/live/ab-renderer.js"


class NativeRendererTests(unittest.TestCase):
    def test_complete_scene_matches_real_finite_world(self):
        data = scene()
        recorded = json.loads(OUT.read_text(encoding="utf8"))
        self.assertEqual(data, recorded)
        self.assertEqual(recorded["schema"], "ab-renderer/native-finite-scene/v1")
        self.assertEqual(recorded["node_count"], 27)
        self.assertEqual(recorded["edge_count"], 54)
        self.assertEqual(recorded["source_sha256"], sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(recorded["source"], "work/arc_like_maze/math.py::World")

    def test_every_state_and_both_edges_verified_independently(self):
        world = World(3, (0, 1, 2))
        rows = scene()["nodes"]
        self.assertEqual({tuple(row["state"]) for row in rows}, world.reachable())
        for row in rows:
            state = tuple(row["state"])
            self.assertEqual(row["id"], ",".join(map(str, state)))
            for action in "AB":
                with self.subTest(state=state, action=action):
                    nxt = world.step(state, action)
                    self.assertEqual(nxt, _independent_step(state, action))
                    self.assertEqual(row["transitions"][action], ",".join(map(str, nxt)))

    def test_steps_from_origin_reconstructed_in_graph_order(self):
        world = World(3, (0, 1, 2))
        recorded = scene()
        seen = {world.origin: 0}
        pending = [world.origin]
        for state in pending:
            for action in "AB":
                target = world.step(state, action)
                if target not in seen:
                    seen[target] = seen[state] + 1
                    pending.append(target)
        self.assertEqual([row["state"] for row in recorded["nodes"]],
                         [list(s) for s in pending])
        self.assertTrue(all(row["steps_from_origin"] == seen[tuple(row["state"])]
                            for row in recorded["nodes"]))

    def test_source_owned_example_action_history_replays(self):
        value = scene()
        world = World(3, (0, 1, 2))
        current = world.origin
        self.assertEqual(value["example_states"][0], ",".join(map(str, current)))
        for action, target in zip(value["example_actions"], value["example_states"][1:]):
            current = world.step(current, action)
            self.assertEqual(target, ",".join(map(str, current)))
        self.assertNotIn("real_world", value)
        self.assertIn("editorial", value["presentation_boundary"])

    def test_read_only_check_has_no_side_effect_on_scene(self):
        before = OUT.read_bytes()
        self.assertEqual(main(["--check"]), 0)
        self.assertEqual(OUT.read_bytes(), before)
        with TemporaryDirectory() as d:
            # Test code does not create a new output path or a second source.
            self.assertTrue(Path(d).is_dir())

    def test_no_godot_or_secondary_executor_in_viewer(self):
        text = JS.read_text(encoding="utf8")
        html = HTML.read_text(encoding="utf8")
        self.assertIn('getContext("2d"', text)
        self.assertIn('requestAnimationFrame', text)
        self.assertIn('read-only', text.lower())
        self.assertNotIn('PhysicsServer', text)
        self.assertNotIn('.tscn', text)
        self.assertNotIn('GDScript', text)
        self.assertNotIn('https://cdn.', html.lower())
        self.assertIn('ab-renderer.js', html)
        self.assertIn('ab-renderer-scene.json', text)


if __name__ == "__main__":
    unittest.main()
