"""48-law ARC entry: exact ORIGINAL WindowCombined mathematics, no native game.

Archive tests for the previous nine-law agent remain separately pinned to its
archived source. The canonical single-file entry must match all 48 mathematical
laws on every finite 3-coordinate state (not merely the marked origin).
"""
from __future__ import annotations

from enum import Enum
import importlib.util
from itertools import product
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from work.arc_like_maze.window_combined import (
    family, combined_rule, classify_pair, rooted_conflict,
    CombinedWorld
)


FILE = Path(__file__).resolve().parents[2] / "work/arc3/agent/my_agent.py"


def load_entry():
    agents=ModuleType("agents")
    sub=ModuleType("agents.agent")
    class Agent:
        def __init__(self,*args,**kwargs):
            pass
    sub.Agent=Agent
    arc=ModuleType("arcengine")
    class Action(Enum):
        RESET=0
        ACTION1=1
        ACTION2=2
        ACTION3=3
        ACTION4=4
        ACTION5=5
        ACTION6=6
        ACTION7=7
        def set_data(self, data):
            self.action_data=data
    class State(Enum):
        NOT_PLAYED=0
        NOT_FINISHED=1
        WIN=2
        GAME_OVER=3
    arc.FrameData=object
    arc.GameAction=Action
    arc.GameState=State
    spec=importlib.util.spec_from_file_location("arc3_window48_entry",FILE)
    module=importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules,{"agents":agents,"agents.agent":sub,
                                 "arcengine":arc,spec.name:module}):
        spec.loader.exec_module(module)
    return module,Action,State


class Window48SourceConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry,cls.Action,cls.State=load_entry()
        cls.original=family()

    def test_all_48_sources_in_original_order(self):
        self.assertEqual(len(self.entry.WINDOW48),48)
        self.assertEqual(len(set(self.entry.WINDOW48)),48)
        self.assertEqual(self.entry.WINDOW48,
                         tuple((w.support,w.coefficient,w.pulse,w.balanced)
                               for w in self.original))

    def test_all_nine_table_entries_match_every_original_law(self):
        for world,law in zip(self.original,self.entry.WINDOW48):
            source=combined_rule(world.support,world.coefficient,
                                 world.pulse,world.balanced)
            self.assertEqual(tuple(
                self.entry.window48_q(u,v,law)
                for u,v in product(range(3),repeat=2)),source)

    def test_every_state_every_action_matches_original_source(self):
        for world,law in zip(self.original,self.entry.WINDOW48):
            for state in product(range(3),repeat=3):
                for letter in "AB":
                    self.assertEqual(self.entry.window48_step(state,letter,law),
                                     world.step(state,letter))
                    self.assertEqual(self.entry.window48_inverse(state,letter,law),
                                     world.inverse(state,letter))
                    self.assertEqual(self.entry.window48_inverse(
                        self.entry.window48_step(state,letter,law),letter,law),state)

    def test_rooted_word_endpoints_match_original_sources(self):
        words=("","A","B","AAA","BBB","AB","BA","AABAB",
               "ABABAB","BAB","BBBA","BABA","ABBA")
        for world,law in zip(self.original,self.entry.WINDOW48):
            for word in words:
                self.assertEqual(self.entry.window48_endpoint(word,law),
                                 world.apply((0,0,0),word))

    def test_origin_marked_classes_not_collapsed_into_full_classes(self):
        self.assertEqual(self.entry.ROOTED_CLASS_COUNT,16)
        self.assertEqual(self.entry.FULL_STATE_CLASS_COUNT,14)
        root_classes={(w.support,w.pulse,w.balanced) for w in self.original}
        self.assertEqual(len(root_classes),16)
        # k=0 / 3 and pulse=1 admit full but NONROOT conjugacies.
        for k in (0,3):
            a=CombinedWorld(k,0,1,0)
            b=CombinedWorld(k,0,1,1)
            relation=classify_pair(a,b)
            self.assertFalse(relation.root_preserving)
            self.assertEqual(relation.status,"ALL_DEPTH_FULL_STATE_NONROOT_CONJUGACY")
            self.assertIsNotNone(rooted_conflict(a,b))
        # Same parameter branch, differing shear chart, preserves root.
        self.assertTrue(classify_pair(CombinedWorld(1,0,1,1),
                                      CombinedWorld(1,2,1,1)).root_preserving)

    def test_native_visible_mismatch_rules_out_forced_root_return(self):
        probe=self.entry.Window48Evidence(1,2,b"native-root")
        self.assertEqual(len(probe.candidates),48)
        probe.record("A",b"step1")
        probe.record("A",b"step2")
        report=probe.record("A",b"not-root")
        self.assertEqual(report.status,"WALL_NO_DIRECT_ROOTED_WINDOW48_MATCH")
        self.assertEqual(len(report.candidate_indices),0)

    def test_visible_equality_does_not_imply_hidden_state_or_full_conjugacy(self):
        probe=self.entry.Window48Evidence(1,2,b"native-root")
        result=probe.record("B",b"native-root")
        self.assertEqual(len(result.candidate_indices),48)
        self.assertEqual(result.status,"CONDITIONAL_ROOTED_WINDOW48")
        self.assertEqual(len(result.rooted_class_keys),16)
        self.assertEqual(result.visible_collisions,1)

    def test_probe_action_selection_uses_source_collisions(self):
        probe=self.entry.Window48Evidence(1,2,b"native-root")
        self.assertEqual(set(probe.rank_letters()),{"A","B"})
        probe.record("A",b"step1")
        self.assertEqual(set(probe.rank_letters()),{"A","B"})

    def test_real_native_colors_not_reduced_to_f3(self):
        g=np.zeros((64,64),dtype=np.uint8)
        a=self.entry.observation_key(SimpleNamespace(frame=[g]))
        g[0,0]=15
        b=self.entry.observation_key(SimpleNamespace(frame=[g]))
        self.assertNotEqual(a,b)
        g[0,0]=3
        self.assertNotEqual(b,self.entry.observation_key(SimpleNamespace(frame=[g])))

    def test_agent_uses_48_not_old_nine(self):
        agent=self.entry.MyAgent()
        g=np.zeros((64,64),dtype=np.uint8)
        frame=SimpleNamespace(frame=[g],
                              available_actions=[self.Action.ACTION1,
                                                 self.Action.ACTION2],
                              levels_completed=0,state=self.State.NOT_FINISHED)
        self.assertFalse(agent.is_done([],frame))
        action=agent.choose_action([],frame)
        self.assertIn(action,(self.Action.ACTION1,self.Action.ACTION2))
        self.assertEqual(action.reasoning["48_source_laws_remaining"],48)
        self.assertTrue(action.reasoning["rooted_conjugacy_not_full_state_claim"])

    def test_click_only_native_game_is_not_assigned_fictitious_generators(self):
        agent=self.entry.MyAgent()
        frame=SimpleNamespace(frame=[np.zeros((64,64),dtype=np.uint8)],
                              available_actions=[self.Action.ACTION6],
                              levels_completed=0,state=self.State.NOT_FINISHED)
        self.assertTrue(agent.is_done([],frame))
        self.assertIsNone(agent.f3_48)

    def test_illegal_source_parameters_rejected(self):
        with self.assertRaises(ValueError):
            self.entry.window48_q(0,0,(4,0,0,0))
        with self.assertRaises(ValueError):
            self.entry.window48_step((0,0,3),"A",self.entry.WINDOW48[0])


if __name__=="__main__":
    unittest.main()
