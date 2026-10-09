"""Focused mathematical Engine 1 integration against existing native constructors."""
import unittest

from work.arc_like_maze.engine_one import (
    ConstructedEngine, InverseConstructionEngine, Requirements,
)
from work.arc_like_maze.third_coupling import CouplingTower
from work.arc_like_maze.window_combined import CombinedWorld


class MathematicalEngineOneTests(unittest.TestCase):
    def setUp(self):
        self.builder = InverseConstructionEngine()

    def test_inverse_equations_construct_a_law_not_a_named_product(self):
        result = self.builder.construct(Requirements(
            "window48", fixed_words=(("B", 9), ("BBB", 18), ("ABABAB", 18)),
        ))
        self.assertEqual(result.status, "CONSTRUCTED")
        self.assertIsInstance(result.engine.law, CombinedWorld)
        w = result.engine.law
        self.assertEqual((w.support, w.pulse), (0, 1))
        self.assertEqual(result.admissible_candidates, 6)  # 2 balanced x 3 shears
        self.assertIn("not a unique inverse", result.selection_rule)

    def test_every_window_system_is_selectable_by_equations_or_proven_relation(self):
        seed = ConstructedEngine(CombinedWorld(0, 0, 0, 0), 0)
        result = seed.evolve(self.builder, Requirements("window48", relation="ROOTED_FULL"))
        self.assertEqual(result.status, "CONSTRUCTED")
        self.assertNotEqual(result.engine.law, seed.law)
        self.assertEqual(result.engine.history[-1].kind, "ROOTED_FULL")
        self.assertEqual(result.engine.version, 1)

    def test_nonroot_alignment_retains_original_mark_and_collision(self):
        seed = ConstructedEngine(CombinedWorld(0, 0, 1, 0), 0)
        result = seed.evolve(self.builder, Requirements(
            "window48", relation="FULL_UNROOTED",
        ))
        self.assertEqual(result.status, "CONSTRUCTED")
        item = result.engine.history[-1]
        self.assertEqual(item.kind, "FULL_UNROOTED")
        self.assertEqual(item.source_mark, (0, 0, 0))
        self.assertNotEqual(item.target_mark, item.source_mark)
        self.assertTrue(any("word collision:" in s for s in item.evidence))

    def test_middle_support_combined_edit_cannot_be_falsely_aligned(self):
        for k in (1, 2):
            seed = ConstructedEngine(CombinedWorld(k, 0, 1, 0), 0)
            result = seed.evolve(self.builder, Requirements(
                "window48", relation="FULL_OBSTRUCTED",
                fixed_words=(("B", (3 - k) * 3), ("BBB", 18)),
            ))
            self.assertEqual(result.status, "CONSTRUCTED")
            self.assertEqual(result.engine.history[-1].kind, "FULL_OBSTRUCTED")
            self.assertTrue(any("fixed word" in s for s in result.engine.history[-1].evidence))

    def test_window_operator_walls_are_not_wrapped(self):
        seed = ConstructedEngine(CombinedWorld(3, 0, 1, 1), 4)
        result = seed.evolve(self.builder, Requirements(
            "window48", relation="FULL_OBSTRUCTED",
        ))
        self.assertEqual(result.status, "WALL")
        self.assertIsNone(result.engine)

    def test_changing_engine_laws_preserves_generator_inverse(self):
        seed = ConstructedEngine(CombinedWorld(0, 0, 1, 0), 0)
        changed = seed.evolve(self.builder, Requirements(
            "window48", relation="FULL_UNROOTED",
        )).engine
        self.assertEqual(changed.inverse(changed.step((0, 1, 2), "B"), "B"), (0, 1, 2))

    def test_incompatible_or_unproved_constraints_return_wall(self):
        result = self.builder.construct(Requirements("window48", fixed_words=(("B", 500),)))
        self.assertEqual(result.status, "WALL")
        self.assertIsNone(result.engine)
        with self.assertRaises(ValueError):
            Requirements("window48", fixed_words=(("AB", 3),))
        with self.assertRaises(ValueError):
            Requirements("coupling_tower", fixed_words=(("BBB", 3),))
        with self.assertRaises(ValueError):
            Requirements("window48", fixed_words=(("B", 3), ("B", 6)))

    def test_tower_equivalent_change_has_explicit_all_depth_scale(self):
        seed = ConstructedEngine(CouplingTower(((0, 1, 2),), 3), 0)
        change = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=1, fixed_B=3, relation="ROOTED_FULL",
        ))
        self.assertEqual(change.status, "CONSTRUCTED")
        self.assertEqual(change.engine.law.rules, ((0, 2, 1),))
        self.assertEqual(change.engine.history[-1].kind, "ROOTED_FULL")
        self.assertTrue(any("all-depth" in w for w in change.engine.history[-1].evidence))

    def test_dormant_origin_orbit_is_not_misreported_full_state(self):
        seed = ConstructedEngine(CouplingTower(((0, 0, 0), (0, 0, 0)), 4), 0)
        change = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=2, relation="ROOTED_REACHABLE",
        ))
        self.assertEqual(change.status, "CONSTRUCTED")
        self.assertEqual(change.engine.history[-1].kind, "ROOTED_REACHABLE")
        self.assertIn("full-state alignment remains UNKNOWN", change.engine.history[-1].evidence)

    def test_tower_different_fixed_B_proves_full_state_obstruction(self):
        seed = ConstructedEngine(CouplingTower(((0, 0, 0),), 3), 0)
        change = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=1, fixed_B=3, relation="FULL_OBSTRUCTED",
        ))
        self.assertEqual(change.status, "CONSTRUCTED")
        self.assertIn("fixed B on complete state space", change.engine.history[-1].evidence)

    def test_tower_rule_extension_preserves_projection_not_equivalence(self):
        seed = ConstructedEngine(CouplingTower(((0, 1, 2),), 3), 0)
        change = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=2, fixed_B=9, relation="PROJECTION",
        ))
        self.assertEqual(change.status, "CONSTRUCTED")
        self.assertEqual(change.engine.history[-1].kind, "PROJECTION")
        self.assertEqual(change.engine.version, 1)
        self.assertTrue(any("not a full-state conjugacy" in s
                            for s in change.engine.history[-1].evidence))

    def test_no_fake_bridge_between_unrelated_grammars(self):
        seed = ConstructedEngine(CombinedWorld(0, 0, 0, 0), 0)
        change = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=1,
        ))
        self.assertEqual(change.status, "WALL")
        self.assertIn("no admitted construction", change.wall)

    def test_no_unwitnessed_multi_table_jump(self):
        seed = ConstructedEngine(CouplingTower(((0, 0, 0), (0, 0, 0)), 4), 0)
        # One step may alter only one table. No two-table rewrite is admitted.
        result = seed.evolve(self.builder, Requirements(
            "coupling_tower", couplings=2, fixed_B=3,
        ))
        self.assertEqual(result.status, "WALL")

    def test_new_versions_retain_earlier_witnesses(self):
        first = ConstructedEngine(CombinedWorld(0, 0, 0, 0), 0)
        second = first.evolve(self.builder, Requirements(
            "window48", relation="ROOTED_FULL",
        )).engine
        third = second.evolve(self.builder, Requirements(
            "window48", relation="FULL_OBSTRUCTED",
        )).engine
        self.assertEqual((second.version, third.version), (1, 2))
        self.assertGreater(len(third.history), len(second.history))
        self.assertEqual(third.history[:len(second.history)], second.history)


if __name__ == "__main__":
    unittest.main()
