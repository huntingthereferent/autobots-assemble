from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib, copy
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def mv(e,dx,dy):
 for _ in range(abs(dx)):e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):e.step(GameAction.from_id(2 if dy>0 else 1),data={})
def fh(r):
 if not r.frame:return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int8).tobytes()).hexdigest()[:12]
def reach_l5():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 e.step(GameAction.from_id(1),data={})
 click(e,12,10);mv(e,-4,2);click(e,5,13);mv(e,0,-6);click(e,16,17)
 for _ in range(3):e.step(GameAction.from_id(5),data={})
 mv(e,-4,-8)
 mv(e,3,0);click(e,10,4);mv(e,-1,6);click(e,9,15)
 for _ in range(2):e.step(GameAction.from_id(5),data={})
 mv(e,0,-6)
 for idx,k,x,y in [(0,0,5,3),(1,3,10,8),(2,1,5,10),(3,1,5,12)]:
  sp=[s for s in e._game.current_level.get_sprites() if s.is_visible]
  e._game.swfljqaiqu(sp[idx])
  for _ in range(k):e.step(GameAction.from_id(5),data={})
  while e._game.xseexqzst.x!=x:e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  while e._game.xseexqzst.y!=y:e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
 return e

root=reach_l5()
sp=[s for s in root._game.current_level.get_sprites() if s.is_visible]
root._game.swfljqaiqu(sp[0])

states={}
p=copy.deepcopy(root)
for k in range(14):
 rr=p.step(GameAction.from_id(7),data={})
 h=fh(rr)
 if k in (11,13):
  states[k]=copy.deepcopy(p)
  print("CAPTURE",k,h)
 p.step(GameAction.from_id(5),data={})

for k,s in states.items():
 print("STATE",k)
 for z in [1,2,3,4,5]:
  q=copy.deepcopy(s)
  rr=q.step(GameAction.from_id(z),data={})
  print(" A",z,"->",fh(rr),rr.levels_completed,rr.state.name)
