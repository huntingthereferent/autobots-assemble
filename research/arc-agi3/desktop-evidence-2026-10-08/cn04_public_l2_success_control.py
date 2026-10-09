from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def reach_l2():
 e=a.make("cn04");click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 return e,r
def md(e,dx,dy):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>1:return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>1:return r
 return r
# Public-index mapping control:
# p0 start(3,3)->(3,9), p1(12,4)->(8,12), p2(4,11)->(4,11), p3(16,16), k3 ->(12,14)
e,r=reach_l2()
# collision-safe execution order: p1 -> p2 -> p0 -> p3
click(e,15,4);r=md(e,-4,8) or r
click(e,7,11) # p2 no move
click(e,3,3);r=md(e,0,6) or r
click(e,16,17)
for _ in range(3):r=e.step(GameAction.from_id(5),data={})
r=md(e,-4,-2) or r
print("CONTROL",r.levels_completed,r.state.name)
assert r.levels_completed==2
