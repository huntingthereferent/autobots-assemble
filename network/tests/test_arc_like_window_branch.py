"""An independent q(0,0) pulse defeats the old B-fixed-only classification."""
import unittest
from itertools import product

from work.arc_like_maze.window_branch import (
    BranchedWindow, branch_rule, family, classify_pair, certify_branch,
    fixed_word_formula,
)
from work.arc_like_maze.window_family import ClassifiedWindow
from work.arc_like_maze.nondiagonal_transport import shear


class WindowBranchTests(unittest.TestCase):

    def test_24_concrete_laws_and_eight_proved_full_state_classes(self):
        report = certify_branch()
        self.assertEqual(report.status, "CLOSED_DECLARED_SHEARS_EIGHT_FULL_STATE_CLASSES")
        self.assertEqual((report.constructed_laws,report.full_state_classes), (24,8))
        self.assertEqual(report.class_sizes, (3,)*8)
        self.assertEqual((report.aligned_ordered_pairs,
                          report.B_obstructed_ordered_pairs,
                          report.BBB_obstructed_ordered_pairs), (72,432,72))
        self.assertTrue(report.all_concrete_laws_distinct)

    def test_old_support_family_embeds_as_zero_pulse_with_exact_rules(self):
        for support, coefficient in product(range(4), range(3)):
            old = ClassifiedWindow(support, coefficient).world()
            new = BranchedWindow(support, coefficient, 0).world()
            self.assertEqual(old, new)
            for depth in (3,4,5):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(old.step(state, action),
                                         new.step(state, action))

    def test_new_pulse_outside_old_row_does_not_change_B_fixed_count(self):
        for support, coefficient in product(range(4),range(3)):
            a=BranchedWindow(support, coefficient, 0)
            b=BranchedWindow(support, coefficient, 1)
            self.assertEqual(a.count_fixed_word("B"), b.count_fixed_word("B"))
            self.assertEqual(a.count_fixed_word("B"), (3-support)*3)
            self.assertNotEqual(a.world().rule(0), b.world().rule(0))
            self.assertEqual((b.world().rule(0)[0]-a.world().rule(0)[0])%3, 1)
            for index in range(1,9):
                self.assertEqual(a.world().rule(0)[index], b.world().rule(0)[index])

    def test_BBB_finite_word_separates_same_B_count(self):
        for support, coefficient in product(range(4),range(3)):
            a=BranchedWindow(support, coefficient, 0)
            b=BranchedWindow(support, coefficient, 1)
            self.assertEqual(a.count_fixed_word("BBB"), 27)
            self.assertEqual(b.count_fixed_word("BBB"), 18)
            relation=classify_pair(a,b)
            self.assertEqual(relation.obstruction_word,"BBB")
            self.assertEqual(relation.first_obstruction_depth,3)
            self.assertEqual((relation.source_fixed,relation.target_fixed),(27,18))
            with self.assertRaises(ValueError): relation.map_state((0,0,0))

    def test_origin_BBB_return_is_false_just_after_independent_edit(self):
        before=BranchedWindow(0,0,0)
        after=BranchedWindow(0,0,1)
        origin=(0,0,0)
        self.assertEqual(before.apply(origin,"BBB"), origin)
        self.assertEqual(after.apply(origin,"BBB"), (0,0,1))
        self.assertNotEqual(before.step(origin,"B"), after.step(origin,"B"))
        # But a different state hides the difference for one B turn:
        hidden=(0,1,0)
        self.assertEqual(before.step(hidden,"B"), after.step(hidden,"B"))
        self.assertNotEqual(before.apply(hidden,"BBB"),
                            after.apply(hidden,"BBB"))

    def test_B_and_BBB_closed_form_on_full_states_depths_three_through_six(self):
        for world in family():
            for depth in range(3,7):
                for word in ("B","BBB"):
                    self.assertEqual(
                        world.count_fixed_word(word, depth),
                        fixed_word_formula(word,depth,world.support,world.pulse))

    def test_all_576_ordered_pairs_have_exact_map_or_word_obstruction(self):
        worlds=family()
        self.assertEqual(len(worlds),24)
        seen={"map":0,"B":0,"BBB":0}
        for source in worlds:
            for target in worlds:
                relation=classify_pair(source,target)
                if relation.shear_witness is not None:
                    seen["map"]+=1
                    for depth in range(3,6):
                        for state in product(range(3),repeat=depth):
                            mapped=relation.map_state(state)
                            for action in "AB":
                                self.assertEqual(
                                    relation.map_state(source.step(state,action)),
                                    target.step(mapped,action))
                else:
                    seen[relation.obstruction_word]+=1
                    self.assertNotEqual(relation.source_fixed, relation.target_fixed)
                    self.assertEqual(relation.first_obstruction_depth, 3)
        self.assertEqual(seen,{"map":72,"B":432,"BBB":72})

    def test_non_diagonal_maps_are_composable_in_each_class(self):
        for k,e in product(range(4),range(2)):
            a=BranchedWindow(k,0,e)
            b=BranchedWindow(k,1,e)
            c=BranchedWindow(k,2,e)
            for state in product(range(3),repeat=5):
                ab=classify_pair(a,b).map_state
                bc=classify_pair(b,c).map_state
                ac=classify_pair(a,c).map_state
                self.assertEqual(bc(ab(state)),ac(state))
                self.assertEqual(shear(shear(state,1),1),shear(state,2))

    def test_triangular_inverses_on_all_states(self):
        for world in family():
            for depth in range(3,7):
                for state in product(range(3),repeat=depth):
                    for action in "AB":
                        y=world.step(state,action)
                        self.assertEqual(world.inverse(y,action),state)
                        self.assertEqual(world.step(world.inverse(state,action),action),
                                         state)

    def test_projection_works_at_every_checked_depth(self):
        for world in family():
            for depth in range(4,8):
                for state in product(range(3),repeat=depth):
                    for action in "AB":
                        self.assertEqual(world.step(state,action)[:-1],
                                         world.step(state[:-1],action))

    def test_three_directions_have_separate_walls_and_commuting_squares(self):
        result=certify_branch()
        self.assertEqual((result.shear_cycle_order,result.support_walls,
                          result.pulse_walls),(3,6,12))
        for world in family():
            self.assertEqual(
                world.shear_next().shear_next().shear_next(),world)
            s=world.support_next()
            p=world.pulse_next()
            if s is not None:
                self.assertEqual(world.shear_next().support_next(),s.shear_next())
            else:
                self.assertEqual(world.support,3)
            if p is not None:
                self.assertEqual(world.shear_next().pulse_next(),p.shear_next())
            else:
                self.assertEqual(world.pulse,1)
            if s is not None and p is not None:
                self.assertEqual(s.pulse_next(),p.support_next())

    def test_fixed_word_formulas_are_not_universal_word_counters(self):
        with self.assertRaises(ValueError):
            fixed_word_formula("AB",3,0,0)
        with self.assertRaises(ValueError):
            fixed_word_formula("BBB",2,0,0)
        with self.assertRaises(ValueError):
            fixed_word_formula("BBB",3,4,0)
        with self.assertRaises(ValueError):
            fixed_word_formula("BBB",3,1,2)

    def test_reject_non_F3_parameters_and_unknown_action_words(self):
        for k,c,e in ((-1,0,0),(4,0,0),(0,3,0),(0,0,2),
                      (False,0,0),(0,True,1),(0,0,False)):
            with self.assertRaises(ValueError): BranchedWindow(k,c,e)
        with self.assertRaises(ValueError):
            BranchedWindow(0,0,0).apply((0,0,0),"C")
        with self.assertRaises(ValueError):
            BranchedWindow(0,0,1).count_fixed_word("BBB",2)

if __name__=="__main__":
    unittest.main(verbosity=2)
