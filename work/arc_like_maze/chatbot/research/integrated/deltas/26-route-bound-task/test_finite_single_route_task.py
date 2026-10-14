import unittest
from dataclasses import replace
from finite_single_route_task import fixture,evaluate

class FiniteSingleRouteTests(unittest.TestCase):
    def test_left_route_accepts_own_unique_edge(self):
        r=evaluate(fixture('left'),edges=(((1,0,0),'B'),))
        self.assertEqual(r.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual((len(r.pairs),len(r.edges)),(6,5))
    def test_right_route_accepts_different_edge(self):
        r=evaluate(fixture('right'),edges=(((0,1,2),'B'),))
        self.assertEqual(r.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
    def test_no_cross_route_edge_borrowing(self):
        self.assertEqual(evaluate(fixture('left'),edges=(((0,1,2),'B'),)).status,
            'ROUTE_TASK_REQUIREMENTS_UNPROVED')
    def test_combined_obligations_need_one_route(self):
        edges=(((1,0,0),'B'),((0,1,2),'B'))
        self.assertEqual(evaluate(fixture('left'),edges=edges).status,
            'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual(evaluate(fixture('right'),edges=edges).status,
            'ROUTE_TASK_REQUIREMENTS_UNPROVED')
    def test_exact_path_requirements(self):
        self.assertEqual(evaluate(fixture('right'),paths=(('BB',(0,2,2),(0,2,1)),)).status,
                         'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(evaluate(fixture('left'),paths=(('BB',(0,2,2),(0,2,1)),)).status,
                         'ROUTE_TASK_REQUIREMENTS_UNPROVED')
    def test_false_destination_and_invalid_task_rejected(self):
        self.assertEqual(evaluate(fixture('right'),destinations=(((0,2,2),(0,2,2)),)).status,
            'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        with self.assertRaises(ValueError):evaluate(fixture('left'))
        with self.assertRaises(ValueError):fixture('middle')
    def test_failed_route_cannot_be_used_as_proof(self):
        invalid=replace(fixture('left'),status='SECOND_INTERTWINING_CONFLICT')
        self.assertEqual(evaluate(invalid,edges=(((1,0,0),'B'),)).status,'ROUTE_UNPROVED')

if __name__=='__main__':unittest.main()
