"""Exhaustive boundary of compatible invertible affine world-construction maps."""
import unittest
from itertools import product

from work.arc_like_maze.affine_scan import compose, scan_affine
from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.operators import SCALE, SHEAR, SWAP, TRANSLATE


class AffineConstructionScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = scan_affine()

    def test_exhausts_all_729_maps_with_432_bijections(self):
        r = self.result
        self.assertEqual((r.all_affine_maps, r.bijections), (729, 432))

    def test_exact_compatible_bijections_and_induced_quotient_permutations(self):
        r = self.result
        self.assertEqual(r.status, "CLOSED_FOR_INVERTIBLE_AFFINE_AB_QUOTIENT")
        self.assertEqual((r.quotient_classes, r.compatible_bijections,
                          r.translated_compatible_bijections,
                          r.induced_quotient_permutations), (5, 48, 0, 24))

    def test_non_bijective_maps_not_promoted_to_group(self):
        r = self.result
        self.assertEqual(r.quotient_compatible_maps, 89)
        self.assertEqual(r.quotient_compatible_maps - r.compatible_bijections, 41)

    def test_all_accepted_maps_fix_origin_and_preserve_quotient(self):
        self.assertTrue(all(op.offset == (0, 0) for op in self.result.accepted))
        self.assertTrue(all(set(p) == set(range(5)) and p[0] == 0
                            for p in self.result.quotient_actions))

    def test_all_24_actions_cover_permutations_of_four_nonzero_classes(self):
        permutations = {p[1:] for p in self.result.quotient_actions}
        self.assertEqual(len(permutations), 24)
        self.assertEqual(permutations,
                         set(__import__('itertools').permutations(range(1, 5))))

    def test_all_48_accepted_maps_are_closed_under_pairwise_composition(self):
        keys = {(op.matrix, op.offset) for op in self.result.accepted}
        for a in self.result.accepted:
            for b in self.result.accepted:
                op = compose(a, b)
                self.assertIn((op.matrix, op.offset), keys)

    def test_example_generators_are_accepted(self):
        keys = {(op.matrix, op.offset) for op in self.result.accepted}
        for op in (SCALE, SHEAR, SWAP):
            self.assertIn((op.matrix, op.offset), keys)
        self.assertNotIn((TRANSLATE.matrix, TRANSLATE.offset), keys)

    def test_affine_composition_matches_sequential_construction(self):
        for a, b in product((SCALE, SHEAR, SWAP, TRANSLATE), repeat=2):
            for w in inverse_candidates():
                self.assertEqual(compose(a, b)(w), a(b(w)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
