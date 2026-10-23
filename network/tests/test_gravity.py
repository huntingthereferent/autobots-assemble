"""Finite-world gravity decisions: internal motion before external dependency."""
import unittest
from systems.workspace.gravity import World, Move, gravity

class GravityTests(unittest.TestCase):
    def test_internal_wins_over_external(self):
        world = World("rea", ("native-build", "rea-witness"))
        result = gravity(world, (
            Move("fetch-rea", "outside", required_for="rea-witness"),
            Move("native-build", "inside", evidence="fixture"),
        ))
        self.assertEqual(result["decision"], "continue_inside")
        self.assertEqual(result["operation"], "native-build")

    def test_wall_does_not_stop_other_branch(self):
        world = World("rea", ("native-build", "rea-witness"), walls=("rea-witness",))
        result = gravity(world, (Move("rea-witness", "blocked"),
                                 Move("native-build", "inside")))
        self.assertEqual(result["decision"], "continue_inside")

    def test_outside_only_if_required(self):
        world = World("rea", ("rea-witness",))
        self.assertEqual(gravity(world, (Move("unrelated", "outside", required_for="other"),))["decision"], "retain_wall")
        self.assertEqual(gravity(world, (Move("fetch-rea", "outside", required_for="rea-witness"),))["decision"], "external_dependency")

    def test_empty_world_rejected(self):
        with self.assertRaises(ValueError):
            gravity(World("", ("test",)), ())

if __name__ == "__main__":
    unittest.main()
