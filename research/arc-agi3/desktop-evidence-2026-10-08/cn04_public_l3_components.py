from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy,lc):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>lc:return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>lc:return r
 return r
def reach():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 click(e,12,10);r=move(e,-4,2,1) or r
 click(e,5,13);r=move(e,0,-6,1) or r
 click(e,16,17)
 for _ in range(3):r=e.step(GameAction.from_id(5),data={})
 r=move(e,-4,-8,1) or r
 r=e.step(GameAction.from_id(7),data={})
 return e,r
e,r=reach()
F=np.array(r.frame[0],int)
G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
bg=Counter(G.flatten().tolist()).most_common(1)[0][0]
S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=bg}
out=[]
while S:
 p=S.pop();q=[p];c={p}
 while q:
  x,y=q.pop()
  for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if n in S:S.remove(n);c.add(n);q.append(n)
 xs=[x for x,y in c];ys=[y for x,y in c]
 vals={int(G[y,x]) for x,y in c}
 marks={(x,y) for x,y in c if int(G[y,x])==8}
 out.append((len(c),(min(xs),min(ys),max(xs),max(ys)),sorted(vals),sorted(marks),sorted(c)[:8]))
for z in sorted(out,key=lambda q:(q[1][1],q[1][0])):print(z)
