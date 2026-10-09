from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy,lc):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>lc:return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>lc:return r
 return r
def reach_l3():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 click(e,12,10);r=move(e,-4,2,1) or r
 click(e,5,13);r=move(e,0,-6,1) or r
 click(e,16,17)
 for _ in range(3):r=e.step(GameAction.from_id(5),data={})
 r=move(e,-4,-8,1) or r
 assert r.levels_completed==2
 return e,r

e,r=reach_l3()
# typed-pruned plan:
# obj0 k0 (10,3)->(9,9)
# obj1 k0 (2,4)->(5,4)
# obj2 k2 (9,9)->(9,3)
# order: obj1 initially selected, then obj0, then obj2
r=move(e,3,0,2) or r
click(e,10,4);r=move(e,-1,6,2) or r
click(e,9,15)
for _ in range(2):r=e.step(GameAction.from_id(5),data={})
r=move(e,0,-6,2) or r
print("TYPED_PREDICTION",r.levels_completed,r.state.name)
assert r.levels_completed==3
print("PASS public-learned latent classes predict L3 completion")
