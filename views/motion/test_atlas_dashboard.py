"""Source-native trace hero and original workstation research projection."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import xml.etree.ElementTree as ET

from views.motion.atlas_dashboard import dashboard, generate, native_paths, snapshot
from systems.workspace.research_observatory import ROOT, research_snapshot


class AtlasDashboardTests(unittest.TestCase):
    def test_source_native_paths_and_research_are_presented_without_decoration(self):
        data=snapshot()
        self.assertEqual(data["research"]["schema"],"workstation-research-continuity/v1")
        self.assertGreater(data["research"]["totals"]["structured_records"],0)
        self.assertGreater(data["research"]["totals"]["explicit_wall_entries"],0)
        self.assertEqual(data["native"]["routes"][0]["states"][-1],data["native"]["target"])
        self.assertEqual(data["native"]["routes"][1]["states"][-1],data["native"]["target"])
        image=dashboard(data)
        ET.fromstring(image)
        self.assertIn("HUNTING",image)
        self.assertIn("THE REFERENT",image)
        self.assertIn("ORIGINAL RESEARCH",image)
        self.assertIn("EXPLICIT MOVES",image)
        self.assertIn("RECORDED WALLS",image)
        self.assertNotIn("10 DOMAINS",image)
        self.assertNotIn("NOT JOINED",image)
        self.assertNotIn("CANDIDATE FEEDS",image)
        self.assertNotIn("JAMES",image)
        self.assertNotIn("MUNEOKA",image)
        self.assertNotIn("WORKSTATION 15",image)
        self.assertIn("@keyframes",image)
        self.assertIn("prefers-reduced-motion",image)
        self.assertNotIn("<script",image)

    def test_verification_cannot_be_bypassed_with_unmatched_path(self):
        data=snapshot()
        data["native"]["routes"][0]["states"][-1]=[0,0,0]
        with self.assertRaises(ValueError):
            dashboard(data)
        with patch("views.motion.atlas_dashboard._independent_step",return_value=(2,2,2)):
            with self.assertRaises(ValueError):
                native_paths()

    def test_write_only_generated_svg(self):
        sources=[ROOT/"state/current.json",ROOT/"research/dives/ARC3-TRACE-001/dive.json",
                 ROOT/"work/arc_like_maze/math.py"]
        before=[x.read_bytes() for x in sources]
        with TemporaryDirectory() as d:
            body=generate(Path(d))
            svg=Path(d)/"atlas-dashboard.svg"
            self.assertEqual(svg.read_text(encoding="utf8"),body+"\n")
            ET.parse(svg)
        self.assertEqual(before,[x.read_bytes() for x in sources])


if __name__=="__main__":
    unittest.main()
