"""Rooted discrimination tests against original 48 source worlds."""
from __future__ import annotations

from itertools import combinations
import unittest

from work.arc_like_maze.window_combined import (
    CombinedWorld, classify_pair, family
)
from work.arc3.window48_rooted_questions import (
    ORIGIN, equality, plan, representatives, root_class_key
)


class Window48RootedPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=plan()

    def test_original_48_16_14_all_preserved(self):
        self.assertEqual(self.result["worlds"],48)
        self.assertEqual(self.result["origin_preserving_classes"],16)
        self.assertEqual(self.result["full_state_classes"],14)
        self.assertEqual(len(self.result["source_class_rooted_signatures"]),16)

    def test_source_rooted_questions_distinguish_every_class_pair(self):
        signatures=[
            tuple(row["equality_signature"])
            for row in self.result["source_class_rooted_signatures"]
        ]
        self.assertEqual(len(signatures),len(set(signatures)))
        self.assertEqual(len(list(combinations(signatures,2))),120)

    def test_every_question_is_actual_source_origin_equality(self):
        q=[tuple(x["words"]) for x in self.result["questions"]]
        self.assertGreater(len(q),0)
        sources=family()
        for world in sources:
            key=list(root_class_key(world))
            row=next(x for x in self.result["source_class_rooted_signatures"]
                     if x["key"]==key)
            self.assertEqual(tuple(equality(world,question) for question in q),
                             tuple(row["equality_signature"]))

    def test_nonrooted_full_conjugacies_are_root_distinct(self):
        self.assertEqual(len(self.result[
            "origin_moving_full_conjugacy_not_root_equivalent_examples"]),2)
        for k in (0,3):
            left=CombinedWorld(k,0,1,0)
            right=CombinedWorld(k,0,1,1)
            relation=classify_pair(left,right)
            self.assertFalse(relation.root_preserving)
            self.assertEqual(relation.kind,"FIBER_SHIFT")
            selected=[tuple(q["words"]) for q in self.result["questions"]]
            self.assertTrue(any(equality(left,q)!=equality(right,q)
                                for q in selected))

    def test_all_three_shear_charts_share_rooted_class_signature(self):
        questions=[tuple(q["words"]) for q in self.result["questions"]]
        for k in range(4):
            for e in (0,1):
                for t in (0,1):
                    base=CombinedWorld(k,0,e,t)
                    signature=tuple(equality(base,q) for q in questions)
                    for c in (1,2):
                        shifted=CombinedWorld(k,c,e,t)
                        self.assertEqual(
                            tuple(equality(shifted,q) for q in questions),
                            signature)


if __name__=="__main__":
    unittest.main()
