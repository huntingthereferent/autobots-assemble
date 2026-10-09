from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy,lc):
 r=None
 for _ in range(abs(dx)):r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
 return r
def reach():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 click(e,12,10);move(e,-4,2,1)
 click(e,5,13);move(e,0,-6,1)
 click(e,16,17)
 for _ in range(3):e.step(GameAction.from_id(5),data={})
 r=move(e,-4,-8,1)
 r=e.step(GameAction.from_id(7),data={})
 return e,r
def G(r):
 F=np.array(r.frame[0],int)
 return np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
clicks=[(10,4),(2,6),(9,10)]
for i,p in enumerate(clicks):
 e,r=reach();B=G(r);r=click(e,*p);A=G(r)
 D={(x,y) for y in range(20) for x in range(20) if B[y,x]!=A[y,x]}
 print("OBJ",i,"CLICK",p,"DIFF_N",len(D),"DIFF_BOX",(min(x for x,y in D),min(y for x,y in D),max(x for x,y in D),max(y for x,y in D)))
 vals=Counter(int(A[y,x]) for x,y in D)
 print(" AFTER_DIFF_VALS",vals)
 print(" AFTER_UNIQ",sorted(np.unique(A).tolist()))
 for y in range(20):
  row=''.join({12:'.',4:'4',8:'*',14:'e',0:'0',9:'9',11:'b',10:'.'}.get(int(v),'?') for v in A[y])
  if any(ch not in '.4' for ch in row):print(f"{y:02}",row)
