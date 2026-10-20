"""Original W13 movement preservation across neutral A/B construction."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from systems.workspace import game_construction as native
from work.ab_world import w13_source_handoff as bridge
from work.ab_world.verify_construction import verify_receipt


class WorldSourceHandoffTests(unittest.TestCase):
    def test_01_original_w13_source_movement_carried_without_new_rule(self):
        output = bridge.handoff()
        self.assertEqual(output["schema"], bridge.SCHEMA)
        self.assertTrue(output["native_source_replay"]["valid"])
        self.assertTrue(output["source_consistent_with_independent_contract"])
        self.assertEqual(output["differences"], [])
        self.assertFalse(output["physically_measured"])
        world = output["world_receipt"]
        self.assertEqual(verify_receipt(world)["steps_verified"], 10)
        self.assertEqual(world["final"]["objects"]["w13-native-state"]["native"]["turns"], 3)
        self.assertTrue(world["final"]["objects"]["w13-native-state"]["native"]["collected"])
        self.assertEqual(len(world["final"]["comparisons"]), 3)
        self.assertEqual(len(world["final"]["observations"]), 3)
        self.assertIn(output["source_code_sha256"],
                      world["final"]["observations"]["w13-native-event-1"]["basis"]["source"])

    def test_02_alternate_native_path_returns_uncollected_without_fabrication(self):
        output = bridge.handoff(["left", "left", "up"])
        self.assertTrue(output["source_consistent_with_independent_contract"])
        state = output["world_receipt"]["final"]["objects"]["w13-native-state"]["native"]
        self.assertEqual(state["x"], 0)
        self.assertEqual(state["y"], 0)
        self.assertFalse(state["collected"])

    def test_03_invalid_source_action_is_not_world_movement(self):
        with self.assertRaises(ValueError):
            bridge.handoff(["fly"])

    def test_04_forged_source_trace_rejected_before_world(self):
        original = native.run_actions
        def forged(actions, spec):
            result = original(actions, spec)
            result["steps"][0]["after"]["x"] = 22
            return result
        with patch.object(bridge.source, "run_actions", side_effect=forged):
            with self.assertRaises(ValueError):
                bridge.handoff()

    def test_05_different_independent_expectation_stays_explicitly_different(self):
        original = bridge.independent_expected
        def perturbed(spec, actions):
            result = original(spec, actions)
            result[0]["verdict"] = "unwitnessed-alternate-rule"
            return result
        with patch.object(bridge, "independent_expected", side_effect=perturbed):
            output = bridge.handoff()
        self.assertFalse(output["source_consistent_with_independent_contract"])
        self.assertEqual(output["differences"], ["w13-independent-contrast-1"])
        self.assertEqual(output["world_receipt"]["final"]["comparisons"]["w13-independent-contrast-1"]["result"], "DIFFERENT")
        self.assertTrue(output["world_ledger_witness"]["valid"])
        self.assertFalse(output["physically_measured"])

    def test_06_limits_prevent_unbounded_handoff(self):
        with self.assertRaises(ValueError):
            bridge.handoff(["right"] * 3001)


if __name__ == "__main__":
    unittest.main()
