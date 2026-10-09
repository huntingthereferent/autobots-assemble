import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64)
def player(a):
 # player witness: color12 10-cell 5x2 component
 ys,xs=np.where(a==12)
 if len(xs):
  return (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
 return None
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
print("start",player(g(env.observation_space)),env.observation_space.levels_completed)
for i in range(12):
 o=env.step(GameAction.ACTION1,data={},reasoning={"probe":"straight_up"})
 print(i+1,player(g(o)),o.levels_completed,o.state)
 if o.levels_completed>0 or "GAME_OVER" in str(o.state):break
