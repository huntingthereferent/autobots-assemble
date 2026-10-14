import unittest
from finite_goal_priority import Law
from finite_explicit_task import parse_explicit, task_candidates

WORDS=(('ABAA','ABBABA'), ('ABAA','AAABB','BAAAB'), ('ABBABA',))
OLD,NEW=Law((0,0,1)),Law((0,0,0))

class TaskOracleTests(unittest.TestCase):
    def test_strict_text_recognizes_only_user_declared_edge(self):
        self.assertEqual(parse_explicit('goals: (0,1,1), (0,2,0); require: edge (0,0,0) B'),
                         (((0,1,1),(0,2,0)),((0,0,0),'B')))
        self.assertEqual(parse_explicit('goals: (0,1,1), (0,2,0)'),
                         (((0,1,1),(0,2,0)),None))

    def test_ambiguous_text_rejected_without_movement(self):
        for text in ('keep B','goals: (0,1,1); preserve B',
                     'goals: (0,1,1); require: edge (3,0,0) B',
                     'goals: (0,1,1), (0,1,1)'):
            self.assertIsNone(parse_explicit(text))
            self.assertEqual(task_candidates(OLD,NEW,text,WORDS)[0],'UNKNOWN_TASK')

    def test_explicit_required_edge_prunes_only_replayed_conflicts(self):
        self.assertEqual(task_candidates(OLD,NEW,
            'goals: (0,1,1), (0,2,0); require: edge (0,0,0) B',WORDS),
            ('REQUIRED_EDGE',('CONTRADICTED','NOT_CONTRADICTED','CONTRADICTED')))

    def test_no_constraint_no_pruning(self):
        self.assertEqual(task_candidates(OLD,NEW,'goals: (0,1,1), (0,2,0)',WORDS),
                         ('GOALS_ONLY',('NOT_CHECKED',)*3))

if __name__=='__main__':unittest.main()
