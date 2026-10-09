from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
# L1
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out
def selidx(e):
 sp=list(e._game.current_level.get_sprites())
 return sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
def select(e,idx):
 if selidx(e)==idx:return
 sp=list(e._game.current_level.get_sprites());s=sp[idx];A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp];e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if selidx(e)==idx:return
 raise RuntimeError(idx)
def move(e,idx,x,y):
 select(e,idx)
 while e._game.xseexqzst.x!=x:
  global r;r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})

move(e,1,8,12)
move(e,2,3,9)
select(e,3);r=e.step(GameAction.from_id(5),data={});move(e,3,10,14)

sp=list(e._game.current_level.get_sprites())
cnt=Counter()
for i,s in enumerate(sp):
 A=np.array(s.render(),dtype=int)
 M={(s.x+c,s.y+rr,int(A[rr,c])) for rr in range(A.shape[0]) for c in range(A.shape[1]) if int(A[rr,c]) in (8,13)}
 print("OBJ",i,"POS",s.x,s.y,"ROT",getattr(s,"rotation",None),"MARKERS",sorted(M))
 for x,y,v in M:cnt[(x,y,v)]+=1
print("COUNTS",sorted(cnt.items()))
print("ALL_EXACT2",all(v==2 for v in cnt.values()))
print("IAH_KEYS",list(getattr(e._game,"iahpylgry",{}).keys()))
for i,s in enumerate(sp):
 print("MATCHED",i,sorted(getattr(e._game,"iahpylgry",{}).get(s.name,set())))
print("COMPLETE_CHECK",e._game.sjwqloivve())
print("LC",r.levels_completed,"STATE",r.state.name)
