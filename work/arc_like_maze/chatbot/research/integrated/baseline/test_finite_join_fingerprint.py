import unittest
from finite_goal_priority import Law
from finite_join_fingerprint import witnessed_digest,compare_task
from finite_cross_pin_join import join

class FiniteFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.a,self.b=Law((0,0,0)),Law((0,1,2))
        self.options=tuple((str(i),w,witnessed_digest(self.a,self.b,w)[0])
                for i,w in enumerate((('A','BAA'),('B','ABB'))))
    def test_identical_evidence_same_digest(self):
        x,w=witnessed_digest(self.a,self.b,('A','BAA'))
        y,_=witnessed_digest(self.a,self.b,('A','BAA'))
        self.assertEqual(x,y)
        self.assertEqual(len(x),64)
    def test_changed_word_or_pinned_context_changes_digest(self):
        x,_=witnessed_digest(self.a,self.b,('A','BAA'))
        y,_=witnessed_digest(self.a,self.b,('B','ABB'))
        z,_=witnessed_digest(self.a,self.b,('A','BAA'),target_id='different')
        self.assertEqual(len({x,y,z}),3)
    def test_no_task_evidence_transfer(self):
        status,records,winners=compare_task(self.a,self.b,
            {'edges':(((1,1,0),'A'),((1,0,0),'B'))},self.options)
        self.assertEqual(status,'TASK_UNPROVED_ACROSS_TESTED_WITNESSES')
        self.assertEqual([r[2] for r in records],[1,1])
        self.assertEqual(winners,())
    def test_winner_named_not_global(self):
        status,records,winners=compare_task(self.a,self.b,
            {'edges':(((1,1,0),'A'),)},self.options)
        self.assertEqual(status,'TASK_COMPLETED_BY_INDEPENDENT_WITNESS')
        self.assertEqual(winners,('0',))
    def test_fingerprint_claim_cannot_admit_wrong_witness(self):
        altered=list(self.options)
        altered[1]=('1',altered[1][1],altered[0][2])
        status,records,winners=compare_task(self.a,self.b,
            {'edges':(((1,0,0),'B'),)},tuple(altered))
        self.assertEqual(records[1][1],'WITNESS_FINGERPRINT_MISMATCH')
        self.assertEqual(winners,())
    def test_conflict_is_not_identity(self):
        result,w= witnessed_digest(self.a,self.b,('A','BAB'))
        self.assertIsNone(result)
        self.assertEqual(w.status,'JOINT_RELATION_CONFLICT_WITNESSED')
if __name__=='__main__':unittest.main()
