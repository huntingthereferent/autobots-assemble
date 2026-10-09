"""Public SK48 screenshots printed as compact symbol grids."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
route=(1,1,1,4,4,4,4,3,2,2,4,3,1,4)
def show(title,r):
 a=np.asarray(r.frame[-1],dtype=np.uint8).reshape(64,64)
 print("BOARD",title,"LEVELS",r.levels_completed,flush=True)
 for y in range(6,48):
  s=''.join("0123456789ABCDEF"[v] for v in a[y,5:55])
  if len(set(s))>2 or y in (6,25,28,42,44,47):
   print(f"{y:02} {s}",flush=True)
show("level1_initial",e.observation_space)
for i,z in enumerate(route,1):
 r=e.step(GameAction.from_id(z),data={})
 if i in (7,13,14):show(f"after_{i}",r)
