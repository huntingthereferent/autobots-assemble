from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)
def grid(e):
 r=e.step(GameAction.from_id(7),data={})
 F=np.array(r.frame[0],int)
 return np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int),r
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy):
 r=None
 for _ in range(abs(dx)):r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
 return r
# Public L1 solution: select second at visible cell 13,9; action5 once; move to box origin 2,8
e=a.make("cn04");click(e,13,9);e.step(GameAction.from_id(5),data={})
G,_=grid(e)
# selected bbox from public colors 0/8
pts={(x,y) for y in range(20) for x in range(20) if int(G[y,x]) in (0,8)}
# keep component containing marker around right object/current selection
# known current selected origin still 12,9 from observation, move -10,-1
r=move(e,-10,-1)
print("L1",r.levels_completed,r.state.name)
G,r2=grid(e)
print("L2",r2.levels_completed,"UNIQ",sorted(np.unique(G).tolist()))
for y in range(20):
 row=''.join({10:'.',0:'o',14:'u',8:'*',4:'h',3:'X',9:'q',11:'w'}.get(int(v),'?') for v in G[y])
 if set(row)!={'.'}:print(f"{y:02}",row)
