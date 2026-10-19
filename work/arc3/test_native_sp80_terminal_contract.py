"""Regression contract: the native runner must not step after explicit terminal."""
import unittest
from types import SimpleNamespace

import numpy as np

from work.arc3.native_sp80_frozen_color_contexts import (
    classify_original_native_terminal, steps_on_real_game)


class FakeNativeEnvironment:
    def __init__(self, terminal_at, stage1):
        self.terminal_at=terminal_at
        self.stage1=stage1
        self.calls=0

    def observation(self):
        level=1 if self.stage1 and self.calls>=6 else 0
        state=("GAME_OVER" if self.calls==self.terminal_at else "NOT_FINISHED")
        grid=np.full((1,64,64),self.calls%16,dtype=np.uint8)
        return SimpleNamespace(
            frame=grid,
            levels_completed=level,
            state=state,
            available_actions=[4,5]
        )

    def reset(self):
        self.calls=0
        return self.observation()

    def step(self, action):
        self.calls+=1
        if self.calls>self.terminal_at:
            raise AssertionError("Native SDK called after explicit terminal")
        return self.observation()


class FakeArcade:
    def __init__(self, terminal_at, stage1=False):
        self.env=FakeNativeEnvironment(terminal_at,stage1)

    def make(self, game):
        assert game=="sp80"
        return self.env


class ExplicitNativeTerminalTests(unittest.TestCase):
    def test_enum_names_and_nonterminals(self):
        self.assertEqual(classify_original_native_terminal(
            SimpleNamespace(state="GameState.GAME_OVER")),"NATIVE_TERMINAL_GAME_OVER")
        self.assertEqual(classify_original_native_terminal(
            SimpleNamespace(state=SimpleNamespace(name="WIN"))),"NATIVE_TERMINAL_WIN")
        self.assertIsNone(classify_original_native_terminal(
            SimpleNamespace(state="GameState.NOT_FINISHED")))

    def test_stage0_keeps_valid_terminal_frame_without_extra_step(self):
        arcade=FakeArcade(terminal_at=1)
        record,frames=steps_on_real_game(arcade,"4444",0,0)
        self.assertEqual(arcade.env.calls,1)
        self.assertEqual(record["real_native_actions"],1)
        self.assertEqual(record["status"],"NATIVE_TERMINAL_GAME_OVER")
        self.assertEqual(record["terminal_observation"]["native_action_index"],1)
        self.assertEqual(record["terminal_observation"]["context_action_step"],1)
        self.assertTrue(record["terminal_observation"]["frame_available"])
        self.assertEqual(frames.shape,(2,64,64))
        self.assertEqual(len(record["transition_records"]),1)
        self.assertEqual(record["errors"],[])
        self.assertFalse(record["complete"])

    def test_stage1_entry_then_exact_terminal_record(self):
        arcade=FakeArcade(terminal_at=7,stage1=True)
        record,frames=steps_on_real_game(arcade,"4444",1,0)
        self.assertEqual(arcade.env.calls,7)
        self.assertEqual(record["stage_root_index"],6)
        self.assertEqual(record["real_native_actions"],7)
        self.assertEqual(record["status"],"NATIVE_TERMINAL_GAME_OVER")
        self.assertEqual(record["terminal_observation"]["native_action_index"],7)
        self.assertEqual(record["terminal_observation"]["context_action_step"],1)
        self.assertEqual(record["terminal_observation"]["level"],1)
        self.assertEqual(len(record["transition_records"]),7)
        self.assertEqual(frames.shape,(8,64,64))


if __name__=="__main__":
    unittest.main()
