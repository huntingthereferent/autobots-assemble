from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from school_view import build_school_view
from systems.education import EducationKernel, Observation


class OnlineSchoolWorkspaceTests(unittest.TestCase):
    def state(self):
        return {
            "learners": [
                {"id": "track_a", "display_name": "Learner A", "grade_context": "3"},
                {"id": "track_b", "display_name": "Learner B", "grade_context": "1"},
            ],
            "tasks": [
                {
                    "id": "a-reading",
                    "date": "2026-10-05",
                    "title": "independent reading",
                    "scope": "individual",
                    "learner_ids": ["track_a"],
                    "status": "todo",
                    "planned_minutes": 30,
                    "meta": {},
                },
                {
                    "id": "shared-math",
                    "date": "2026-10-05",
                    "title": "mathematics",
                    "scope": "shared",
                    "learner_ids": ["track_a", "track_b"],
                    "status": "todo",
                    "planned_minutes": 60,
                    "meta": {},
                },
            ],
            "worksheets": [],
        }

    def test_grade_context_adds_obligations_not_learner_state(self):
        view = build_school_view(
            state=self.state(),
            day="2026-10-05",
            kernel=EducationKernel(),
        )
        learner = next(x for x in view["learners"] if x["id"] == "track_a")
        self.assertEqual(learner["grade_context"], "3")
        self.assertTrue(learner["curriculum_obligations"])
        self.assertEqual(learner["current_relations"], [])
        self.assertEqual(learner["observation_count"], 0)

    def test_observation_becomes_current_relation_and_old_relation_stays_back(self):
        kernel = EducationKernel()
        first = kernel.observe(
            Observation.create(
                person_ref="track_b",
                referent="addition across ten",
                observed="counted all objects",
                supports=("count-all available",),
            )
        )
        second = kernel.observe(
            Observation.create(
                person_ref="track_b",
                referent="addition across ten",
                observed="made ten independently",
                supports=("make-ten available",),
                contradicts=("count-all available",),
            )
        )
        view = build_school_view(
            state=self.state(),
            day="2026-10-05",
            kernel=kernel,
        )
        learner = next(x for x in view["learners"] if x["id"] == "track_b")
        self.assertEqual(len(learner["current_relations"]), 1)
        current = learner["current_relations"][0]
        self.assertEqual(current["relation_id"], second.relation_id)
        self.assertEqual(current["supersedes"], first.relation_id)
        self.assertIn("make-ten available", current["supported"])

    def test_shared_schedule_is_not_duplicated_as_individual_movement(self):
        view = build_school_view(
            state=self.state(),
            day="2026-10-05",
            kernel=EducationKernel(),
        )
        learner = next(x for x in view["learners"] if x["id"] == "track_a")
        self.assertEqual([x["id"] for x in learner["today_tasks"]], ["a-reading"])
        self.assertEqual([x["id"] for x in view["shared_today"]], ["shared-math"])

    def test_front_projection_uses_latest_relation_real_next_work_and_latest_observation(self):
        kernel = EducationKernel()
        kernel.observe(
            Observation.create(
                person_ref="track_a",
                referent="multiplication",
                observed="used equal groups",
                supports=("equal groups available",),
            )
        )
        latest = kernel.observe(
            Observation.create(
                person_ref="track_a",
                referent="division",
                observed="shared 12 objects into equal groups",
                supports=("sharing as division available",),
            )
        )
        view = build_school_view(
            state=self.state(),
            day="2026-10-05",
            kernel=kernel,
        )
        learner = next(x for x in view["learners"] if x["id"] == "track_a")
        self.assertEqual(
            learner["front"]["learning_now"]["relation_id"],
            latest.relation_id,
        )
        self.assertEqual(
            learner["front"]["do_next"]["id"],
            "a-reading",
        )
        self.assertEqual(
            learner["front"]["what_changed"]["observed"],
            "shared 12 objects into equal groups",
        )

    def test_front_falls_through_to_shared_real_work_when_no_individual_work_exists(self):
        state = self.state()
        state["tasks"] = [
            task for task in state["tasks"] if task["id"] != "a-reading"
        ]
        view = build_school_view(
            state=state,
            day="2026-10-05",
            kernel=EducationKernel(),
        )
        learner = next(x for x in view["learners"] if x["id"] == "track_a")
        self.assertEqual(
            learner["front"]["do_next"]["id"],
            "shared-math",
        )

    def test_workspace_declares_kernel_routes_and_visual_template(self):
        server = (APP / "server.py").read_text(encoding="utf-8")
        html = (APP / "index.html").read_text(encoding="utf-8")
        self.assertIn('"/api/school"', server)
        self.assertIn('"/api/observations"', server)
        self.assertIn('"/api/learners"', server)
        self.assertNotIn('"display_name": "Learner A"', server)
        self.assertNotIn('"display_name": "Learner B"', server)
        self.assertIn(
            '<meta name="visual-template" content="education_workspace_v1">',
            html,
        )


if __name__ == "__main__":
    unittest.main()
