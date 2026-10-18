"""F3 agent conformance to original mathematics; no native game is run."""
from __future__ import annotations

from enum import Enum
import importlib.util
from itertools import product
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np  # import before patch.dict: native extension cannot be reimported

from work.arc_like_maze.math import inverse_candidates


FILE = Path(__file__).resolve().parents[2] / "work/arc3/archive/nine_law_agent_2026-10-17.py"


def load_single_file():
    agents = ModuleType("agents")
    agent = ModuleType("agents.agent")
    class StubAgent:
        def __init__(self, *args, **kwargs):
            pass
    agent.Agent = StubAgent
    arcengine = ModuleType("arcengine")
    class Action(Enum):
        RESET = 0
        ACTION1 = 1
        ACTION2 = 2
        ACTION3 = 3
        ACTION4 = 4
        ACTION5 = 5
        ACTION6 = 6
        ACTION7 = 7
        def set_data(self, data):
            self.action_data = data
    class State(Enum):
        NOT_PLAYED = 0
        NOT_FINISHED = 1
        WIN = 2
        GAME_OVER = 3
    arcengine.FrameData = object
    arcengine.GameAction = Action
    arcengine.GameState = State
    spec = importlib.util.spec_from_file_location("arc3_f3_agent_test", FILE)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"agents": agents, "agents.agent": agent,
                                  "arcengine": arcengine, spec.name: module}):
        spec.loader.exec_module(module)
    return module, Action, State


class F3CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f3, cls.Action, cls.State = load_single_file()

    def test_source_transforms_are_exact_for_every_state_and_world(self):
        for source in inverse_candidates():
            for state in product(range(3), repeat=3):
                for letter in "AB":
                    self.assertEqual(self.f3.f3_step(state, letter, source.phi),
                                     source.step(state, letter))

    def test_rooted_words_match_original_worlds(self):
        for source in inverse_candidates():
            for word in ("", "A", "B", "BBB", "ABABAB", "AABAB", "BBAAAB", "ABBBABAA"):
                self.assertEqual(self.f3.f3_endpoint(word, source.phi), source.apply(word))

    def test_all_nine_original_laws_admitted_without_native_evidence(self):
        self.assertEqual(tuple(s.phi for s in inverse_candidates()), self.f3.PHIS)
        evidence = self.f3.F3Evidence(1, 2, b"root")
        self.assertEqual(evidence.report().status, "CONDITIONAL_F3_CANDIDATES")
        self.assertEqual(len(evidence.candidates), 9)

    def test_native_distinction_refutes_f3_forced_return(self):
        evidence = self.f3.F3Evidence(1, 2, b"root")
        evidence.record("A", b"one")
        evidence.record("A", b"two")
        result = evidence.record("A", b"different")
        self.assertEqual(result.status, "OUTSIDE_DECLARED_F3_FAMILY")
        self.assertEqual(result.candidate_indices, ())

    def test_visible_equality_is_not_claimed_as_hidden_state_identity(self):
        evidence = self.f3.F3Evidence(1, 2, b"root")
        result = evidence.record("A", b"root")
        self.assertEqual(result.status, "CONDITIONAL_F3_CANDIDATES")
        self.assertEqual(len(result.candidate_indices), 9)
        self.assertEqual(result.visible_equalities, 1)

    def test_finite_field_probe_rank_uses_predicted_collisions(self):
        evidence = self.f3.F3Evidence(1, 2, b"root")
        self.assertEqual(set(evidence.rank_letters()), {"A", "B"})
        evidence.record("B", b"different")
        self.assertEqual(set(evidence.rank_letters()), {"A", "B"})

    def test_native_colors_not_reduced_modulo_three(self):
        grid = np.zeros((64, 64), dtype=np.uint8)
        first = self.f3.observation_key(SimpleNamespace(frame=[grid]))
        grid[0, 0] = 15
        second = self.f3.observation_key(SimpleNamespace(frame=[grid]))
        self.assertNotEqual(first, second)
        grid[0, 0] = 3
        self.assertNotEqual(second, self.f3.observation_key(SimpleNamespace(frame=[grid])))

    def test_agent_reports_a_provisional_generator(self):
        runner = self.f3.MyAgent()
        native = SimpleNamespace(frame=[np.zeros((64,64), dtype=np.uint8)],
                                 available_actions=[self.Action.ACTION1, self.Action.ACTION2],
                                 levels_completed=0, state=self.State.NOT_FINISHED)
        action = runner.choose_action([], native)
        self.assertIn(action, (self.Action.ACTION1, self.Action.ACTION2))
        self.assertTrue(action.reasoning["hypothesis_only"])
        self.assertEqual(action.reasoning["candidate_count"], 9)

    def test_no_unadvertised_second_generator(self):
        runner = self.f3.MyAgent()
        native = SimpleNamespace(frame=[np.zeros((64,64), dtype=np.uint8)],
                                 available_actions=[self.Action.ACTION5],
                                 levels_completed=0, state=self.State.NOT_FINISHED)
        action = runner.choose_action([], native)
        self.assertEqual(action, self.Action.ACTION5)
        self.assertIsNone(runner.f3)
        self.assertEqual(action.reasoning["status"], "WALL_NO_ADMITTED_F3_CORRESPONDENCE")


if __name__ == "__main__":
    unittest.main()
