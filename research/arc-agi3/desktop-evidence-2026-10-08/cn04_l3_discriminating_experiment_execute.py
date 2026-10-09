from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy,lc):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return r
 return r
def reach_l3():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 # public-discovered L2 success
 click(e,12,10);r=move(e,-4,2,1) or r
 click(e,5,13);r=move(e,0,-6,1) or r
 click(e,16,17)
 for _ in range(3):r=e.step(GameAction.from_id(5),data={})
 r=move(e,-4,-8,1) or r
 assert r.levels_completed==2
 return e,r

e,r=reach_l3()
# Discriminating plan:
# obj0 k2, (10,3)->(10,4)
# obj1 k0, (2,4)->(11,4)
# obj2 k0, (9,9)->(9,5)
# collision-safe order obj0 -> obj2 -> obj1
click(e,10,4)
for _ in range(2):r=e.step(GameAction.from_id(5),data={})
r=move(e,0,1,2) or r

click(e,9,10)
r=move(e,0,-4,2) or r

click(e,2,6)
r=move(e,9,0,2) or r

print("DISCRIM_RESULT",r.levels_completed,r.state.name)
print("PRED_H1",False,"PRED_H2",True)
