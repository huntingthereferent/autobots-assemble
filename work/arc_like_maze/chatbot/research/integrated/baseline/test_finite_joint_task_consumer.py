import unittest
from dataclasses import replace
from finite_goal_priority import Law, ROOT
from finite_cross_pin_join import join
from finite_joint_task_consumer import consume

class FiniteJointTaskConsumerTests(unittest.TestCase):
    def setUp(self):
        self.old, self.new = Law((0,0,0)), Law((0,1,2))
        self.joint = join(self.old,self.new,('A','BAA'))

    def test_complete_from_existing_witness_only(self):
        status,checks,_=consume(self.old,self.new,self.joint,goals=((1,0,0),(2,1,0)),
            edges=((ROOT,'A'),((1,1,0),'A')),
            paths=(('BAA',(2,1,0),(2,1,0)),),
            destinations=(((1,0,0),(1,0,0)),))
        self.assertEqual(status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        self.assertEqual(len(checks),6)
        self.assertTrue(all(row[2] for row in checks))
        self.assertEqual((len(self.joint.state_pairs),len(self.joint.admitted_edges)),(5,4))

    def test_complete_law_edge_does_not_imply_admission(self):
        # An old-rule transition always exists in the finite law, but was not observed.
        self.assertEqual(self.old.step((1,0,0),'B'),(1,2,0))
        status,checks,_=consume(self.old,self.new,self.joint,edges=(((1,0,0),'B'),))
        self.assertEqual(status,'TASK_REQUIREMENTS_UNPROVED')
        self.assertFalse(checks[0][2])

    def test_paired_goal_not_same_as_witnessed_path(self):
        status,checks,_=consume(self.old,self.new,self.joint,
            goals=((1,0,0),), paths=(('AB',(1,1,0),(1,1,0)),))
        self.assertEqual(status,'TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual([row[2] for row in checks],[True,False])

    def test_conflicting_join_cannot_admit_task(self):
        collision=join(self.old,self.new,('A','BAB'))
        status,checks,certificate=consume(self.old,self.new,collision,goals=((1,0,0),))
        self.assertEqual(status,'JOINT_RELATION_CONFLICT_WITNESSED')
        self.assertFalse(checks)
        self.assertEqual(certificate[2],'SOURCE_STATE_CONFLICT')

    def test_forged_admitted_edge_rejected_by_independent_laws(self):
        extra=((1,0,0),'B',(1,2,0),(1,0,0),(1,2,0))
        forged=replace(self.joint,admitted_edges=self.joint.admitted_edges+(extra,))
        with self.assertRaises(ValueError):consume(self.old,self.new,forged,
                                                    edges=(((1,0,0),'B'),))

    def test_identical_rules_unobserved_edge_remains_unproved(self):
        law=Law((0,0,1))
        witness=join(law,law,('A','BAA'))
        status,checks,_=consume(law,law,witness,edges=(((1,0,0),'B'),))
        self.assertEqual(status,'TASK_REQUIREMENTS_UNPROVED')

if __name__=='__main__': unittest.main()
