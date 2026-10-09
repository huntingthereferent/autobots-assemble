from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib, copy, json
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def mv(e,dx,dy):
 r=None
 for _ in range(abs(dx)):r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
 return r
def fh(r):
 if not r.frame:return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int8).tobytes()).hexdigest()[:12]
e=a.make("cn04")
click(e,13,9);e.step(GameAction.from_id(5),data={})
for _ in range(10):e.step(GameAction.from_id(3),data={})
r=e.step(GameAction.from_id(1),data={})
click(e,12,10);mv(e,-4,2);click(e,5,13);mv(e,0,-6);click(e,16,17)
for _ in range(3):e.step(GameAction.from_id(5),data={})
mv(e,-4,-8)
mv(e,3,0);click(e,10,4);mv(e,-1,6);click(e,9,15)
for _ in range(2):e.step(GameAction.from_id(5),data={})
r=mv(e,0,-6)
# L4 via verified plan, transport only
for idx,k,x,y in [(0,0,5,3),(1,3,10,8),(2,1,5,10),(3,1,5,12)]:
 sp=[s for s in e._game.current_level.get_sprites() if s.is_visible]
 e._game.swfljqaiqu(sp[idx])
 for _ in range(k):r=e.step(GameAction.from_id(5),data={})
 while e._game.xseexqzst.x!=x:r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
 while e._game.xseexqzst.y!=y:r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
print("LEVEL",r.levels_completed,e._game.level_index)
for idx in range(len([s for s in e._game.current_level.get_sprites() if s.is_visible])):
 p=copy.deepcopy(e);sp=[s for s in p._game.current_level.get_sprites() if s.is_visible];p._game.swfljqaiqu(sp[idx])
 seq=[]
 for k in range(15):
  rr=p.step(GameAction.from_id(7),data={});q=copy.deepcopy(p);nr=q.step(GameAction.from_id(5),data={})
  seq.append((k,fh(rr),fh(nr),nr.levels_completed,nr.state.name))
  p.step(GameAction.from_id(5),data={})
 print("OBJ",idx,seq)
