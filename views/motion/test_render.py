"""Test motion from actual finite math and bounded source records."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from work.arc_like_maze.math import World
from views.motion.render import (finite_observation, read_world_snapshot, render_finite, render_world, generate)

class MotionSourceTests(unittest.TestCase):
    def test_native_math_generated_endpoints(self):
        world=World(3,(0,1,2))
        result=finite_observation()
        self.assertEqual(result["AB"],world.apply("AB"))
        self.assertEqual(result["BA"],world.apply("BA"))
        self.assertNotEqual(result["AB"],result["BA"])
        self.assertEqual(result["A3"],world.origin)
        self.assertEqual(result["reachable_states"],len(world.reachable()))
        self.assertIn("AB != BA",render_finite(result))

    def test_source_match_or_refusal_never_joins_usgs(self):
        path=Path(__file__).resolve().parents[1]/"world-continuity/latest.json"
        snapshot=read_world_snapshot(path)
        svg=render_world(snapshot)
        self.assertIn("USGS unjoined",svg)
        self.assertIn(snapshot["checked_at"][:19].replace("T"," "),svg)
        self.assertEqual("M503 181H562" in svg,
                         snapshot["relationship"]["matched_by_declared_url_rule"])
        copy=json.loads(json.dumps(snapshot))
        copy["relationship"]["matched_by_declared_url_rule"]=False
        self.assertNotIn("M503 181H562",render_world(copy))

    def test_reject_unknown_world_schema(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps({"schema":"wrong","checked_at":"now",
                                     "relationship":{},"sources":{},"unjoined":[]}))
            with self.assertRaises(ValueError):read_world_snapshot(p)

    def test_three_animated_xml_outputs_are_self_contained(self):
        with TemporaryDirectory() as d:
            out=Path(d)/"svg"
            generate(out)
            self.assertEqual({x.name for x in out.iterdir()},
              {"finite-motion.svg","world-motion.svg"})
            for file in out.glob("*.svg"):
                content=file.read_text()
                ET.fromstring(content)
                self.assertIn("prefers-reduced-motion",content)
                self.assertIn("@keyframes",content)
                self.assertNotIn("<script",content)

    def test_does_not_mutate_native_sources(self):
        root=Path(__file__).resolve().parents[2]
        tracked=[root/"views/world-continuity/latest.json",
                 root/"work/arc_like_maze/math.py"]
        before=[p.read_bytes() for p in tracked]
        with TemporaryDirectory() as d:generate(Path(d))
        self.assertEqual(before,[p.read_bytes() for p in tracked])

if __name__=="__main__":unittest.main()
