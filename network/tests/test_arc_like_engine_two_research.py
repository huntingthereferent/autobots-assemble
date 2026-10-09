"""Tests at Engine 2's public mathematical research entry/exit points."""
import json
import unittest
from itertools import product

from work.arc_like_maze.engine_two_research import Engine2ResearchKernel
from work.arc_like_maze.window_two import WindowProcess

F3 = range(3)
ZERO = (0,) * 9
CARRY2 = tuple(int(right == 2) for left, right in product(F3, repeat=2))
CARRY3 = tuple(int(left == 2 and right == 2) for left, right in product(F3, repeat=2))
DOUBLE = tuple((2*v) % 3 for v in CARRY3)
W9 = WindowProcess(1, (CARRY2, ZERO), (ZERO,))
W27 = WindowProcess(1, (CARRY2, CARRY3), (ZERO,))
W27S = WindowProcess(1, (CARRY2, DOUBLE), (ZERO,))
FIBER = Engine2ResearchKernel.fiber(5)


class ResearchKernelContinuationTests(unittest.TestCase):
    def setUp(self):
        self.kernel = Engine2ResearchKernel()

    def test_eight_is_unknown_nine_is_distinguished(self):
        early = self.kernel.start(W9, W27, FIBER, 8)
        self.assertEqual((early.status, early.powers_examined), ('UNKNOWN_BUDGET', 8))
        late = self.kernel.resume(early.serialize(), 9,
                                  expected_question_id=early.record['question_id'])
        self.assertEqual((late.status, late.powers_examined), ('DISTINGUISHED_B_ACTIONS', 9))
        self.assertEqual((len(late.record['observations'][-1]['source_fixed']),
                          len(late.record['observations'][-1]['target_fixed'])), (81, 0))
        self.assertEqual(late.record['observations'][:8], early.record['observations'])
        self.assertEqual(late.record['simultaneous_A_B'], 'UNKNOWN_NOT_WATCHED')

    def test_distinction_is_not_erased_by_longer_budget(self):
        result = self.kernel.start(W9, W27, FIBER, 9)
        revived = self.kernel.resume(result.serialize(), 27)
        self.assertEqual((revived.status, revived.powers_examined),
                         ('DISTINGUISHED_B_ACTIONS', 9))

    def test_26_unknown_27_earns_restricted_B_conjugacy(self):
        early = self.kernel.start(W27, W27S, FIBER, 26)
        self.assertEqual(early.status, 'UNKNOWN_BUDGET')
        result = self.kernel.resume(early.serialize(), 27)
        self.assertEqual((result.status, result.powers_examined),
                         ('B_ONLY_CONJUGACY_WITNESSED', 27))
        pairs = result.record['B_bijection']
        f = {tuple(a): tuple(b) for a, b in pairs}
        self.assertEqual(len(f), 81)
        self.assertEqual(len(set(f.values())), 81)
        for x in FIBER:
            self.assertEqual(f[W27.step(x, 'B')], W27S.step(f[x], 'B'))

    def test_positive_resume_preserves_map_and_terminal_status(self):
        done = self.kernel.start(W27, W27S, FIBER, 27)
        self.assertEqual(self.kernel.resume(done.serialize(), 30).record['B_bijection'],
                         done.record['B_bijection'])

    def test_source_observations_and_relation_cannot_change(self):
        first = self.kernel.start(W9, W27, FIBER, 8)
        baseline = first.record
        for mutate in ('fixed', 'relation', 'law', 'carrier', 'status', 'witness'):
            altered = json.loads(first.serialize())
            if mutate == 'fixed':
                altered['observations'][0]['source_fixed'].append([0]*5)
            elif mutate == 'relation':
                altered['question']['operation'] = 'A_SUCCESSIVE_COMPOSITION'
            elif mutate == 'law':
                altered['question']['source']['stem'][0][1] = 2
            elif mutate == 'carrier':
                altered['question']['carrier'][0][1] = 1
            elif mutate == 'status':
                altered['status'] = 'B_ONLY_CONJUGACY_WITNESSED'
            else:
                altered['B_bijection'] = [[[0]*5, [0]*5]]
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.kernel.resume(json.dumps(altered), 9,
                                   expected_question_id=baseline['question_id'])

    def test_actual_witness_replay_rejects_forged_observation(self):
        first = self.kernel.start(W9, W27, FIBER, 8)
        altered = json.loads(first.serialize())
        altered['observations'][0]['source_anchor_image'][1] = 2
        with self.assertRaisesRegex(ValueError, 'mathematical replay'):
            self.kernel.resume(json.dumps(altered), 9)

    def test_valid_origin_and_projection_scope_are_preserved(self):
        first = self.kernel.start(W9, W27, FIBER, 8)
        self.assertEqual(len(first.record['question']['carrier']), 81)
        self.assertEqual(first.record['question']['carrier'][0], [0,0,0,0,0])
        self.assertEqual(first.record['question']['relation'],
                         'B_ONLY_ON_DECLARED_INVARIANT_CARRIER')

    def test_budget_and_carrier_constraints(self):
        with self.assertRaises(ValueError):
            self.kernel.start(W9, W27, FIBER, 0)
        with self.assertRaises(ValueError):
            self.kernel.start(W9, W27, FIBER[:-1], 8)
        with self.assertRaises(ValueError):
            self.kernel.start(W9, W27, ((0,0,0,0,0),)*2, 8)
        record = self.kernel.start(W9, W27, FIBER, 8)
        with self.assertRaises(ValueError):
            self.kernel.resume(record.serialize(), 7)

    def test_short_equal_fixed_point_counts_never_imply_equivalence(self):
        result = self.kernel.start(W27, W27S, FIBER, 9)
        self.assertEqual(result.status, 'UNKNOWN_BUDGET')
        self.assertEqual(result.record['B_bijection'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
