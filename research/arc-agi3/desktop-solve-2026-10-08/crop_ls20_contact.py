import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64).astype(int)
def show(a,y0,y1,x0,x1):
 chars="0123456789ABCDEF"
 for y in range(y0,y1+1):
  print(f"{y:02d} "+''.join(chars[int(a[y,x])] if 0<=int(a[y,x])<16 else '?' for x in range(x0,x1+1)))
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
print("INITIAL TOP")
show(grid(env.observation_space),6,22,28,44)
for _ in range(6):o=env.step(GameAction.ACTION1,data={},reasoning={"probe":"up"})
print("\nCONTACT")
show(grid(o),6,24,28,44)
