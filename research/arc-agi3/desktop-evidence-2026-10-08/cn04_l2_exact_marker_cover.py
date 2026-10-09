from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import defaultdict

def op(A):
 H,W=A.shape
 B=np.empty((W,H),dtype=A.dtype)
 for r in range(H):
  for c in range(W):B[c,H-1-r]=A[r,c]
 return B
def orientations(A):
 out=[A]
 for _ in range(3):out.append(op(out[-1]))
 return out
def marker_cells(A):
 return {(c,r) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c]) in (8,13)}

# reach L2 using learned L1 plan
a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
g=e._game;sp=list(g.current_level.get_sprites());W,H=g.current_level.grid_size
print("LEVEL",g.level_index+1,"N",len(sp),"GRID",W,H)

states=[]
for i,s in enumerate(sp):
 A=np.array(s.render(),dtype=int)
 ss=[]
 seen=set()
 for k,O in enumerate(orientations(A)):
  key=(O.shape,O.tobytes())
  if key in seen:continue
  seen.add(key)
  M=marker_cells(O)
  h,w=O.shape
  for x in range(W-w+1):
   for y in range(H-h+1):
    G=frozenset((x+dx,y+dy) for dx,dy in M)
    cost=k+abs(x-s.x)+abs(y-s.y)
    ss.append((cost,k,x,y,G,O.shape))
 states.append(ss)
 print("STATES",i,len(ss),"markers",len(marker_cells(A)))

# Search order: most markers first.
order=sorted(range(len(sp)),key=lambda i:-len(marker_cells(np.array(sp[i].render(),dtype=int))))
best=[None]
nodes=[0]
def dfs(depth,occ,chosen,cost):
 nodes[0]+=1
 if best[0] is not None and cost>=best[0][0]:return
 if depth==len(order):
  if occ and all(v==2 for v in occ.values()):
   best[0]=(cost,dict(chosen),dict(occ));print("BEST",best[0][0],best[0][1],flush=True)
  return
 i=order[depth]
 # after first object, candidate must cover at least one currently undercovered marker.
 need={p for p,v in occ.items() if v==1}
 cand=states[i]
 if depth>0:
  cand=[s for s in cand if s[4]&need]
 cand=sorted(cand,key=lambda s:s[0])
 for st in cand:
  c,k,x,y,G,sh=st
  # no coordinate may exceed multiplicity 2
  if any(occ.get(p,0)>=2 for p in G):continue
  # pruning: a new marker introduced this late must still be coverable by remaining sprites
  nocc=dict(occ)
  for p in G:nocc[p]=nocc.get(p,0)+1
  chosen[i]=(k,x,y,G,sh)
  dfs(depth+1,nocc,chosen,cost+c)
  del chosen[i]

dfs(0,{}, {},0)
print("NODES",nodes[0])
print("FINAL_BEST",best[0])
assert best[0] is not None
