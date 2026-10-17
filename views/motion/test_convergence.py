"""Do not animate invented A/B convergence or change the original math."""
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from work.arc_like_maze.math import World
from views.motion.convergence import discover_convergence, animate


class NativeConvergenceTests(unittest.TestCase):
    def test_actual_independently_checked_paths_converge(self):
        x=discover_convergence()
        self.assertEqual(x["schema"],"finite-ab-convergence/v1")
        self.assertNotEqual(x["left_word"],x["right_word"])
        self.assertNotEqual(x["left_word"][0],x["right_word"][0])
        world=World(3,(0,1,2))
        self.assertEqual(list(world.apply(x["left_word"])),x["target"])
        self.assertEqual(list(world.apply(x["right_word"])),x["target"])
        self.assertGreater(x["states_explored"],0)

    def test_unresolved_budget_never_invents_witness(self):
        x=discover_convergence(max_states=2)
        self.assertEqual(x["status"],"OPEN")
        with self.assertRaises(ValueError):
            animate(x)

    def test_source_mismatch_fails_closed(self):
        with patch("views.motion.convergence._independent_step",return_value=(2,2,2)):
            with self.assertRaises(ValueError):
                discover_convergence()

    def test_self_contained_motion_reduced_motion(self):
        svg=animate(discover_convergence())
        ET.fromstring(svg)
        self.assertIn("@keyframes",svg)
        self.assertIn("prefers-reduced-motion",svg)
        self.assertIn("No path was chosen",svg)
        self.assertNotIn("<script",svg)


if __name__=="__main__":
    unittest.main()
