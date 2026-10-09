from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy):
 r=None
 for _ in range(abs(dx)):r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
 return r
def reach():
 e=a.make("cn04");click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 e.step(GameAction.from_id(1),data={})
 click(e,12,10);move(e,-4,2)
 click(e,5,13);move(e,0,-6)
 click(e,16,17)
 for _ in range(3):e.step(GameAction.from_id(5),data={})
 move(e,-4,-8)
 r=e.step(GameAction.from_id(7),data={})
 return e,r
def grid(r):
 F=np.array(r.frame[0],int)
 return np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
e,r=reach();G=grid(r)
# target public component bbox 2..6,4..10
cells=[(x,y) for y in range(4,11) for x in range(2,7) if int(G[y,x])!=12]
print("CELLS",cells)
for p in cells:
 ee,rr=reach();rr=click(ee,*p);A=grid(rr)
 n8=int((A==8).sum());vals=Counter(A.flatten().tolist())
 print("CLICK",p,"N8",n8,"UNIQ",sorted(vals),"COUNT8",vals.get(8,0),"COUNT0",vals.get(0,0),"COUNT11",vals.get(11,0),"COUNT14",vals.get(14,0),"COUNT15",vals.get(15,0))
