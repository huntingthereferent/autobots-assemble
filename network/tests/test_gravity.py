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


    def test_dispatch_runs_internal_handler(self):
        from systems.workspace.gravity import anchored_dispatch
        called = []
        world = World("rea", ("build", "witness"))
        result = anchored_dispatch(world, (
            Move("fetch", "outside", required_for="witness"),
            Move("build", "inside")), internal_handlers={
                "build": lambda: called.append("build") or "done"})
        self.assertEqual(called, ["build"])
        self.assertEqual(result["state"], "DISPATCHED")

    def test_missing_handler_does_not_execute(self):
        from systems.workspace.gravity import anchored_dispatch
        world = World("rea", ("build",))
        result = anchored_dispatch(world, (Move("build", "inside"),),
                                   internal_handlers={})
        self.assertEqual(result["state"], "UNSTAFFED")
        self.assertFalse(result["executed"])

    def test_external_handler_not_called_when_inside_available(self):
        from systems.workspace.gravity import anchored_dispatch
        called = []
        world = World("rea", ("build", "witness"))
        result = anchored_dispatch(world, (
            Move("fetch", "outside", required_for="witness"),
            Move("build", "inside")), internal_handlers={"build": lambda: "ok"},
            external_handler=lambda _: called.append("external"))
        self.assertEqual(result["operation"], "build")
        self.assertEqual(called, [])

if __name__ == "__main__":
    unittest.main()
