"""Independent tests for multi-WATCH bounded Boundary Math embryo."""
import unittest
from itertools import product
from engine_two_boundary_experiment import CouplingLaw, ZERO, IDENTITY
from engine_two_research_kernel import (
    RootedReading, RootCollision, Engine2ResearchKernel, rooted_watch,
    fixed_B_watch, transition_watch, projection_watch, run_research,
)

NEGATIVE=(0,2,1)

class MathematicalResearchKernelTests(unittest.TestCase):
    def test_rooted_full_graph_equivalence_retains_actual_state_map(self):
        src = CouplingLaw((IDENTITY, IDENTITY))
        dst = CouplingLaw((NEGATIVE, NEGATIVE))
        w = rooted_watch(src,dst)
        self.assertEqual(w.status, 'ROOTED_EQUIVALENT')
        self.assertEqual(w.before_reachable, w.after_reachable)
        self.assertEqual(len(w.state_correspondence), w.before_reachable)
        self.assertEqual(len({b for _,b in w.state_correspondence}), len(w.state_correspondence))
        mapping=dict(w.state_correspondence)
        for a,b in mapping.items():
            for gen in 'AB':
                self.assertEqual(mapping[src.step(a,gen)],dst.step(b,gen))
        self.assertIn('not full-state', w.omissions[0])

    def test_rooted_collision_contains_two_replayable_words(self):
        src=CouplingLaw((IDENTITY,))
        dst=CouplingLaw((ZERO,))
        w=rooted_watch(src,dst)
        self.assertEqual(w.status,'ROOTED_OBSTRUCTED')
        self.assertIsNotNone(w.obstruction)
        self.assertTrue(w.obstruction.verify(src,dst))
        self.assertNotEqual(w.obstruction.old_word,w.obstruction.new_word)

    def test_rooted_equivalence_can_hide_fixed_state_boundary(self):
        src=CouplingLaw((ZERO,ZERO))
        dst=CouplingLaw((ZERO,IDENTITY))
        kernel=Engine2ResearchKernel()
        result=kernel.investigate(src,dst)
        self.assertEqual(result.status,'WATCHED_DIFFERENCE')
        self.assertEqual([r.status for r in result.readings],
            ['ROOTED_EQUIVALENT','BOUNDARY','LABELED_ARROWS_DIFFER'])
        self.assertEqual((result.readings[1].before_count,result.readings[1].after_count),(27,9))
        self.assertIn('rooted continuation matches',result.remainder[0])
        self.assertEqual(result.selection_reason.split(':')[0], 'AUTO')

    def test_separate_requested_watch_does_not_launder_scope(self):
        src=CouplingLaw((ZERO,ZERO)); dst=CouplingLaw((ZERO,IDENTITY))
        k=Engine2ResearchKernel()
        rooted=k.investigate(src,dst, 'ROOTED')
        self.assertEqual(len(rooted.readings),1)
        self.assertEqual(rooted.status,'EARNED_LOCAL_PRESERVATION')
        fixed=k.investigate(src,dst,'FIXED_B')
        self.assertEqual(fixed.status,'WATCHED_DIFFERENCE')
        self.assertEqual(fixed.readings[0].status,'BOUNDARY')
        self.assertNotEqual(rooted.readings[0].watch,fixed.readings[0].watch)

    def test_identical_fixed_B_can_hide_concrete_arrow_change(self):
        a=CouplingLaw((IDENTITY,IDENTITY))
        b=CouplingLaw((IDENTITY,NEGATIVE))
        fixed=fixed_B_watch(a,b)
        edge=transition_watch(a,b)
        self.assertEqual(fixed.status,'EARNED_ZERO_FOR_FIXED_B_WATCH')
        self.assertEqual((fixed.before_count,fixed.after_count),(3,3))
        self.assertEqual(edge.status,'LABELED_ARROWS_DIFFER')
        self.assertEqual(edge.changed_A,0)
        self.assertGreater(edge.changed_B,0)
        for x,gen,p,q in edge.sample_changes:
            self.assertEqual(a.step(x,gen),p)
            self.assertEqual(b.step(x,gen),q)
            self.assertNotEqual(p,q)

    def test_native_projection_two_directed_generator_squares(self):
        a=CouplingLaw((IDENTITY,))
        b=CouplingLaw((IDENTITY,ZERO))
        r=projection_watch(a,b)
        self.assertEqual(r.status,'PROJECTION_PRESERVED')
        self.assertEqual(r.new_coordinate_fiber,3)
        self.assertEqual(r.checked_state_actions,2*3**b.depth)
        self.assertTrue(any('NOT bijective' in s for s in r.omissions))

    def test_unadmitted_extension_is_wall(self):
        a=CouplingLaw((IDENTITY,))
        b=CouplingLaw((NEGATIVE,ZERO))
        result=projection_watch(a,b)
        self.assertEqual(result.status,'WALL_UNADMITTED_EXTENSION')
        self.assertEqual(result.checked_state_actions,0)

    def test_follow_previous_witness_constructs_new_space_without_engine_one(self):
        k=Engine2ResearchKernel()
        a=CouplingLaw((ZERO,ZERO)); b=CouplingLaw((ZERO,IDENTITY))
        first=k.investigate(a,b)
        proj, compared=k.extend_from_finding(0)
        self.assertEqual(proj.readings[0].status,'PROJECTION_PRESERVED')
        self.assertEqual(compared.parent_id,1)
        self.assertEqual(compared.source_rules[:-1], b.rules)
        self.assertEqual(compared.target_rules[:-1], b.rules)
        self.assertEqual(len(k.findings),3)
        self.assertEqual(compared.readings[1].status,'BOUNDARY')
        self.assertTrue(all(f.parent_id is not None for f in k.findings[1:]))

    def test_wrong_parent_target_must_not_become_reentry(self):
        k=Engine2ResearchKernel()
        k.investigate(CouplingLaw((ZERO,)),CouplingLaw((IDENTITY,)))
        with self.assertRaisesRegex(ValueError,'parent finding'):
            k.investigate(CouplingLaw((ZERO,)),CouplingLaw((NEGATIVE,)),parent_id=0)

    def test_unknown_budget_retained_in_rooted_watch(self):
        a=CouplingLaw((IDENTITY,)); b=CouplingLaw((IDENTITY,))
        r=rooted_watch(a,b,max_reachable=1)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertGreater(len(r.unresolved),0)

    def test_boundary_budget_walls_not_proofs(self):
        k=Engine2ResearchKernel(maximum_state_carrier=30)
        before=CouplingLaw((IDENTITY,IDENTITY))
        after=CouplingLaw((IDENTITY,NEGATIVE))
        result=k.investigate(before,after, 'TRANSITIONS')
        self.assertEqual(result.status,'PARTIAL_OR_UNKNOWN')
        self.assertEqual(result.readings[0].status,'UNKNOWN_BUDGET')

    def test_auto_budget_preserves_missing_fixed_membership_witness(self):
        k=Engine2ResearchKernel(maximum_state_carrier=30)
        a=CouplingLaw((ZERO, ZERO))
        b=CouplingLaw((ZERO, IDENTITY))
        out=k.investigate(a,b)
        self.assertEqual(len(out.readings),3)
        self.assertEqual(out.readings[1].status,'UNKNOWN_BUDGET')
        self.assertEqual(out.readings[1].watch,'complete-space B-fixed membership')
        self.assertEqual(out.status,'PARTIAL_OR_UNKNOWN')
        self.assertTrue(any('budget' in u for u in out.unresolved))

    def test_full_dimension_four_independent_watch_contracts(self):
        a=CouplingLaw((ZERO,ZERO,ZERO,ZERO))
        b=CouplingLaw((ZERO,ZERO,ZERO,IDENTITY))
        k=Engine2ResearchKernel()
        res=k.investigate(a,b)
        self.assertEqual(res.readings[0].status,'ROOTED_EQUIVALENT')
        self.assertEqual(res.readings[1].status,'BOUNDARY')
        self.assertEqual((res.readings[1].before_count,res.readings[1].after_count),(243,81))
        self.assertEqual(res.readings[2].status,'LABELED_ARROWS_DIFFER')
        self.assertEqual(res.readings[2].total_carrier_states,729)

    def test_identical_laws_earn_local_preservation_only(self):
        x=CouplingLaw((IDENTITY,))
        result=Engine2ResearchKernel().investigate(x,x)
        self.assertEqual(result.status,'EARNED_LOCAL_PRESERVATION')
        self.assertEqual([w.status for w in result.readings],
            ['ROOTED_EQUIVALENT','EARNED_ZERO_FOR_FIXED_B_WATCH',
             'EARNED_ZERO_FOR_TRANSITIONS_WATCH'])

    def test_explicit_invalid_watch_is_rejected(self):
        k=Engine2ResearchKernel()
        with self.assertRaisesRegex(ValueError,'WATCH'):
            k.investigate(CouplingLaw((ZERO,)),CouplingLaw((IDENTITY,)), 'ANYTHING')

    def test_experiment_output_retains_witnesses_and_remainders(self):
        report=run_research()
        self.assertEqual(len(report['cases']),4)
        self.assertEqual(report['engine_one_calls'],0)
        self.assertTrue(report['cases'][0]['remainder'])

if __name__=='__main__':
    unittest.main(verbosity=2)