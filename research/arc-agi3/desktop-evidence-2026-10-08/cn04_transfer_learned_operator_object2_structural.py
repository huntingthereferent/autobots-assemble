from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

def apply(A):
 H,W=A.shape
 B=np.empty((W,H),dtype=A.dtype)
 for r in range(H):
  for c in range(W):
   B[c,H-1-r]=A[r,c]
 return B

def canon(A):
 # infer semantic roles from this puzzle's observed rendering:
 # -1 = empty; 8 = special marker; every other visible value = ordinary material.
 C=np.zeros(A.shape,dtype=int)
 C[A==-1]=-1
 C[A==8]=8
 C[(A!=-1)&(A!=8)]=1
 return C

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
sp=list(e._game.current_level.get_sprites())
A=np.array(sp[1].render(),dtype=int)
P=apply(canon(A))

e.step(GameAction.from_id(6),data={"x":41,"y":31})
assert list(e._game.current_level.get_sprites()).index(e._game.xseexqzst)==1
e.step(GameAction.from_id(5),data={})
B=np.array(e._game.xseexqzst.render(),dtype=int)
Q=canon(B)

print("PRED_CANON");print(P)
print("OBS_CANON");print(Q)
print("STRUCT_MATCH",np.array_equal(P,Q))
assert np.array_equal(P,Q)
print("PASS learned graph-derived operator transfers structurally; render color is state-dependent")
