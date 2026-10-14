"""Cross-pin join tests use the same owner fixtures as existing cross-pin comparisons."""
import unittest
from ab_chatbot_cross_pin_join import CrossPinJoin
from test_ab_chatbot_cross_pin_comparison import CrossPinTests

class JoinCrossPinTests(unittest.TestCase):
    make = CrossPinTests.make
    def join(self,words,*,oldlaw=(0,0,0),newlaw=(0,1,2),budget=54):
        old,new,owner,reg,p,q=self.make(oldlaw=oldlaw,newlaw=newlaw,budget=budget)
        req={'required_owner_pins':{'old':p.token,'new':q.token},'join_words':list(words)}
        return CrossPinJoin(old,new,req,registry=reg),old,new,owner,reg,p,q
    def settle_join(self,agent,cap=108):
        for _ in range(40):
            result=agent.advance(max_new_edges=cap)
            if result.status!='SEARCHING':return result
        self.fail('join did not settle under bounded observation')

    def test_consistent_multiple_paths_create_only_observed_partial_pairing(self):
        agent,old,new,*_=self.join(('A','BAA'))
        out=self.settle_join(agent)
        self.assertEqual(out.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertEqual(len(out.state_pairs),5)
        self.assertEqual(len(out.admitted_edges),4)
        self.assertIsNone(out.obstruction)
        self.assertEqual({(s,a) for s,a,*_ in out.admitted_edges},
                         {((0,0,0),'A'), ((0,0,0),'B'), ((0,1,0),'A'), ((1,1,0),'A')})
        self.assertLess(len(out.admitted_edges),2*len(out.state_pairs))

    def test_individually_valid_paths_can_have_incompatible_union(self):
        agent,old,new,*_=self.join(('A','BAB'))
        out=self.settle_join(agent)
        self.assertEqual(out.status,'JOINT_RELATION_CONFLICT_WITNESSED')
        self.assertEqual(out.obstruction.cause,'SOURCE_STATE_CONFLICT')
        self.assertEqual((out.obstruction.previous_word,out.obstruction.incoming_word),('A','BAB'))
        self.assertTrue(out.obstruction.old_equal)
        self.assertFalse(out.obstruction.new_equal)
        self.assertEqual(out.state_pairs,())
        self.assertFalse(out.admitted_edges)

    def test_target_image_collision_against_different_laws(self):
        agent,*_=self.join(('B','ABBABA'),oldlaw=(0,0,1),newlaw=(0,0,0))
        out=self.settle_join(agent)
        self.assertEqual(out.status,'JOINT_RELATION_CONFLICT_WITNESSED')
        self.assertEqual(out.obstruction.cause,'TARGET_STATE_CONFLICT')
        self.assertEqual((out.obstruction.old_equal,out.obstruction.new_equal),(False,True))

    def test_compatible_seed_union_more_than_two_histories(self):
        agent,*_=self.join(('ABAA','ABBABA','A'),oldlaw=(0,0,1),newlaw=(0,0,0))
        out=self.settle_join(agent)
        self.assertEqual(out.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertEqual(len(out.state_pairs),8)
        self.assertGreater(len(out.admitted_edges),3)

    def test_bounded_resumable_without_early_witness(self):
        agent,old,new,*_=self.join(('A','BAA'))
        out=agent.advance(max_new_edges=0)
        self.assertEqual(out.status,'SEARCHING')
        self.assertEqual((out.old_observed,out.new_observed),(0,0))
        out=self.settle_join(agent,cap=1)
        self.assertEqual(out.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')

    def test_budget_exhaustion_is_not_collision(self):
        agent,*_=self.join(('A','BAA'),budget=1)
        out=self.settle_join(agent)
        self.assertEqual(out.status,'UNKNOWN_BUDGET')
        self.assertFalse(out.obstruction)

    def test_tamper_invalidates_result_on_zero_edge_read(self):
        agent,old,new,*_=self.join(('A','BAA'))
        self.assertEqual(self.settle_join(agent).status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        edge=next(iter(old.snapshot.edges))
        old.snapshot.edges[edge]=(2,2,2)
        outcome=agent.advance(max_new_edges=0)
        self.assertEqual(outcome.status,'WALL_OBSERVATION')
        self.assertFalse(outcome.state_pairs)

    def test_withdrawal_invalidates_result(self):
        agent,old,new,owner,reg,p,q=self.join(('A','BAA'))
        self.assertEqual(self.settle_join(agent).status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        reg.revoke(q.token)
        out=agent.advance(max_new_edges=0)
        self.assertEqual(out.status,'OWNER_PIN_UNPROVED')
        self.assertFalse(out.state_pairs)

    def test_snapshot_revision_changed_before_observation(self):
        agent,old,new,*_=self.join(('A','BAA'))
        new.snapshot.revision+=1
        out=agent.advance(max_new_edges=0)
        self.assertEqual(out.status,'UNKNOWN_VERSION')
        self.assertEqual((out.old_observed,out.new_observed),(0,0))

    def test_unknown_pin_bad_words_and_unsupported_keys(self):
        agent,old,new,owner,reg,p,q=self.join(('A','BAA'))
        orig={'required_owner_pins':{'old':p.token,'new':q.token},'join_words':['A','BAA']}
        variants=[{**orig,'join_words':['A','A']},{**orig,'join_words':['A','C']},
                  {**orig,'join_words':['A']},{**orig,'extra':1},
                  {**orig,'required_owner_pins':{'old':'f'*48,'new':q.token}}]
        for req in variants:
            r=CrossPinJoin(old,new,req,registry=reg).advance()
            self.assertIn(r.status,('INVALID_TASK','UNKNOWN_OWNER_PIN'))
        self.assertEqual(len(old.snapshot.edges),0)

if __name__=='__main__':unittest.main()
