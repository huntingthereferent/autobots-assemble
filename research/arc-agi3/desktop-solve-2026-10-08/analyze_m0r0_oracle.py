import json, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

trace=json.load(open(r"C:\Users\teepa\arc3\solve\m0r0_oracle_trace.json"))
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")

def g():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).copy()

def neighborhood(a,x,y,r=3):
    out=[]
    for yy in range(max(0,y-r),min(64,y+r+1)):
        out.append("".join(format(int(v),"x") for v in a[yy,max(0,x-r):min(64,x+r+1)]))
    return out

last=env.observation_space.levels_completed
level_start=0
for i,t in enumerate(trace):
    aid=t[0]
    before=g()
    lvl=env.observation_space.levels_completed
    data={}
    if aid==6:
        x,y=t[1],t[2]
        data={"x":x,"y":y}
        print("CLICK_PRE","idx",i,"level",lvl,"xy",(x,y),"color",int(before[y,x]),"nb",neighborhood(before,x,y))
    action=getattr(GameAction,"ACTION"+str(aid)) if aid else GameAction.RESET
    out=env.step(action,data=data,reasoning={"oracle_analysis":True})
    after=g()
    if aid==6:
        ys,xs=np.where(before!=after)
        pairs={}
        for yy,xx in zip(ys,xs):
            k=(int(before[yy,xx]),int(after[yy,xx]))
            pairs[k]=pairs.get(k,0)+1
        print("CLICK_POST","idx",i,"n",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"pairs",pairs,"state",out.state)
    now=out.levels_completed
    if now>last:
        print("LEVEL_UP","from",last,"to",now,"trace_indices",(level_start,i),"segment_actions",i-level_start+1)
        level_start=i+1
        last=now
print("FINAL",env.observation_space.levels_completed,env.observation_space.state)
