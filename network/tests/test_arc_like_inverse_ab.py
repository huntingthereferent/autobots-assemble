"""Generated-world witnesses only; no native ARC claims or runtime mutation."""
import unittest

from work.arc_like_maze.math import World, align_worlds, inverse_candidates, rescale_last, verify_recurrence


class InverseABConstructionTests(unittest.TestCase):
    def test_inverse_generates_nine_candidate_relations(self):
        worlds = inverse_candidates()
        self.assertEqual(len(worlds), 9)
        self.assertEqual(sum(len(world.reachable()) == 27 for world in worlds), 8)

    def test_different_states_can_preserve_exact_action_relations(self):
        left = World(3, (0, 1, 2))
        right = World(3, (0, 2, 1))
        self.assertTrue(align_worlds(left, right, rescale_last).aligned)
        self.assertNotEqual(left.apply("BB"), right.apply("BB"))
        self.assertEqual(rescale_last(left.apply("BB")), right.apply("BB"))

    def test_identity_is_not_enough_for_renamed_world(self):
        self.assertFalse(align_worlds(World(3), World(3, (0, 2, 1)), lambda state: state).aligned)

    def test_projection_is_not_entire_world_alignment(self):
        lower, higher = World(3), World(4)
        self.assertEqual(higher.apply("BBB")[:-1], lower.apply("BBB"))
        self.assertNotEqual(higher.apply("BBB"), higher.origin)
        self.assertFalse(align_worlds(higher, lower, lambda state: state[:-1]).aligned)

    def test_distinct_cycle_relation_rejects_proposed_alignment(self):
        result = align_worlds(World(3), World(3, (0, 1, 1)), lambda state: state)
        self.assertFalse(result.aligned)
        self.assertEqual(World(3).apply("BBB"), World(3).origin)
        self.assertNotEqual(World(3, (0, 1, 1)).apply("BBB"), World(3).origin)

    def test_single_aligned_turn_does_not_claim_closed_construction(self):
        left, right = World(3), World(3, (0, 2, 1))
        self.assertTrue(verify_recurrence((left, right), (rescale_last,)).startswith("CANDIDATE:"))

    def test_next_turn_alignment_is_checked_but_not_infinite_proof(self):
        left, right = World(3), World(3, (0, 2, 1))
        status = verify_recurrence((left, right, left), (rescale_last, rescale_last))
        self.assertTrue(status.startswith("CANDIDATE_NEXT_LAYER_VERIFIED:"))

    def test_new_relation_breaks_candidate_on_later_turn(self):
        left, right, changed = World(3), World(3, (0, 2, 1)), World(4)
        self.assertEqual(verify_recurrence((left, right, changed),
                                           (rescale_last, lambda state: state + (0,))),
                         "OPEN: alignment breaks")

    def test_invalid_evidence_shape_remains_unknown(self):
        self.assertTrue(verify_recurrence((World(3),), ()).startswith("UNKNOWN:"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
