"""Cross-family integration tests for the shared observe/move harness."""
import unittest

from work.arc_like_maze.engine_one import ConstructedEngine, Requirements
from work.arc_like_maze.observe_move_harness import ObserveMoveHarness
from work.arc_like_maze.third_coupling import CouplingTower
from work.arc_like_maze.window_combined import CombinedWorld


class ObserveMoveHarnessTests(unittest.TestCase):
    def setUp(self):
        self.harness = ObserveMoveHarness()

    def test_observation_adapters_keep_native_invariants_distinct(self):
        window = self.harness.observe(ConstructedEngine(CombinedWorld(0, 0, 1, 0), 4))
        tower = self.harness.observe(ConstructedEngine(CouplingTower(((0, 1, 2),), 3), 7))
        self.assertEqual(window.family, "window48")
        self.assertEqual(dict(window.fixed_word_counts)["B"], 27)
        self.assertIsNone(window.fixed_B_count)
        self.assertEqual(tower.family, "coupling_tower")
        self.assertIsNotNone(tower.fixed_B_count)
        self.assertIsNotNone(tower.rooted_state_count)
        self.assertEqual((window.version, tower.version), (4, 7))

    def test_cross_family_comparison_is_unknown_not_false_equivalence(self):
        window = ConstructedEngine(CombinedWorld(0, 0, 1, 0), 0)
        tower = ConstructedEngine(CouplingTower(((0, 1, 2),), 3), 0)
        result = self.harness.compare(window, tower)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertIsNone(result.witness)
        self.assertTrue(any("cross-family bridge not admitted" in x for x in result.evidence))

    def test_rooted_and_unrooted_are_not_flattened(self):
        source = ConstructedEngine(CombinedWorld(0, 0, 1, 0), 0)
        unrooted = ConstructedEngine(CombinedWorld(0, 0, 1, 1), 1)
        result = self.harness.compare(source, unrooted)
        self.assertEqual(result.status, "EQUIVALENT_UNROOTED")
        self.assertEqual(result.witness_kind, "FULL_UNROOTED")
        self.assertNotEqual(result.witness.source_mark, result.witness.target_mark)
        self.assertTrue(any("word collision:" in x for x in result.evidence))

    def test_fixed_word_obstruction_survives_shared_interface(self):
        source = ConstructedEngine(CombinedWorld(1, 0, 1, 0), 0)
        target = ConstructedEngine(CombinedWorld(1, 0, 1, 1), 1)
        result = self.harness.compare(source, target)
        self.assertEqual(result.status, "OBSTRUCTED_FULL_STATE")
        self.assertEqual(result.witness_kind, "FULL_OBSTRUCTED")
        self.assertTrue(any("fixed word ABABAB" in x for x in result.evidence))

    def test_unwitnessed_same_family_pair_stays_unknown(self):
        source = ConstructedEngine(CouplingTower(((0, 1, 2),), 3), 0)
        target = ConstructedEngine(CouplingTower(((0, 2, 1), (0, 0, 0)), 4), 1)
        result = self.harness.compare(source, target)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertIsNone(result.witness)

    def test_movement_uses_native_constructor_and_preserves_witness_kind(self):
        source = ConstructedEngine(CombinedWorld(0, 0, 0, 0), 0)
        result = self.harness.move(source, Requirements("window48", relation="ROOTED_FULL"))
        self.assertEqual(result.status, "MOVED")
        self.assertEqual(result.next_version, 1)
        self.assertTrue(result.witness_kinds)
        self.assertTrue(all(k == "ROOTED_FULL" for k in result.witness_kinds))

    def test_native_wall_is_not_relabelled_as_success(self):
        source = ConstructedEngine(CombinedWorld(3, 0, 1, 1), 4)
        result = self.harness.move(source, Requirements("window48", relation="FULL_OBSTRUCTED"))
        self.assertEqual(result.status, "WALL")
        self.assertIsNone(result.next_version)
        self.assertIsNotNone(result.wall)


if __name__ == "__main__":
    unittest.main()
