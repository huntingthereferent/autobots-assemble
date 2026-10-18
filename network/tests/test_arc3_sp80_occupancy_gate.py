"""Frozen SP80 target pre-color filter: test negative controls and nonleakage."""
from __future__ import annotations
import unittest
import numpy as np

from work.arc3.native_sp80_occupancy_gate import gate_using_target_pre_state


class NativeOccupancyGateTests(unittest.TestCase):
    def test_retains_only_actual_pre_action_color_matches(self):
        root=np.zeros((64,64),dtype=np.uint8)
        root[3,1]=14
        root[4,2]=14
        predicted={
            (1,3):(14,0),       # admissible
            (2,4):(14,0),       # admissible
            (3,5):(14,0),       # already zero; never a 14->0 change
            (4,6):(9,12),       # wrong native pre-color
        }
        selected,rejected=gate_using_target_pre_state(predicted,root)
        self.assertEqual(selected,{(1,3):(14,0),(2,4):(14,0)})
        self.assertEqual(len(rejected),2)
        self.assertEqual(
            {x["reason"] for x in rejected},
            {"ALREADY_AT_EXPECTED_NEW_COLOR","DIFFERENT_NATIVE_PRE_COLOR"}
        )

    def test_already_final_native_color_cannot_be_predicted_to_change(self):
        root=np.full((64,64),12,dtype=np.uint8)
        predictions={(63,20):(14,12)}
        selected,rejected=gate_using_target_pre_state(predictions,root)
        self.assertEqual(selected,{})
        self.assertEqual(rejected[0]["actual_pre_action_color"],12)

    def test_no_operation_native_colors_not_admitted_as_changes(self):
        root=np.full((64,64),14,dtype=np.uint8)
        selected,rejected=gate_using_target_pre_state(
            {(5,5):(14,14)},root)
        self.assertEqual(selected,{})
        self.assertEqual(rejected[0]["reason"],"ALREADY_AT_EXPECTED_NEW_COLOR")

    def test_current_native_color_not_future_frame_controls_gating(self):
        root=np.zeros((64,64),dtype=np.uint8)
        root[0,0]=14
        selected,_=gate_using_target_pre_state({(0,0):(14,0)},root)
        self.assertEqual(selected,{(0,0):(14,0)})
        # The gate can only check PRE-color. It cannot decide whether the
        # real game changes the pixel to zero; that requires a NEW trial.


if __name__=="__main__":
    unittest.main()
