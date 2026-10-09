import numpy as np
from collections import Counter
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3: a=a[-1]
    return a.reshape(64,64)

def desc(a):
    vals,counts=np.unique(a,return_counts=True)
    return {"colors":dict(zip(map(int,vals),map(int,counts)))}

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ["ls20","sb26"]:
    print("\nGAME",gid)
    env=arc.make(gid)
    o=env.observation_space
    a0=arr(o)
    print("state",o.state,"avail",o.available_actions,"levels",o.levels_completed)
    print("initial",desc(a0))
    for act in [GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4,GameAction.ACTION5,GameAction.ACTION7]:
        try:
            env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
            before=arr(env.observation_space)
            out=env.step(act,data={},reasoning={"probe":"single"})
            after=arr(out)
            ys,xs=np.where(before!=after)
            bbox=None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
            print(act.name,"changed",len(xs),"bbox",bbox,"levels",out.levels_completed,"state",out.state,
                  "color_delta",{k:v for k,v in (Counter(after.ravel())-Counter(before.ravel())).items() if v})
        except Exception as e:
            print(act.name,"ERR",repr(e))
