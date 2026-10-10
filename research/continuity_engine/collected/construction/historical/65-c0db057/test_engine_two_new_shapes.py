"""Regression witnesses for new 48-law + zero-trace native research spaces."""
import unittest
from collections import Counter
from itertools import product

from engine_two_window48_research import (
    Window48, family48, classify, count_word, Engine2WindowResearch, audit48,
)
from engine_two_zero_trace_extension import (
    ZERO, F3, VERTICES, INDEX, ZeroTraceSpace, solve_correction,
    all_selected_corrections, Engine2CorrectionResearch, run_examples, trace,
    count_whole_zero_trace_family,
)


class Window48IntegrationTests(unittest.TestCase):
    def test_all_48_are_distinct_and_all_pair_types_match_the_old_record(self):
        result=audit48()
        self.assertEqual((result['laws'],result['unique_tables'],result['pair_witnesses']),(48,48,2304))
        self.assertEqual((result['rooted_pairs'],result['nonroot_pairs']),(144,36))
        self.assertEqual(result['distribution'],{
            "('ROOTED_FULL', None)":144,
            "('FULL_UNROOTED', None)":36,
            "('FULL_OBSTRUCTED', 'B')":1728,
            "('FULL_OBSTRUCTED', 'BBB')":288,
            "('FULL_OBSTRUCTED', 'AABAB')":72,
            "('FULL_OBSTRUCTED', 'ABABAB')":36,
        })

    def test_every_law_and_generator_has_an_inverse_at_multiple_depths(self):
        for law in family48():
            for depth in (3,4):
                for s in product(F3,repeat=depth):
                    for gen in 'AB':
                        self.assertEqual(law.inverse(law.step(s,gen),gen),s)
                        if depth>3:
                            self.assertEqual(law.step(s,gen)[:-1],law.step(s[:-1],gen))

    def test_one_world_is_full_equivalent_but_not_equivalent_at_root(self):
        a,b=Window48(0,0,1,0),Window48(0,0,1,1)
        lab=Engine2WindowResearch()
        full=lab.investigate(a,b,watch='FULL_STATE')
        root=lab.investigate(a,b,watch='ROOTED')
        self.assertEqual(full.status,'FULL_STATE_NONROOT_EQUIVALENT')
        self.assertEqual(root.status,'ROOTED_OBSTRUCTED_BY_WORD_COLLISION')
        self.assertNotEqual(full.mapped_origin,(0,0,0))
        self.assertEqual(full.checked_edges,54)
        w1,w2,src,dst1,dst2=root.collision
        self.assertEqual(a.apply((0,0,0),w1),src)
        self.assertEqual(a.apply((0,0,0),w2),src)
        self.assertNotEqual(dst1,dst2)
        self.assertEqual(b.apply((0,0,0),w1),dst1)
        self.assertEqual(b.apply((0,0,0),w2),dst2)

    def test_middle_support_needs_the_long_six_action_obstruction(self):
        for k in (1,2):
            a,b=Window48(k,0,1,0),Window48(k,0,1,1)
            result=Engine2WindowResearch().investigate(a,b)
            self.assertEqual(result.obstruction_word,'ABABAB')
            self.assertNotEqual(*result.obstruction_counts)
            for length in range(1,6):
                for word in map(''.join,product('AB',repeat=length)):
                    self.assertEqual(count_word(a,word),count_word(b,word))

    def test_reenter_requires_the_actual_parent_target(self):
        a,b,c=Window48(0,0,0,0),Window48(0,1,0,0),Window48(0,2,0,0)
        lab=Engine2WindowResearch()
        lab.investigate(a,b)
        result=lab.reenter(0,c)
        self.assertEqual((result.source,result.target,result.parent_id),(b,c,0))
        with self.assertRaisesRegex(ValueError,'parent'):
            lab.investigate(a,c,parent_id=0)

    def test_no_false_new_world_is_inferred_from_change_of_chart(self):
        a,b=Window48(2,0,0,0),Window48(2,1,0,0)
        root=Engine2WindowResearch().investigate(a,b,watch='ROOTED')
        self.assertEqual(root.status,'ROOTED_FULL_EQUIVALENT')
        self.assertEqual(root.mapped_origin,(0,0,0))
        self.assertNotEqual(a.rule(),b.rule())


class ZeroTraceShapeTests(unittest.TestCase):
    def test_independent_all_162_matrix_ranks_and_cyclic_order_counts(self):
        result=count_whole_zero_trace_family()
        self.assertEqual(result['configurations'],162)
        self.assertEqual(result['admitted'],22410)
        self.assertEqual(result['order_three_possible'],11106)
        self.assertEqual(result['order_nine_possible'],12492)
        self.assertEqual(result['both'],1188)
        self.assertEqual(result['multi_component_gauge'],12)
        self.assertEqual(result['histogram'],{
            '1 components, rank 3':12,'1 components, rank 4':24,
            '1 components, rank 5':36,'1 components, rank 6':72,
            '3 components, rank 3':2,'3 components, rank 4':4,
            '3 components, rank 5':4,'3 components, rank 6':8,
        })

    def test_three_example_categories_follow_the_document(self):
        data=run_examples()
        self.assertEqual(data['order_three_only']['selected_orders'],[3])
        self.assertEqual(data['order_nine_only']['selected_orders'],[9])
        self.assertEqual(data['both_orders']['selected_orders'],[3,9])
        self.assertEqual(data['signed_cycle_obstruction']['status'],'SIGNED_CYCLE_OBSTRUCTION')
        self.assertEqual(data['signed_cycle_obstruction']['components'],1)
        self.assertEqual(data['engine_one_calls'],0)
        self.assertEqual(data['reentered_parent'],2)

    def test_same_world_law_same_fifth_table_two_different_corrections(self):
        p=ZeroTraceSpace(1,(1,0,2),(0,0,0))
        evidence=solve_correction(p,ZERO)
        self.assertTrue(evidence.admissible)
        self.assertEqual(evidence.component_count,3)
        self.assertEqual(evidence.equations_verified,81)
        corrections=all_selected_corrections(evidence)
        self.assertEqual(set(corrections),{3,9})
        self.assertNotEqual(corrections[3].values,corrections[9].values)
        for choice in corrections.values():
            self.assertEqual(choice.audit_generators(),486)
            self.assertEqual(len(choice.mark_orbit()),choice.order)

    def test_order_3_and_order_9_have_distinct_pointed_recurrence(self):
        p=ZeroTraceSpace(1,(1,0,2),(0,0,0))
        options=all_selected_corrections(solve_correction(p,ZERO))
        origin=(0,0,0,0,0)
        t3,t9=origin,origin
        for _ in range(3):
            t3=options[3].move_mark(t3)
            t9=options[9].move_mark(t9)
        self.assertEqual(t3,origin)
        self.assertNotEqual(t9,origin)
        for _ in range(6):t9=options[9].move_mark(t9)
        self.assertEqual(t9,origin)

    def test_signed_cycle_obstruction_is_replayable_not_a_missing_solution_guess(self):
        p=ZeroTraceSpace(1,(0,0,0),(0,0,1))
        q=(1,)+(0,)*8
        witness=solve_correction(p,q)
        self.assertFalse(witness.admissible)
        self.assertIsNone(witness.normalized)
        self.assertTrue(witness.obstruction.replay(p,q))
        self.assertNotEqual(witness.obstruction.one,witness.obstruction.two)

    def test_changing_constants_keeps_the_exact_cocycle_equations(self):
        p=ZeroTraceSpace(1,(1,0,2),(0,0,0))
        evidence=solve_correction(p,ZERO)
        choices=all_selected_corrections(evidence)
        for order,selected in choices.items():
            self.assertEqual(selected.order,order)
            self.assertTrue(any(trace(p,selected.values))==(order==9))

    def test_zero_trace_has_162_declared_configurations_not_all_48_worlds(self):
        configs=[]
        for g in (1,2):
            for Q in product(F3,repeat=3):
                if sum(Q)%3:continue
                for a,b in product(F3,repeat=2):
                    configs.append(ZeroTraceSpace(g,Q,(0,a,b)))
        self.assertEqual(len(configs),162)
        self.assertEqual(len(set(configs)),162)

    def test_same_shape_reentry_cannot_jump_to_a_different_grammar_or_coupling(self):
        lab=Engine2CorrectionResearch()
        p=ZeroTraceSpace(1,(1,0,2),(0,0,0))
        lab.investigate(p,ZERO)
        again=lab.reenter(0)
        self.assertEqual(again.parent_id,0)
        self.assertEqual([s.order for s in again.selected],[3,9])
        other=ZeroTraceSpace(1,(0,0,0),(0,0,1))
        with self.assertRaisesRegex(ValueError,'bridge'):
            lab.investigate(other,ZERO,parent_id=0)

    def test_ab_inverses_are_preserved_under_new_correction_shape(self):
        p=ZeroTraceSpace(1,(1,0,2),(0,0,0))
        q=ZERO
        def inverse_B(state):
            u=state[0]
            v=(state[1]-p.gain*(u+1))%3
            z=(state[2]-((0,1,2,0,2,1,1,1,1)[3*u+v]))%3
            y=(state[3]-p.quotient[(z+(0,1,1)[v])%3]-p.offsets[v])%3
            t=(state[4]-q[3*z+y])%3
            return (u,v,z,y,t)
        for x in product(F3,repeat=5):
            self.assertEqual(inverse_B(p.step(x,'B',q)),x)

if __name__=='__main__':
    unittest.main(verbosity=2)