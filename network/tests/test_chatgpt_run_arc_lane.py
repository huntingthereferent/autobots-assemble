"""Synthetic, SDK-free negative and receipt tests for the ChatGPT Run ARC lane."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from research.arc_native_runs.chatgpt_run import ObservedArc, frame_digest, run, validate


def observation(color: int, *, state: str = "NOT_FINISHED", levels: int = 0):
    board = [0] * 4096
    board[36 * 64 + 36] = color
    return SimpleNamespace(
        frame=[board],
        levels_completed=levels,
        state=SimpleNamespace(name=state),
    )


class FakeEnvironment:
    def __init__(self, *, ending="WIN", levels=6):
        self.observation_space = observation(2)
        self.ending = ending
        self.levels = levels
        self.actions = []

    def step(self, action, *args, **kwargs):
        self.actions.append(action)
        self.observation_space = observation(
            3, state=self.ending, levels=self.levels
        )
        return self.observation_space


class FakeArcade:
    def __init__(self, env):
        self.env = env
    def make(self, game):
        if game != "ft09":
            raise ValueError("unexpected game")
        return self.env


class FakeAgent:
    def __init__(self, *, arc_env, **kwargs):
        self.arc_env = arc_env
        self.frames = []
        self.failures = []

    def main(self):
        result = self.arc_env.step(SimpleNamespace(name="ACTION6", data={"x": 36, "y": 36}))
        self.frames.append(result)


class DishonestAgent(FakeAgent):
    def main(self):
        super().main()
        self.frames.append(observation(8, state="WIN", levels=6))


class BrokenAgent(FakeAgent):
    def main(self):
        raise RuntimeError("simulated native execution fault")


class ChatGPTRunLaneTests(unittest.TestCase):
    def test_frame_hash_public_64x64_only(self):
        self.assertEqual(len(frame_digest(observation(2))), 64)
        self.assertIsNone(frame_digest(SimpleNamespace(frame=[[2]])))

    def test_admission_refuses_mismatched_game_and_missing_model_authority(self):
        with self.assertRaisesRegex(ValueError, "only valid"):
            validate("sk48", "ft09-visible", 80, None, key=None)
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            validate("ft09", "chatgpt-model", 80, "gpt-example", key=None)
        with self.assertRaisesRegex(ValueError, "between 1 and 200"):
            validate("ft09", "ft09-visible", 0, None, key=None)

    def test_native_win_creates_scoped_receipt(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "receipt.json"
            result = run(game="ft09", policy="ft09-visible", budget=10, model=None,
                         output=output, arcade_factory=lambda: FakeArcade(FakeEnvironment()),
                         policy_class=FakeAgent)
            self.assertTrue(result["native_win_observed"])
            self.assertEqual(result["claim"], "FRESH_LOCAL_NATIVE_WIN_NOT_INDEPENDENTLY_REPRODUCED")
            self.assertEqual(result["action_count"], 1)
            self.assertEqual(len(json.loads(output.read_text())["transitions"]), 1)
            self.assertTrue(result["transitions"][0]["before_frame_sha256"])
            self.assertTrue(result["transitions"][0]["after_frame_sha256"])
            self.assertEqual(result["transitions"][0]["coordinates"], {"x": 36, "y": 36})

    def test_no_fabricated_win_from_policy_response(self):
        with TemporaryDirectory() as tmp:
            result = run(game="ft09", policy="ft09-visible", budget=10, model=None,
                         output=Path(tmp) / "receipt.json",
                         arcade_factory=lambda: FakeArcade(FakeEnvironment(ending="NOT_FINISHED", levels=0)),
                         policy_class=DishonestAgent)
            self.assertFalse(result["native_win_observed"])
            self.assertEqual(result["claim"], "NO_VERIFIED_WIN")

    def test_failure_produces_negative_receipt(self):
        with TemporaryDirectory() as tmp:
            result = run(game="ft09", policy="ft09-visible", budget=10, model=None,
                         output=Path(tmp) / "receipt.json",
                         arcade_factory=lambda: FakeArcade(FakeEnvironment()),
                         policy_class=BrokenAgent)
            self.assertFalse(result["native_win_observed"])
            self.assertIn("simulated native execution fault", result["error"])
            self.assertEqual(result["action_count"], 0)

    def test_observer_does_not_execute_without_worker(self):
        env = FakeEnvironment()
        observer = ObservedArc(env)
        self.assertEqual(observer.transitions, [])
        self.assertEqual(env.actions, [])


if __name__ == "__main__":
    unittest.main()
