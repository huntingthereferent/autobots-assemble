from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

def op(A):
 H,W=A.shape
 B=np.empty((W,H),dtype=A.dtype)
 for r in range(H):
  for c in range(W):B[c,H-1-r]=A[r,c]
 return B
def canon(A):
 C=np.zeros(A.shape,dtype=int);C[A==-1]=-1;C[A==8]=8;C[A==13]=13;C[(A!=-1)&(A!=8)&(A!=13)]=1
 return C

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

def selected_index(e):
 sp=list(e._game.current_level.get_sprites())
 return sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1

def select_idx(root,idx):
 ee=copy.deepcopy(root)
 if selected_index(ee)==idx:return ee
 sp=list(ee._game.current_level.get_sprites());s=sp[idx]
 A=np.array(s.render(),dtype=int);inv=invmap(ee._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp]
   trial=copy.deepcopy(ee)
   trial.step(GameAction.from_id(6),data={"x":x,"y":y})
   if selected_index(trial)==idx:return trial
 raise RuntimeError(idx)

for idx in range(4):
 ee=select_idx(e,idx);s=ee._game.xseexqzst
 A=np.array(s.render(),dtype=int)
 P=op(canon(A))
 ee.step(GameAction.from_id(5),data={})
 B=np.array(ee._game.xseexqzst.render(),dtype=int);Q=canon(B)
 print("OBJ",idx,"A",A.shape,"B",B.shape,"GEOM_MATCH",P.shape==Q.shape and np.array_equal(P,Q),
       "M8",int((A==8).sum()),int((B==8).sum()),"M13",int((A==13).sum()),int((B==13).sum()))
 if not (P.shape==Q.shape and np.array_equal(P,Q)):
  print(" BEFORE_CANON");print(canon(A));print(" AFTER_CANON");print(Q)
