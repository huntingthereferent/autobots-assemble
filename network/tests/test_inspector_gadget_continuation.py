"""Inspector Gadget calendar dispatches existing owner workers, not surrogate agents."""
import datetime as dt
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from systems.workspace.inspector_gadget_continuation import ROSTER, assess, run, validate

NOW = dt.datetime(2026, 10, 22, 23, 30, tzinfo=dt.timezone.utc)
REPO = "huntingthereferent/autobots-assemble"


def record(name, *, cooldown=360, enabled=True):
    return {"id": name, "filename": f"{name}.yml",
            "min_interval_minutes": cooldown, "enabled": enabled}


def mock_registry(*names, cap=4):
    return {"schema": "inspector-gadget/native-worker-calendar/v1",
            "ref": "main", "max_dispatch_per_tick": cap,
            "workers": [record(n) for n in names]}


def native_run(minutes_ago, *, status="completed", conclusion="success"):
    clock = (NOW - dt.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"created_at": clock, "status": status, "conclusion": conclusion}


class NativeLaneContinuationTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = TemporaryDirectory()
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        directory = self.root / ".github" / "workflows"
        directory.mkdir(parents=True)
        for name in ("arc", "nih", "world", "meow"):
            (directory / f"{name}.yml").write_text(
                "name: owner-worker\non:\n  workflow_dispatch:\njobs:\n  native:\n    runs-on: ubuntu-latest\n    steps: []\n", encoding="utf8")

    def test_repository_worker_relations_derive_from_current_roster(self):
        roster = json.loads(ROSTER.read_text(encoding="utf8"))
        entries = validate(roster)
        self.assertEqual(entries, roster["workers"])
        self.assertEqual(len({row["id"] for row in entries}), len(entries))
        self.assertEqual(len({row["filename"] for row in entries}), len(entries))
        self.assertTrue(all(row["enabled"] in (True, False) for row in entries))

    def test_roster_change_does_not_require_hardcoded_worker_names(self):
        roster = mock_registry("arc", "nih", "world")
        initial = validate(roster, self.root)
        roster["workers"] = [row for row in initial if row["id"] != "nih"]
        self.assertEqual({row["id"] for row in validate(roster, self.root)},
                         {"arc", "world"})
        plan = assess(roster, {"arc": [], "world": []},
                      repo=REPO, now=NOW, root=self.root)
        self.assertEqual({row["id"] for row in plan["selected"]},
                         {"arc", "world"})

    def test_all_eligible_workers_are_selected_up_to_capacity(self):
        registry = mock_registry("arc", "nih", "world", "meow")
        histories = {name: [] for name in ("arc", "nih", "world", "meow")}
        result = assess(registry, histories, repo=REPO, now=NOW, root=self.root)
        self.assertEqual(result["selected_count"], 4)
        self.assertEqual({row["id"] for row in result["selected"]},
                         {"arc", "nih", "world", "meow"})

    def test_completed_runs_do_not_block_dispatch_but_active_runs_do(self):
        registry = mock_registry("arc", "nih", "world")
        histories = {"arc": [native_run(15)], "nih": [native_run(500, status="in_progress")],
                     "world": [native_run(500)]}
        result = assess(registry, histories, repo=REPO, now=NOW, root=self.root)
        self.assertEqual({r["id"] for r in result["selected"]}, {"arc", "world"})
        states = {r["id"]: r["state"] for r in result["workers"]}
        self.assertEqual(states["arc"], "SELECTED")
        self.assertEqual(states["nih"], "ALREADY_RUNNING")

    def test_decision_replays_from_same_observations(self):
        registry = mock_registry("arc", "nih", "world")
        observations = {
            "arc": [native_run(10), native_run(20)],
            "nih": [native_run(5, status="in_progress")],
            "world": [],
        }
        first = assess(registry, observations, repo=REPO, now=NOW, root=self.root)
        reordered = {key: list(reversed(value)) for key, value in observations.items()}
        later = assess(registry, reordered, repo=REPO,
                       now=NOW + dt.timedelta(hours=2), root=self.root)
        self.assertEqual(first["decision_digest"], later["decision_digest"])
        self.assertEqual([r["id"] for r in first["selected"]],
                         [r["id"] for r in later["selected"]])
        self.assertNotIn("nih", {r["id"] for r in later["selected"]})

    def test_changed_owner_observation_changes_decision(self):
        registry = mock_registry("arc")
        idle = assess(registry, {"arc": []}, repo=REPO, now=NOW, root=self.root)
        active = assess(registry, {"arc": [native_run(1, status="queued")]},
                        repo=REPO, now=NOW, root=self.root)
        self.assertNotEqual(idle["decision_digest"], active["decision_digest"])
        self.assertEqual(active["selected_count"], 0)

    def test_existing_worker_execution_is_really_dispatched(self):
        registry = mock_registry("arc", "nih")
        events = []
        def reader(repo, filename, token):
            events.append(("read", filename))
            return []
        def sender(filename):
            events.append(("dispatch", filename))
            return {"accepted": True}
        result = run(registry, repo=REPO, token="fake",
                     reader=reader, sender=sender, root=self.root)
        self.assertEqual(result["selected_count"], 2)
        self.assertEqual([e for e in events if e[0] == "dispatch"],
                         [("dispatch", "arc.yml"), ("dispatch", "nih.yml")])
        self.assertTrue(all(r["result"] == "DISPATCH_ACCEPTED" for r in result["receipts"]))

    def test_history_failure_does_not_stop_other_native_workers(self):
        def reader(repo, filename, token):
            if filename == "arc.yml":
                raise OSError("GitHub history temporarily unavailable")
            return []
        sent = []
        result = run(mock_registry("arc", "nih"), repo=REPO, token="fake",
                     reader=reader, sender=lambda filename: (sent.append(filename) or {"accepted": True}),
                     root=self.root)
        self.assertEqual(sent, ["nih.yml"])
        self.assertEqual(result["workers"][0]["state"], "HISTORY_UNAVAILABLE")
        self.assertIn("arc", result["history_errors"])

    def test_failed_dispatch_is_not_claimed_as_movement(self):
        result = run(mock_registry("arc"), repo=REPO,
                     token="fake", reader=lambda *a: [],
                     sender=lambda *a: {"accepted": False}, root=self.root)
        self.assertEqual(result["dispatch_failures"], ["arc"])
        self.assertEqual(result["receipts"][0]["result"], "DISPATCH_FAILED")

    def test_calendar_budget_does_not_block_ready_lanes(self):
        registry = mock_registry("arc", "nih", "world", "meow", cap=2)
        result = assess(registry, {name: [] for name in ("arc", "nih", "world", "meow")},
                        repo=REPO, now=NOW, root=self.root)
        self.assertEqual(result["selected_count"], 4)
        self.assertEqual(result["capacity_wait"], 0)
        self.assertEqual(sum(r["state"] == "CAPACITY_WAIT" for r in result["workers"]), 0)

    def test_unknown_worker_cannot_be_substituted_with_prompt(self):
        registry = mock_registry("arc")
        (self.root / ".github/workflows/arc.yml").write_text(
            "name: not-dispatchable\non:\n  pull_request:\n", encoding="utf8")
        with self.assertRaisesRegex(ValueError, "no workflow_dispatch"):
            validate(registry, self.root)

    def test_missing_worker_history_blocks_all_dispatch(self):
        with self.assertRaisesRegex(ValueError, "history missing"):
            assess(mock_registry("arc"), {}, repo=REPO, now=NOW, root=self.root)

    def test_invalid_owning_repository_blocks_all_dispatch(self):
        with self.assertRaisesRegex(ValueError, "owning GitHub repository"):
            assess(mock_registry("arc"), {"arc": []},
                   repo="unapproved", now=NOW, root=self.root)

    def test_empty_or_disabled_workflows_are_not_dispatched(self):
        registry = mock_registry("arc")
        registry["workers"][0]["enabled"] = False
        result = run(registry, repo=REPO, token="fake",
                     reader=lambda *args: self.fail("must not fetch a disabled worker"),
                     sender=lambda *args: self.fail("must not dispatch"),
                     root=self.root)
        self.assertEqual(result["selected_count"], 0)
        self.assertEqual(result["workers"][0]["state"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
