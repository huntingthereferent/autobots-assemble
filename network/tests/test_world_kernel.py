import unittest
from runtime.world_kernel import World,Body,move,branch,relations
class WorldKernelTest(unittest.TestCase):
 def test_wrap_and_recursion(self):
  w=World('root',5,(Body('a',4,1),Body('b',0,1)))
  n,e=move(w,'a',1,0)
  self.assertEqual((0,1), (n.bodies[0].x,n.bodies[0].y))
  self.assertEqual(e.before,w.fingerprint())
  self.assertEqual(e.after,n.fingerprint())
  m,f=move(n,'a',1,0)
  self.assertEqual(f.before,e.after)
  self.assertEqual(m.revision,2)
 def test_branch_and_wall(self):
  w=World('root',5,(Body('a',1,1),))
  b=branch(w,'fork')
  self.assertEqual(b.parent,w.fingerprint())
  self.assertEqual(w.revision,0)
  n,e=move(b,'missing',1,1)
  self.assertEqual(n,b)
  self.assertEqual(e.result,'WALL')
 def test_periodic_relations(self):
  w=World('root',5,(Body('a',4,0),Body('b',0,0)))
  self.assertEqual(relations(w)[0][2],1)
if __name__=='__main__':unittest.main()
