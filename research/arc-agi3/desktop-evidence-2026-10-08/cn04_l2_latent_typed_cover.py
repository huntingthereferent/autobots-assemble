from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

def op(A):
 H,W=A.shape
 B=np.empty((W,H),dtype=A.dtype)
 for r in range(H):
  for c in range(W):B[c,H-1-r]=A[r,c]
 return B
def apply_k(A,k):
 B=A.copy()
 for _ in range(k%4):B=op(B)
 return B
def markers(A):
 return frozenset((c,r,int(A[r,c])) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c]) in (8,13))

a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
g=e._game;sp=list(g.current_level.get_sprites());W,H=g.current_level.grid_size

states=[]
for i,s in enumerate(sp):
 raw=np.array(g.hlxyvcmpk[s.name],dtype=int)
 current=apply_k(raw,(s.rotation//90)%4)
 ss=[]
 for k in range(4):
  O=apply_k(current,k)
  M=markers(O);h,w=O.shape
  for x in range(W-w+1):
   for y in range(H-h+1):
    G=frozenset((x+dx,y+dy,v) for dx,dy,v in M)
    cost=k+abs(x-s.x)+abs(y-s.y)
    ss.append((cost,k,x,y,G,O.shape))
 states.append(ss)
 print("OBJ",i,"ROT",s.rotation,"RAW_MARK",sorted(markers(raw)),"CURRENT_MARK",sorted(markers(current)))

order=sorted(range(len(sp)),key=lambda i:-len(states[i][0][4]))
best=[None];nodes=[0]
def dfs(depth,occ,chosen,cost):
 nodes[0]+=1
 if best[0] is not None and cost>=best[0][0]:return
 if depth==len(order):
  if occ and all(v==2 for v in occ.values()):
   best[0]=(cost,dict(chosen),dict(occ));print("BEST",best[0][0],best[0][1],flush=True)
  return
 i=order[depth]
 need={p for p,v in occ.items() if v==1}
 cand=states[i] if depth==0 else [s for s in states[i] if s[4]&need]
 for st in sorted(cand,key=lambda s:s[0]):
  c,k,x,y,G,sh=st
  if any(occ.get(p,0)>=2 for p in G):continue
  nocc=dict(occ)
  for p in G:nocc[p]=nocc.get(p,0)+1
  chosen[i]=(k,x,y,G,sh)
  dfs(depth+1,nocc,chosen,cost+c)
  del chosen[i]
dfs(0,{}, {},0)
print("NODES",nodes[0])
print("FINAL",best[0])
assert best[0] is not None
