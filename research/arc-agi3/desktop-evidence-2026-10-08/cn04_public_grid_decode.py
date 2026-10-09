from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

a=Arcade(operation_mode=OperationMode.NORMAL)

def obs(e):
 r=e.step(GameAction.from_id(7),data={})
 F=np.array(r.frame[0],dtype=int)
 G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],dtype=int)
 return G,r

e=a.make("cn04")
G,r=obs(e)
print("GRID_UNIQ",sorted(np.unique(G).tolist()))
for y in range(20):
 row=''.join({10:'.',0:'o',14:'u',8:'*',4:'h',3:'X'}.get(int(v),'?') for v in G[y])
 if set(row)!={'.'}:print(f"{y:02}",row)

# Components on logical board excluding background.
S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=10}
cc=[]
while S:
 p=S.pop();q=[p];c={p}
 while q:
  x,y=q.pop()
  for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if n in S:S.remove(n);c.add(n);q.append(n)
 cc.append(c)
for i,c in enumerate(sorted(cc,key=lambda c:-len(c))):
 vals={int(G[y,x]) for x,y in c}
 if 4 in vals:continue
 print("OBJ",i,"BOX",(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c)),
       "MARKERS",sorted((x,y) for x,y in c if int(G[y,x])==8),"VALS",vals)
