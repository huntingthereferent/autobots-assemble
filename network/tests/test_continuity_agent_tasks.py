from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from systems.personal_operations import PersonalOperationsStore
from systems.personal_operations.continuity_tasks import (
    ensure_continuity_agent_tasks,
)


ROOT = Path(__file__).resolve().parents[2]


class ContinuityAgentTaskTests(unittest.TestCase):
    def test_three_agent_tasks_seed_duplicate_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            store = PersonalOperationsStore(
                Path(temp) / "personal_operations.jsonl"
            )
            first = ensure_continuity_agent_tasks(store)
            second = ensure_continuity_agent_tasks(store)

            self.assertEqual(len(first), 3)
            self.assertEqual(len(second), 3)
            self.assertEqual(len(store.tasks()), 3)
            self.assertEqual(
                {task.task_id for task in first},
                {task.task_id for task in second},
            )

    def test_finish_site_task_uses_build_ab_not_app_slots(self):
        store = PersonalOperationsStore()
        tasks = ensure_continuity_agent_tasks(store)
        task = next(
            task
            for task in tasks
            if task.title == "Finish Continuity site"
        )

        self.assertEqual(task.assignee, "continuity-agent-pool")
        self.assertEqual(
            task.inputs["start_reference_kind"],
            "build",
        )
        self.assertEqual(
            task.inputs["start_reference"],
            "COMPLETE_STACK.md",
        )
        boundaries = " ".join(task.boundaries).lower()
        self.assertIn("fixed frontend/backend", boundaries)
        self.assertIn("do not add a component", boundaries)
        self.assertIn("james task bridge", boundaries)

    def test_swallow_task_preserves_external_ownership(self):
        store = PersonalOperationsStore()
        tasks = ensure_continuity_agent_tasks(store)
        task = next(
            task
            for task in tasks
            if task.title == "Find things to swallow"
        )

        self.assertEqual(
            task.inputs["start_reference_kind"],
            "research",
        )
        self.assertIn(
            "traverse/connect",
            " ".join(task.boundaries).lower(),
        )
        self.assertIn(
            "native shape",
            " ".join(task.required_witnesses).lower(),
        )

    def test_visual_minmax_is_iterative_and_checks_both_viewports(self):
        store = PersonalOperationsStore()
        tasks = ensure_continuity_agent_tasks(store)
        task = next(
            task
            for task in tasks
            if task.title == "Visual provenance min/max"
        )

        self.assertEqual(
            task.inputs["start_reference_kind"],
            "visual",
        )
        self.assertIn(
            "one visual relation change at a time",
            task.inputs["loop_rule"],
        )
        witnesses = set(task.required_witnesses)
        self.assertIn("desktop fit inspected", witnesses)
        self.assertIn("mobile fit inspected", witnesses)


if __name__ == "__main__":
    unittest.main()
