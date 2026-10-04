"""Hermetic tests for Gen-1 ARC3 perception/model code."""
from __future__ import annotations

import unittest

import numpy as np

from state import infer_directional_translation, perceive_grid
from model import TransitionModel


def board(x: int, y: int, marker: bool = False) -> np.ndarray:
    g = np.zeros((64, 64), dtype=np.int8)
    g[y:y+2, x:x+2] = 3
    if marker:
        g[50:52, 50:52] = 7
    return g


class PerceptionTests(unittest.TestCase):
    def test_exact_key_changes_with_one_pixel_indicator(self):
        a = board(10, 10)
        b = a.copy()
        b[1, 1] = 9
        self.assertNotEqual(perceive_grid(a).exact_key, perceive_grid(b).exact_key)

    def test_object_state_tracks_translation(self):
        a = perceive_grid(board(10, 10))
        b = perceive_grid(board(9, 10))
        moved = infer_directional_translation(a, b, 3)
        self.assertIsNotNone(moved)
        sig, dx2, dy2 = moved
        self.assertEqual(sig[:2], (3, 4))
        self.assertLess(dx2, 0)
        self.assertEqual(dy2, 0)


class ModelTests(unittest.TestCase):
    def test_object_transition_reuse(self):
        m = TransitionModel()
        s0 = perceive_grid(board(10, 10))
        s1 = perceive_grid(board(9, 10))
        m.update(s0, (3,), s1, level_delta=0, terminal_bad=False)
        edge = m.object_edge(s0, (3,))
        self.assertIsNotNone(edge)
        self.assertTrue(edge.changed)

    def test_conflicting_abstract_outcomes_do_not_override_exact_evidence(self):
        m = TransitionModel()
        s0 = perceive_grid(board(10, 10))
        s1 = perceive_grid(board(9, 10))
        s2 = perceive_grid(board(8, 10))
        m.update(s0, (3,), s1, level_delta=0, terminal_bad=False)
        m.object_votes[(s0.object_key, (3,))][(s2.object_key, 0, True, False)] += 1
        self.assertIsNone(m.object_edge(s0, (3,)))
        self.assertAlmostEqual(m.object_confidence(s0, (3,)), 0.5)
        self.assertAlmostEqual(m.confidence(s0, (3,)), 1.0)

    def test_bfs_finds_known_progress(self):
        m = TransitionModel()
        s0 = perceive_grid(board(10, 10))
        s1 = perceive_grid(board(9, 10))
        s2 = perceive_grid(board(8, 10, marker=True))
        m.update(s0, (3,), s1, level_delta=0, terminal_bad=False)
        m.update(s1, (3,), s2, level_delta=1, terminal_bad=False)
        plan = m.plan_to_known_progress(s0, [(1,), (2,), (3,), (4,)])
        self.assertEqual(plan, [(3,), (3,)])


if __name__ == "__main__":
    unittest.main()
