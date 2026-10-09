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
 print("REACH",r.levels_completed,r.state.name)
 r=e.step(GameAction.from_id(7),data={})
 return e,r
e,r=reach()
F=np.array(r.frame[0],int)
G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
print("UNIQ",sorted(np.unique(G).tolist()),"MODE",Counter(G.flatten().tolist()).most_common(5))
mp={10:'.',12:'.',0:'0',8:'*',4:'4',9:'9',11:'b',14:'e',13:'D',3:'X'}
for y in range(20):
 row=''.join(mp.get(int(v),'?') for v in G[y])
 if len(set(row))>1 or row[0]!='.':print(f"{y:02}",row)
