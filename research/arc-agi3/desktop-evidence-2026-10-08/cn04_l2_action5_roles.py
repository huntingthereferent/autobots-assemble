from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
assert r.levels_completed==1

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out

def select_idx(e,idx):
 sp=list(e._game.current_level.get_sprites());s=sp[idx]
 A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])!=-1 and (s.x+cc,s.y+rr) in inv:
    x,y=inv[(s.x+cc,s.y+rr)]
    ee=copy.deepcopy(e)
    ee.step(GameAction.from_id(6),data={"x":x,"y":y})
    sp2=list(ee._game.current_level.get_sprites())
    sel=sp2.index(ee._game.xseexqzst) if ee._game.xseexqzst in sp2 else -1
    if sel==idx:return ee
 raise RuntimeError(idx)

for idx in range(4):
 ee=select_idx(e,idx)
 s=ee._game.xseexqzst
 A=np.array(s.render(),dtype=int)
 ee.step(GameAction.from_id(5),data={})
 B=np.array(ee._game.xseexqzst.render(),dtype=int)
 print("\nOBJ",idx,"A",A.shape,"B",B.shape,
       "COUNT",int((A!=-1).sum()),int((B!=-1).sum()),
       "M8",int((A==8).sum()),int((B==8).sum()),
       "M13",int((A==13).sum()),int((B==13).sum()))
 print("BEFORE");print(A)
 print("AFTER");print(B)
