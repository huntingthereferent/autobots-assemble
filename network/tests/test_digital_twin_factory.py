import json
"""No-network contract tests for digital twin factory admission."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from systems.workspace.digital_twin_factory import (
    birth_decision, birth_twin, checked_repo, observe_account,
)


def samples(running=20, queued=3, owner="huntingthereferent", complete=True):
    start = datetime(2026, 10, 22, 14, tzinfo=timezone.utc)
    return [{
        "schema": "digital-twin-capacity/v1",
        "owner": owner,
        "observed_at": (start + timedelta(seconds=80*i)).isoformat(),
        "running": running, "queued": queued,
        "concurrency_ceiling": 20, "fully_enumerated": complete,
    } for i in range(3)]


class DigitalTwinFactoryTests(unittest.TestCase):
    def test_sustained_saturation_qualifies(self):
        result = birth_decision(samples())
        self.assertTrue(result["spawn"])
        self.assertEqual(result["source_samples"], 3)

    def test_unqualified_states_do_not_spawn(self):
        variants = [
            samples()[:2], samples(running=19), samples(queued=0),
            samples(complete=False),
        ]
        for history in variants:
            with self.subTest(history=history):
                self.assertFalse(birth_decision(history)["spawn"])

    def test_unknown_or_mismatched_source_refused(self):
        history = samples()
        history[-1]["owner"] = "aeren-research"
        self.assertFalse(birth_decision(history)["spawn"])
        history = samples()
        history[1]["observed_at"] = history[0]["observed_at"]
        self.assertFalse(birth_decision(history)["spawn"])

    def test_target_cannot_be_same_or_ambiguous(self):
        with self.assertRaises(ValueError):
            checked_repo("../bad")
        with self.assertRaises(PermissionError):
            birth_twin(source="huntingthereferent/autobots-assemble",
                       target="huntingthereferent/autobots-assemble",
                       source_sha="a"*40, confirm="huntingthereferent/autobots-assemble")

    @patch("systems.workspace.digital_twin_factory._github_get")
    def test_account_observer_counts_all_repos_not_last_100(self, get):
        get.side_effect = [
            {"login": "huntingthereferent"},
            [{"full_name": "huntingthereferent/repo1", "owner": {"login": "huntingthereferent"}},
             {"full_name": "huntingthereferent/repo2", "owner": {"login": "huntingthereferent"}}],
            {"total_count": 12}, {"total_count": 6},
            {"total_count": 8}, {"total_count": 2},
        ]
        observed = observe_account("huntingthereferent", "token")
        self.assertEqual(observed["running"], 20)
        self.assertEqual(observed["queued"], 8)
        self.assertEqual(len(observed["repositories"]), 2)
        self.assertEqual(get.call_count, 6)

    @patch("systems.workspace.digital_twin_factory._github_get")
    def test_wrong_owner_token_rejected(self, get):
        get.return_value = {"login": "other"}
        with self.assertRaises(PermissionError):
            observe_account("huntingthereferent", "token")

    @patch("systems.workspace.digital_twin_factory._run")
    def test_existing_target_never_overwritten(self, run):
        run.return_value = "aeren-research"
        with patch("systems.workspace.digital_twin_factory.subprocess.run") as cmd:
            cmd.return_value.returncode = 0
            with self.assertRaises(FileExistsError):
                birth_twin(source="huntingthereferent/autobots-assemble",
                           target="aeren-research/autobots-assemble-twin-01",
                           source_sha="b"*40,
                           confirm="aeren-research/autobots-assemble-twin-01")
            self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
