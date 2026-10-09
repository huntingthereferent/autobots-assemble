"""Root-aware full-state arrow contract for 48 constructed F3 window worlds."""
import unittest
from dataclasses import replace
from itertools import product

from work.arc_like_maze.window_combined import CombinedWorld, classify_pair, family
from work.arc_like_maze.window_marked_arrows import (
    ORIGIN, PointedWorld, StateArrow, MarkedArrow, MarkChange,
    canonical_arrow, transport_target_mark, certify_marked_operator,
)


class MarkedStateArrowTests(unittest.TestCase):
    def test_certificate_counts_and_no_silent_full_state_promotion(self):
        c = certify_marked_operator()
        self.assertEqual(c.status, "CLOSED_POINTED_ARROW_CONTRACT_IN_DECLARED_FAMILY")
        self.assertEqual((c.total_pairs, c.obstructed, c.canonical_marked_arrows,
                          c.nonrooted_state_arrows), (2304, 2124, 144, 36))
        self.assertEqual((c.guarded_nonrooted_arrows, c.explicit_remarkings,
                          c.marked_inverse_checks, c.marked_composition_checks),
                         (36, 36, 180, 180))

    def test_36_canonical_nonroot_maps_refuse_marked_promotion(self):
        seen=0
        for k, c, d, forward in product((0,3), range(3), range(3), (True,False)):
            a = CombinedWorld(k,c,1,0 if forward else 1)
            b = CombinedWorld(k,d,1,1 if forward else 0)
            arrow = canonical_arrow(a,b)
            self.assertEqual(arrow.mark_status, "MARK_MISMATCH")
            self.assertNotEqual(arrow.image_of_mark, ORIGIN)
            self.assertEqual(arrow.target.mark, ORIGIN)
            with self.assertRaises(ValueError):
                arrow.require_marked()
            seen += 1
        self.assertEqual(seen, 36)

    def test_explicit_repoint_preserves_previous_marks_and_word_counterexample(self):
        count=0
        for k,c,d in product((0,3),range(3),range(3)):
            source=CombinedWorld(k,c,1,0)
            target=CombinedWorld(k,d,1,1)
            arrow=canonical_arrow(source,target)
            move=transport_target_mark(arrow)
            self.assertEqual(move.original.target.mark, ORIGIN)
            self.assertEqual(move.transported_target.world,target)
            self.assertEqual(move.transported_target.mark,(0,2,d))
            self.assertEqual(move.resulting_arrow.source.mark, ORIGIN)
            self.assertEqual(move.resulting_arrow.target.mark,(0,2,d))
            self.assertEqual(move.resulting_arrow.state_arrow.factors,arrow.factors)
            word1,word2,same,first,second=move.original_root_conflict
            self.assertEqual(source.apply(ORIGIN,word1),same)
            self.assertEqual(source.apply(ORIGIN,word2),same)
            self.assertEqual(target.apply(ORIGIN,word1),first)
            self.assertEqual(target.apply(ORIGIN,word2),second)
            self.assertNotEqual(first,second)
            count +=1
        self.assertEqual(count,18)

    def test_opposite_direction_mark_is_also_transported_exactly(self):
        for k,c,d in product((0,3),range(3),range(3)):
            arrow=canonical_arrow(CombinedWorld(k,c,1,1),CombinedWorld(k,d,1,0))
            moved=transport_target_mark(arrow)
            self.assertEqual(moved.transported_target.mark,(0,1,(1+d)%3))

    def test_both_actions_commute_after_repointing_all_prefixes(self):
        for k,c,d in product((0,3),range(3),range(3)):
            arrow=canonical_arrow(CombinedWorld(k,c,1,0),CombinedWorld(k,d,1,1))
            moved=transport_target_mark(arrow).resulting_arrow
            for depth in range(3,7):
                self.assertEqual(moved.map_state(moved.source.at_depth(depth)),
                                 moved.target.at_depth(depth))
                for state in product(range(3),repeat=depth):
                    image=moved.map_state(state)
                    for label in 'AB':
                        self.assertEqual(moved.map_state(moved.source.world.step(state,label)),
                                         moved.target.world.step(image,label))

    def test_inverse_and_composition_retain_the_literal_witness_path(self):
        for k in (0,3):
            arrow=canonical_arrow(CombinedWorld(k,0,1,0),CombinedWorld(k,2,1,1))
            move=transport_target_mark(arrow)
            marked=move.resulting_arrow
            inverse=marked.inverse()
            self.assertEqual(inverse.source,marked.target)
            self.assertEqual(inverse.target,marked.source)
            composed=marked.compose(inverse)
            self.assertEqual(len(composed.state_arrow.factors),2)
            self.assertEqual(composed.source,composed.target)
            for depth in range(3,7):
                for state in product(range(3),repeat=depth):
                    self.assertEqual(composed.map_state(state),state)
                    self.assertEqual(inverse.map_state(marked.map_state(state)),state)

    def test_marked_charts_compose_and_keep_separate_factor_provenance(self):
        a=CombinedWorld(2,0,1,0)
        b=CombinedWorld(2,1,1,0)
        c=CombinedWorld(2,2,1,0)
        ab=canonical_arrow(a,b).require_marked()
        bc=canonical_arrow(b,c).require_marked()
        result=ab.compose(bc)
        self.assertEqual(result.source,PointedWorld(a))
        self.assertEqual(result.target,PointedWorld(c))
        self.assertEqual(len(result.state_arrow.factors),2)
        direct=canonical_arrow(a,c).require_marked()
        for state in product(range(3),repeat=6):
            self.assertEqual(result.map_state(state),direct.map_state(state))

    def test_state_composition_requires_exact_middle_mark(self):
        a=CombinedWorld(0,0,1,0)
        b=CombinedWorld(0,0,1,1)
        original=canonical_arrow(a,b)
        changed=transport_target_mark(original)
        naive_after=canonical_arrow(b,a)
        with self.assertRaises(ValueError):
            original.compose(changed.resulting_arrow.state_arrow)
        with self.assertRaises(ValueError):
            changed.resulting_arrow.state_arrow.compose(naive_after)
        proper_inverse=changed.resulting_arrow.inverse()
        self.assertEqual(changed.resulting_arrow.compose(proper_inverse).source,
                         PointedWorld(a))

    def test_chain_that_cancels_root_movement_does_not_erase_factors(self):
        a=CombinedWorld(3,0,1,0)
        b=CombinedWorld(3,0,1,1)
        forward=canonical_arrow(a,b)
        backward=canonical_arrow(b,a)
        combined=forward.compose(backward)
        self.assertEqual(combined.mark_status,'MARK_PRESERVED')
        self.assertEqual(len(combined.factors),2)
        self.assertEqual(combined.require_marked().source,PointedWorld(a))
        self.assertEqual(combined.require_marked().target,PointedWorld(a))

    def test_rooted_and_full_state_pair_classes_remain_distinct(self):
        recorded={'root':0,'nonroot':0,'obstructed':0}
        for source in family():
            for target in family():
                if classify_pair(source,target).kind is None:
                    recorded['obstructed']+=1
                else:
                    arrow=canonical_arrow(source,target)
                    recorded['root' if arrow.mark_status=='MARK_PRESERVED'
                             else 'nonroot'] += 1
        self.assertEqual(recorded,{'root':144,'nonroot':36,'obstructed':2124})

    def test_repointing_is_not_a_noop_and_rejects_noncanonical_inputs(self):
        a=CombinedWorld(3,0,1,0)
        b=CombinedWorld(3,1,1,0)
        same=canonical_arrow(a,b)
        with self.assertRaises(ValueError):
            transport_target_mark(same)
        nonroot=canonical_arrow(a,CombinedWorld(3,1,1,1))
        arbitrary=StateArrow(PointedWorld(a,(1,0,0)),nonroot.target,nonroot.factors)
        with self.assertRaises(ValueError):
            transport_target_mark(arbitrary)

    def test_obstructed_pairs_and_uncomposable_witnesses_rejected(self):
        a=CombinedWorld(0,0,0,0)
        b=CombinedWorld(1,0,0,0)
        with self.assertRaises(ValueError):
            canonical_arrow(a,b)
        c=CombinedWorld(0,1,0,0)
        with self.assertRaises(ValueError):
            StateArrow(PointedWorld(a),PointedWorld(c),())
        with self.assertRaises(ValueError):
            StateArrow(PointedWorld(a),PointedWorld(a),(classify_pair(a,c),))
        with self.assertRaises(ValueError):
            StateArrow(PointedWorld(a),PointedWorld(a),
                       (classify_pair(a,c),classify_pair(a,c)))

    def test_marks_are_three_digit_finite_support_and_depth_safe(self):
        world=CombinedWorld(0,0,1,0)
        pointed=PointedWorld(world,(0,2,1))
        self.assertEqual(pointed.at_depth(3),(0,2,1))
        self.assertEqual(pointed.at_depth(6),(0,2,1,0,0,0))
        self.assertFalse(pointed.canonical)
        with self.assertRaises(ValueError):
            pointed.at_depth(2)
        for bad in ((0,0), (0,0,0,1), (0,0,3), (0,True,0), [0,0,0]):
            with self.assertRaises(ValueError):
                PointedWorld(world,bad)

    def test_malformed_remarking_record_cannot_forge_rooted_equivalence(self):
        arrow=canonical_arrow(CombinedWorld(0,0,1,0),CombinedWorld(0,0,1,1))
        correct=transport_target_mark(arrow)
        with self.assertRaises(ValueError):
            replace(correct, transported_target=PointedWorld(arrow.target.world))
        bad=('','',(0,0,0),(0,0,0),(0,0,0))
        with self.assertRaises(ValueError):
            replace(correct, original_root_conflict=bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
