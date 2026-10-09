"""Mathematical checks for third independently constructed B coupling."""
import unittest
from collections import Counter
from itertools import product
from math import lcm
from work.arc_like_maze.third_coupling import (
 CouplingTower, RULES, rooted_graph, classify_rooted, construct_family,
 projective_scaling, scale_state, certify_three_couplings, rotation, first_dormant)

class ThirdCouplingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.worlds=construct_family(3)
  cls.groups=classify_rooted(cls.worlds)
  cls.cert=certify_three_couplings()

 def test_partition_729_into_85_classes(self):
  c=self.cert
  self.assertEqual((c.constructed_worlds,c.rooted_classes),(729,85))
  self.assertEqual(c.class_distribution,((4,16),(8,64),(18,4),(81,1)))
  self.assertEqual(c.reachable_distribution,((9,81),(27,72),(81,64),(243,512)))

 def test_depth_extension_does_not_split_classes(self):
  self.assertEqual(self.cert.status,"CLOSED_ROOTED_FAMILY_AT_DEPTH_5_AND_6")
  self.assertTrue(self.cert.stable_next_depth)
  self.assertEqual(self.cert.first_dormant_classes,((0,1),(1,4),(2,16),(3,64)))

 def test_prior_5_and_21_classes_recovered(self):
  self.assertEqual([len(classify_rooted(construct_family(n))) for n in (1,2,3)], [5,21,85])

 def test_full_state_scaling_for_every_active_class(self):
  self.assertEqual(self.cert.all_depth_diagonal_classes,80)
  self.assertEqual(self.cert.rooted_only_classes,5)
  for group in self.groups:
   if first_dormant(group[0])<2:continue
   rep=group[0]
   for other in group:
    scales=projective_scaling(rep,other)
    self.assertIsNotNone(scales)
    for depth in (5,6):
     left=CouplingTower(rep.rules,depth); right=CouplingTower(other.rules,depth)
     for x in product(range(3),repeat=depth):
      for action in 'AB':
       self.assertEqual(scale_state(left.step(x,action),scales),
                        right.step(scale_state(x,scales),action))

 def test_rooted_identical_but_full_state_different(self):
  a=CouplingTower((RULES[0],RULES[0],RULES[0]),5)
  b=CouplingTower((RULES[0],RULES[0],RULES[1]),5)
  self.assertEqual(rooted_graph(a),rooted_graph(b))
  self.assertIsNone(projective_scaling(a,b))
  self.assertEqual(sum(a.step(s,'B')==s for s in product(range(3),repeat=5)),81)
  self.assertEqual(sum(b.step(s,'B')==s for s in product(range(3),repeat=5)),54)

 def test_hidden_rule_first_visible_in_fifth_coordinate(self):
  p,h=RULES[4],RULES[5]
  a=CouplingTower((p,h,RULES[1]),5);b=CouplingTower((p,h,RULES[3]),5)
  self.assertTrue(all(a.step(s,'A')==b.step(s,'A') for s in product(range(3),repeat=5)))
  self.assertTrue(any(a.step(s,'B')!=b.step(s,'B') for s in product(range(3),repeat=5)))

 def test_inverse_and_projection_for_729_models_on_sample(self):
  probes=((0,0,0,0,0,0),(2,1,2,1,0,2),(1,2,0,2,1,0))
  for w in self.worlds:
   six=CouplingTower(w.rules,6)
   for state in probes:
    for a in 'AB':
     moved=six.step(state,a)
     self.assertEqual(six.inverse(moved,a),state)
     self.assertEqual(moved[:-1],w.step(state[:-1],a))

 def test_rotation_returns_after_648_turns_but_not_universal(self):
  moved=rotation(self.groups)
  self.assertEqual(len(moved),729)
  self.assertEqual(len(set(moved.values())),729)
  self.assertTrue(all(w!=moved[w] for w in moved))
  self.assertEqual(self.cert.rotation_order,648)
  for start in moved:
   current=start
   for _ in range(648):current=moved[current]
   self.assertEqual(start,current)
   self.assertEqual(rooted_graph(start), rooted_graph(moved[start]))

 def test_symbolic_fixed_B_matches_every_concrete_state(self):
  from work.arc_like_maze.third_coupling import count_fixed_B_formula
  for world in construct_family(2):
   self.assertEqual(count_fixed_B_formula(world),
                    sum(world.step(s,'B')==s for s in product(range(3),repeat=world.depth)))

 def test_any_finite_level_admits_a_nonconjugate_extension(self):
  from work.arc_like_maze.third_coupling import extension_obstruction
  for rules in ((RULES[0],), (RULES[4],RULES[5]), (RULES[4],RULES[5],RULES[8])):
   outcome=extension_obstruction(rules)
   self.assertEqual(outcome.status,'OPEN_UNRESTRICTED_EXTENSION')
   self.assertEqual(outcome.zero_extension_fixed,3*outcome.base_fixed)
   self.assertEqual(outcome.identity_extension_fixed,outcome.base_fixed)

 def test_fourth_coupling_exhaustive_stress_check(self):
  worlds=construct_family(4)
  groups=classify_rooted(worlds)
  self.assertEqual((len(worlds),len(groups)),(6561,341))
  self.assertEqual(sorted(Counter(map(len,groups)).items()),
                   [(8,64),(16,256),(36,16),(162,4),(729,1)])
  self.assertEqual(lcm(*(len(group) for group in groups)),11664)

 def test_budget_unknown_and_validation(self):
  with self.assertRaisesRegex(ValueError,'UNKNOWN'):
   rooted_graph(CouplingTower((RULES[4],RULES[5],RULES[6]),5),state_budget=2)
  with self.assertRaises(ValueError):CouplingTower((RULES[0],RULES[0],RULES[0]),4)
  with self.assertRaises(ValueError):construct_family(5)
  with self.assertRaises(ValueError):CouplingTower((RULES[0],RULES[0],RULES[0]),5).step((0,)*5,'C')
if __name__=='__main__':unittest.main()
