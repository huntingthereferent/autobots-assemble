"""Finite ARC source equivalence must be falsifiable and scoped."""
import unittest
import numpy as np

from work.arc3.arc4_finite_observation_quotient import (
    projected, witness_difference, word, finite_field_scope_check, WALL,
)

class OriginalSDKFiniteQuotientTests(unittest.TestCase):
    def test_same_projection_not_same_native_full_frame(self):
        a=np.zeros((3,64,64),dtype=np.uint8)
        b=a.copy()
        b[:,63,10]=14
        self.assertIsNone(witness_difference(a,b))
        self.assertFalse(np.array_equal(a,b))
        self.assertTrue(np.array_equal(projected(a),projected(b)))

    def test_different_interior_gives_actual_counterexample(self):
        a=np.zeros((2,64,64),dtype=np.uint8)
        b=a.copy()
        b[1,21,35]=9
        self.assertEqual(witness_difference(a,b),{
            "kind":"OBSERVATIONAL_RIGHT_CONGRUENCE_COUNTEREXAMPLE",
            "first_returned_frame":1,"original_y":21,"original_x":35,
            "left_source_pixel":0,"right_source_pixel":9})

    def test_animation_length_is_not_assumed_equal(self):
        a=np.zeros((1,64,64),dtype=np.uint8)
        b=np.zeros((2,64,64),dtype=np.uint8)
        self.assertEqual(witness_difference(a,b)["kind"],"FRAME_STACK_LENGTH_MISMATCH")

    def test_genuine_native_actions_are_not_mathematical_AB(self):
        self.assertEqual(word("6@46,33 3 5"),((6,[46,33]),(3,None),(5,None)))
        with self.assertRaisesRegex(ValueError,"non-native SDK action"):
            word("A B")
        self.assertEqual(finite_field_scope_check()["sdk_to_F3_operator_correspondence"],WALL)

if __name__=="__main__":
    unittest.main()
