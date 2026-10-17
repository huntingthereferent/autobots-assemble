"""The public first screen must visibly reflect the original research."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from views.motion.research_field import snapshot, render, generate
from systems.workspace.research_observatory import ROOT


class ResearchMovementFieldTests(unittest.TestCase):
    def test_source_bound_large_new_frontpage(self):
        data=snapshot()
        self.assertEqual(data["arc"]["state"],"MOVE_WITH_WALL")
        self.assertGreaterEqual(len(data["experiments"]),6)
        self.assertGreaterEqual(len(data["cp"]),4)
        self.assertEqual(data["native"]["routes"][0]["states"][-1],data["native"]["target"])
        self.assertIn("W13 PASS",data["w13"]["verdict"])
        svg=render(data)
        ET.fromstring(svg)
        self.assertIn("THE WORK IS MOVING",svg)
        self.assertIn("ARC / CAUSAL REASONING",svg)
        self.assertIn("CHECKPOINT CONTINUATION",svg)
        self.assertIn("GAME WORLD / W13",svg)
        self.assertIn("FINITE MATHEMATICS",svg)
        self.assertIn("prefers-reduced-motion",svg)
        self.assertIn("stroke-dasharray",svg)
        self.assertNotIn("10 DOMAINS",svg)
        self.assertNotIn("RECORDED JOBS",svg)
        self.assertNotIn("15 recorded",svg)
        self.assertNotIn("JAMES MUNEOKA",svg)
        self.assertNotIn("<script",svg)

    def test_arc_and_w13_witness_cannot_be_silently_upgraded(self):
        data=snapshot()
        data["arc"]["state"]="UNKNOWN"
        with self.assertRaises(ValueError):
            render(data)
        data=snapshot()
        data["w13"]["verdict"]="W13 NOT CHECKED"
        with self.assertRaises(ValueError):
            render(data)

    def test_cannot_render_mathematical_paths_without_witness(self):
        data=snapshot()
        data["native"]["routes"][0]["states"][-1]=[0,0,0]
        with self.assertRaises(ValueError):
            render(data)

    def test_generation_does_not_change_original_evidence(self):
        src=[ROOT/"research/dives/ARC3-TRACE-001/dive.json",
             ROOT/"work/arc_like_maze/math.py",
             ROOT/"work/arc_like_maze/chatbot/checkpoints/CP-0030.json"]
        before=[s.read_bytes() for s in src]
        with TemporaryDirectory() as d:
            path=Path(d)/"research-movement-field.svg"
            svg=generate(path)
            self.assertEqual(path.read_text(),svg+"\n")
            ET.parse(path)
        self.assertEqual(before,[s.read_bytes() for s in src])


if __name__=="__main__":
    unittest.main()
