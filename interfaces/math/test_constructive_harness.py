import unittest
from work.arc_like_maze.math import World
from interfaces.math.constructive_harness import construct_and_test, demonstration
from interfaces.math.arena import Challenge


class ConstructiveHarnessTests(unittest.TestCase):
    def test_interactions_propose_without_mutating_reference(self):
        world = World(3, (0, 1, 2))
        before = world.apply("ABB")
        result = demonstration()
        self.assertEqual(world.apply("ABB"), before)
        self.assertEqual(result.score["corrected"], 2)
        self.assertEqual(result.score["supported"], 1)
        self.assertTrue(result.proposed_extensions)
        self.assertEqual(result.status, "PROPOSALS_REQUIRE_INDEPENDENT_OBSERVATION")

    def test_no_challenges_no_extensions(self):
        result = construct_and_test(World(3), ())
        self.assertEqual(result.proposed_extensions, ())
        self.assertEqual(result.tested_extensions, ())

    def test_alternative_world_is_a_candidate_not_a_promoted_rule(self):
        reference = World(3, (0, 1, 2))
        other = World(3, (0, 2, 1))
        result = construct_and_test(reference, (
            Challenge("agent", "alternative", "ABB", other.apply("ABB")),
        ))
        self.assertIn(other.phi, result.tested_extensions)
        self.assertEqual(result.baseline, reference.phi)


if __name__ == "__main__":
    unittest.main()
