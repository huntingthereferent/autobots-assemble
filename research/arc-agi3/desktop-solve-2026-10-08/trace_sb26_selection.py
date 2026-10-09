import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def diff(a,b):
    ys,xs=np.where(a!=b)
    rows=[]
    for y,x in zip(ys,xs):
        rows.append((int(x),int(y),int(a[y,x]),int(b[y,x])))
    return rows

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
path=[(35,58),(19,58),(43,58),(27,58)]
prev=grid(env.observation_space)
print("initial status row53",[(x,int(prev[53,x])) for x in range(64) if int(prev[53,x])!=4])
for i,p in enumerate(path,1):
    a=GameAction.ACTION6; a.set_data({"x":p[0],"y":p[1]})
    out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"selection_trace","i":i})
    cur=grid(out)
    dd=diff(prev,cur)
    print("CLICK",i,p,"n",len(dd),"changes",dd[:80])
    print(" row53",[(x,int(cur[53,x])) for x in range(64) if int(cur[53,x])!=4])
    prev=cur

out=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate"})
cur=grid(out); dd=diff(prev,cur)
print("ACTION5 n",len(dd),"changes",dd[:80],"levels",out.levels_completed,"state",out.state)
print(" row53",[(x,int(cur[53,x])) for x in range(64) if int(cur[53,x])!=4])
