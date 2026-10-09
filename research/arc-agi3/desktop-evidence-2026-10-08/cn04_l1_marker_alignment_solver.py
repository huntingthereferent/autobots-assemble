from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,itertools

def op(A):
 H,W=A.shape
 B=np.empty((W,H),dtype=A.dtype)
 for r in range(H):
  for c in range(W):
   B[c,H-1-r]=A[r,c]
 return B

def orientations(A):
 out=[A]
 for _ in range(3):out.append(op(out[-1]))
 return out

def markers(A):
 return {v:{(c,r) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c])==v} for v in (8,13)}

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");g=e._game
sp=list(g.current_level.get_sprites())
base=[np.array(s.render(),dtype=int) for s in sp]
ori=[orientations(A) for A in base]
W,H=g.current_level.grid_size
print("GRID",W,H,"START",[(s.x,s.y,s.width,s.height) for s in sp])

best=None
for k0,A0 in enumerate(ori[0]):
 m0=markers(A0)
 for k1,A1 in enumerate(ori[1]):
  m1=markers(A1)
  # Require the same count of each marker label; then infer translation delta from one label.
  if any(len(m0[v])!=len(m1[v]) for v in (8,13)):continue
  deltas=None
  ok=True
  for v in (8,13):
   if not m0[v]:continue
   # all possible deltas mapping m1[v] onto m0[v]
   ds=set()
   for p in m0[v]:
    for q in m1[v]:
     dx=p[0]-q[0];dy=p[1]-q[1]
     if {(x+dx,y+dy) for x,y in m1[v]}==m0[v]:ds.add((dx,dy))
   deltas=ds if deltas is None else deltas&ds
  if not deltas:continue
  for dx,dy in deltas:
   # global positions satisfy pos1 = pos0 + delta
   for x0 in range(W-A0.shape[1]+1):
    for y0 in range(H-A0.shape[0]+1):
     x1=x0+dx;y1=y0+dy
     if not (0<=x1<=W-A1.shape[1] and 0<=y1<=H-A1.shape[0]):continue
     # score public-action cost: rotations + Manhattan movement
     c=(k0+k1+abs(x0-sp[0].x)+abs(y0-sp[0].y)+abs(x1-sp[1].x)+abs(y1-sp[1].y))
     cand=(c,k0,(x0,y0),k1,(x1,y1),dx,dy)
     if best is None or cand<best:best=cand

print("BEST",best)
assert best is not None
