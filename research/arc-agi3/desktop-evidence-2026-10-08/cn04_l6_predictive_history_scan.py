from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def mv(e,dx,dy):
 for _ in range(abs(dx)):e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):e.step(GameAction.from_id(2 if dy>0 else 1),data={})
def fh(r):
 if not r.frame:return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int8).tobytes()).hexdigest()[:12]
def reach_l6():
 e=a.make("cn04")
 # L1
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 e.step(GameAction.from_id(1),data={})
 # L2
 click(e,12,10);mv(e,-4,2);click(e,5,13);mv(e,0,-6);click(e,16,17)
 for _ in range(3):e.step(GameAction.from_id(5),data={})
 mv(e,-4,-8)
 # L3
 mv(e,3,0);click(e,10,4);mv(e,-1,6);click(e,9,15)
 for _ in range(2):e.step(GameAction.from_id(5),data={})
 mv(e,0,-6)
 # L4 transport
 for idx,k,x,y in [(0,0,5,3),(1,3,10,8),(2,1,5,10),(3,1,5,12)]:
  sp=[s for s in e._game.current_level.get_sprites() if s.is_visible];e._game.swfljqaiqu(sp[idx])
  for _ in range(k):e.step(GameAction.from_id(5),data={})
  while e._game.xseexqzst.x!=x:e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  while e._game.xseexqzst.y!=y:e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
 # L5 verified plan
 for idx,k,x,y in [(0,4,7,4),(1,0,5,5),(2,3,9,4),(3,3,11,8)]:
  sp=[s for s in e._game.current_level.get_sprites() if s.is_visible];e._game.swfljqaiqu(sp[idx])
  for _ in range(k):e.step(GameAction.from_id(5),data={})
  while e._game.xseexqzst.x!=x:e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  while e._game.xseexqzst.y!=y:e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
 return e
e=reach_l6()
print("LEVEL",e._game.level_index)
allrows={}
for idx in range(len([s for s in e._game.current_level.get_sprites() if s.is_visible])):
 p=copy.deepcopy(e);sp=[s for s in p._game.current_level.get_sprites() if s.is_visible];p._game.swfljqaiqu(sp[idx])
 rows=[]
 for k in range(28):
  rr=p.step(GameAction.from_id(7),data={});cur=fh(rr)
  outs=[]
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(p);nr=q.step(GameAction.from_id(z),data={});outs.append(fh(nr))
  rows.append((cur,tuple(outs)))
  nr=p.step(GameAction.from_id(5),data={})
  if nr.state.name!="NOT_FINISHED":break
 allrows[idx]=rows
 print("OBJ",idx,"ROWS",len(rows))
from collections import defaultdict
for L in range(0,6):
 bad=0;examples=[]
 for idx,rows in allrows.items():
  tab=defaultdict(set)
  for t,(cur,outs) in enumerate(rows):
   hist=tuple(rows[j][0] for j in range(max(0,t-L),t)) if L else ()
   tab[(hist,cur)].add(outs)
  for key,v in tab.items():
   if len(v)>1:
    bad+=1
    if len(examples)<5:examples.append((idx,key,len(v)))
 print("H",L,"AMBIG",bad,"EX",examples)
 if bad==0:
  print("MIN",L);break
