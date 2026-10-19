"""WORLD built-space topology tests. No fabricated real-world measurements."""
import json
from pathlib import Path
from copy import deepcopy
import unittest
from systems.workspace.world_physical_construction import (
    ORIGIN,SOURCE,QUERY,GATE,GOAL,footprint,verify_geometry,
    route,witness,neighbors)

FIXTURE=Path(__file__).resolve().parent/"fixtures/world_nih_phase1_phase2_blueprint_v1.json"
def physical():
    return footprint(json.loads(FIXTURE.read_text()))

class PhysicalWorldFitTests(unittest.TestCase):
    def test_01_all_six_blueprint_lanes_and_two_stages_physically_constructed(self):
        m=physical()
        self.assertEqual(m["dimensions"],
          {"width":24,"height":6,"lane_width":4,"stage_height":3,"area_cells":144})
        self.assertEqual(len(m["lanes"]),6)
        self.assertEqual(len(m["stages"]),2)
        self.assertEqual(len(m["solid_blocks"]),5)
        self.assertEqual({b["kind"] for b in m["solid_blocks"]},
                         {"wall","guide","funnel","diverter","spiral"})
        self.assertTrue(witness(m)["gate_required"])
        self.assertFalse(m["physical_scale_authenticated"])
    def test_02_gate_cannot_be_bypassed_and_both_phases_reachable(self):
        m=physical()
        self.assertIsNone(route(m,ORIGIN,[QUERY["x"],QUERY["y"]],False))
        self.assertIsNotNone(route(m,ORIGIN,[SOURCE["x"],SOURCE["y"]],False))
        self.assertIsNotNone(route(m,[SOURCE["x"],SOURCE["y"]],GATE["from"],False))
        self.assertIsNotNone(route(m,GATE["to"],[QUERY["x"],QUERY["y"]],True))
        self.assertIsNotNone(route(m,[QUERY["x"],QUERY["y"]],GOAL,True))
    def test_03_blocks_have_collision_and_no_station_overlap(self):
        m=physical()
        walls={(b["x"],b["y"]) for b in m["solid_blocks"]}
        for pos in ([0,1],[2,1],[12,2],[12,3],[22,4],[23,4]):
            self.assertNotIn(tuple(pos),walls)
        self.assertNotIn((4,1),list(neighbors(m,(3,1),False)))
        self.assertNotIn((12,3),list(neighbors(m,(12,2),False)))
        self.assertIn((12,3),list(neighbors(m,(12,2),True)))
    def test_04_existing_small_w13_rooms_are_not_resized(self):
        m=physical()
        self.assertEqual(m["lanes"][0]["x_end_exclusive"],4)
        self.assertEqual(m["stages"][1]["y_start"],3)
        from systems.workspace.world_temporal_blueprint import ROOMS
        b=json.loads(FIXTURE.read_text())
        self.assertEqual(b["base_world"]["rooms"],ROOMS)
        self.assertEqual([r["spec"]["width"] for r in ROOMS],[4,3])
        self.assertEqual(m["dimensions"]["area_cells"],144)
    def test_05_metric_scale_and_block_tampering_fail_closed(self):
        m=physical()
        for change in (
            lambda x:x["dimensions"].update(width=12),
            lambda x:x.update(physical_scale_authenticated=True),
            lambda x:x["solid_blocks"][0].update(x=22),
            lambda x:x["gate"].update(requires="unconditional"),
            lambda x:x["lanes"][0].update(id="made-up"),
        ):
            fake=deepcopy(m);change(fake)
            with self.assertRaises(ValueError):verify_geometry(fake)
if __name__=="__main__":
    unittest.main()
