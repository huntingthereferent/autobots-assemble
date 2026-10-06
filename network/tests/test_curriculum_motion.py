from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest

from runtime import EvidenceRecord, ExecutionResult, HandoffRuntime
from systems.missouri_curriculum import (
    homework_task,
    next_worksheet_request,
    reconcile_homework,
    target_by_code,
    worksheet_request,
)
from systems.online_school import task_to_handoff


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
sys.path.insert(0, str(APP))
spec = importlib.util.spec_from_file_location(
    "curriculum_motion_worksheet_engine",
    APP / "worksheet_engine.py",
)
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)


class CurriculumMotionTests(unittest.TestCase):
    def make_homework(self, code, *, learner_id, learner_name, seed=11):
        target = target_by_code(code)
        request = worksheet_request(
            target,
            learner=learner_name,
            seed=seed,
            count=10,
        )
        worksheet = engine.generate_worksheet(request)
        task = homework_task(
            worksheet=worksheet,
            target=target,
            learner_id=learner_id,
            date="2026-10-05",
        )
        handoff = task_to_handoff(task)
        return target, worksheet, task, handoff

    def test_myla_real_missouri_target_becomes_homework_handoff(self):
        target, worksheet, task, handoff = self.make_homework(
            "1.RA.C.7",
            learner_id="track_b",
            learner_name="Myla",
        )

        self.assertEqual(target.title, "Add and subtract within 20")
        self.assertEqual(worksheet["source"]["resolved_math_spec"]["grade"], 1)
        self.assertEqual(worksheet["source"]["resolved_math_spec"]["within"], 20)
        self.assertEqual(handoff.to_actor, "track_b")
        self.assertEqual(handoff.metadata["source_system"], "online-school")
        self.assertEqual(task["meta"]["curriculum_standard"], "1.RA.C.7")
        self.assertEqual(task["meta"]["worksheet_id"], worksheet["worksheet_id"])

    def test_returned_homework_is_evidence_and_advances_to_next_real_target(self):
        target, worksheet, task, handoff = self.make_homework(
            "1.RA.C.7",
            learner_id="track_b",
            learner_name="Myla",
        )
        runtime = HandoffRuntime()
        runtime.submit(handoff)
        state = runtime.return_result(
            handoff.handoff_id,
            actor_id="track_b",
            result=ExecutionResult(
                status="COMPLETE",
                output={
                    "worksheet_id": worksheet["worksheet_id"],
                    "correct": 9,
                    "total": 10,
                },
                evidence=(
                    EvidenceRecord(
                        condition="school task disposition reported",
                        kind="work_artifact",
                        source="track_b",
                        ref=worksheet["worksheet_id"],
                        depth="observed",
                    ),
                ),
            ),
        )
        self.assertEqual(state.status, "COMPLETE")

        movement = reconcile_homework(
            target=target,
            correct=state.output["correct"],
            total=state.output["total"],
        )
        self.assertEqual(movement["movement"], "advance")
        self.assertEqual(movement["next_standard"], "1.RA.C.8")

        next_request = next_worksheet_request(
            movement,
            learner="Myla",
            seed=12,
        )
        next_sheet = engine.generate_worksheet(next_request)

        self.assertEqual(next_sheet["title"], "Fluency within 10")
        self.assertEqual(next_sheet["source"]["resolved_math_spec"]["within"], 10)
        self.assertNotEqual(
            next_sheet["knowledge_goal"],
            worksheet["knowledge_goal"],
        )

    def test_weak_homework_return_changes_level_without_faking_progress(self):
        target, worksheet, task, handoff = self.make_homework(
            "1.RA.C.7",
            learner_id="track_b",
            learner_name="Myla",
        )
        movement = reconcile_homework(
            target=target,
            correct=5,
            total=10,
        )
        self.assertEqual(movement["movement"], "revisit")
        self.assertEqual(movement["next_standard"], "1.RA.C.7")
        self.assertEqual(movement["next_level"], "support")

        next_sheet = engine.generate_worksheet(
            next_worksheet_request(
                movement,
                learner="Myla",
                seed=13,
            )
        )
        self.assertEqual(next_sheet["knowledge_goal"], worksheet["knowledge_goal"])
        self.assertEqual(next_sheet["level"], "support")
        self.assertIn(
            "not automatic mastery",
            movement["boundary"],
        )

    def test_rose_real_path_moves_multiplication_to_division(self):
        target, worksheet, task, handoff = self.make_homework(
            "3.OA.A.1",
            learner_id="track_a",
            learner_name="Rose",
        )
        self.assertEqual(target.title, "Understand multiplication")
        self.assertEqual(worksheet["source"]["resolved_math_spec"]["grade"], 3)

        movement = reconcile_homework(
            target=target,
            correct=10,
            total=10,
        )
        self.assertEqual(movement["next_standard"], "3.OA.A.2")

        next_sheet = engine.generate_worksheet(
            next_worksheet_request(
                movement,
                learner="Rose",
                seed=22,
            )
        )
        self.assertEqual(next_sheet["title"], "Understand division")
        self.assertEqual(
            next_sheet["source"]["resolved_math_spec"]["topic"],
            "division",
        )


if __name__ == "__main__":
    unittest.main()
