import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"diag":"reach"})

def reach_l2(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy); click(env,tx,ty)
    return env.step(GameAction.ACTION5,data={},reasoning={"diag":"eval"})

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def runs(g):
    bg=max(set(map(int,g.ravel())),key=lambda c:int(np.sum(g==c)))
    out=[]
    for y in range(64):
        x=0
        while x<64:
            c=int(g[y,x]); x0=x
            while x+1<64 and int(g[y,x+1])==c: x+=1
            n=x-x0+1
            if c!=bg and n>=10:
                out.append((y,c,x0,x,n))
            x+=1
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
g1=grid(env.observation_space)
print("L1 RUNS")
for r in runs(g1): print(r)
reach_l2(env)
g2=grid(env.observation_space)
print("L2 RUNS")
for r in runs(g2): print(r)
