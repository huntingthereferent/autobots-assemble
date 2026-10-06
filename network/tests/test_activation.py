from pathlib import Path
import unittest

from runtime import Handoff, HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "activations" / "registry.json"


def handoff(handoff_id: str, *, to_actor: str, title: str, relation: str = "move task") -> Handoff:
    return Handoff(
        handoff_id=handoff_id,
        referent=title,
        from_actor="router",
        to_actor=to_actor,
        required_relation=relation,
        metadata={"title": title},
    )


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.registry = ActivationRegistry.from_json(REGISTRY_PATH)

    def test_ohayo_resolves_only_for_james(self):
        route = self.registry.resolve("ohayo", actor_id="james")
        self.assertIsNotNone(route)
        self.assertEqual(route.activation_id, "ACT-JAMES-OHAYO-001")
        self.assertEqual(route.projection, "task_queue")

        self.assertIsNone(self.registry.resolve("ohayo", actor_id="dessy"))
        self.assertIsNone(self.registry.resolve("hello", actor_id="james"))

    def test_activation_surface_allows_case_and_whitespace_only(self):
        route = self.registry.resolve("  OHAYO  ", actor_id="JAMES")
        self.assertIsNotNone(route)
        self.assertEqual(route.referent, "James / current day")

    def test_ohayo_selects_james_tasks_from_mixed_ecosystem(self):
        runtime = HandoffRuntime()

        james_school = handoff(
            "james-school",
            to_actor="james",
            title="Check Online School task monitor",
        )
        james_runtime = handoff(
            "james-runtime",
            to_actor="james",
            title="Review factory handoff trace",
        )
        other_person = handoff(
            "other-person",
            to_actor="learner-a",
            title="Mathematics",
        )
        complete_james = handoff(
            "complete-james",
            to_actor="james",
            title="Already finished item",
        )

        for item in (james_school, james_runtime, other_person, complete_james):
            runtime.submit(item)

        # With no required witness this handoff can close from an explicit result.
        from runtime import ExecutionResult
        runtime.return_result(
            "complete-james",
            actor_id="james",
            result=ExecutionResult(status="COMPLETE", output={"done": True}),
        )

        route = self.registry.resolve("ohayo", actor_id="james")
        pairs = [
            (item, runtime.state(item.handoff_id))
            for item in (james_school, james_runtime, other_person, complete_james)
        ]
        result = run_activation(route, surface="ohayo", handoffs=pairs)

        self.assertEqual(
            {item["id"] for item in result.items},
            {"james-school", "james-runtime"},
        )
        self.assertTrue(all(item["assignee"] == "james" for item in result.items))
        self.assertNotIn("Already finished item", {item["title"] for item in result.items})
        self.assertNotIn("Mathematics", {item["title"] for item in result.items})

    def test_ohayo_is_projection_not_state_mutation(self):
        runtime = HandoffRuntime()
        item = handoff("james-one", to_actor="james", title="One task")
        runtime.submit(item)

        before_events = runtime.event_store.all()
        before_state = runtime.state(item.handoff_id)

        route = self.registry.resolve("ohayo", actor_id="james")
        run_activation(
            route,
            surface="ohayo",
            handoffs=[(item, before_state)],
        )

        self.assertEqual(runtime.event_store.all(), before_events)
        self.assertEqual(runtime.state(item.handoff_id), before_state)

    def test_ohayo_boundaries_forbid_rigid_schedule_and_invented_tasks(self):
        route = self.registry.resolve("ohayo", actor_id="james")
        boundaries = " ".join(route.boundaries).lower()
        self.assertIn("do not invent a rigid hourly schedule", boundaries)
        self.assertIn("do not convert notes or observations into tasks", boundaries)
        self.assertIn("do not infer household obligations", boundaries)

    def test_empty_queue_is_valid(self):
        route = self.registry.resolve("ohayo", actor_id="james")
        result = run_activation(route, surface="ohayo", handoffs=[])
        self.assertEqual(result.items, ())
        self.assertIn("no new work was inferred", result.note.lower())


if __name__ == "__main__":
    unittest.main()
