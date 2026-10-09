from collections import deque
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

A=[GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4]

def k(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).tobytes()

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
root=env.observation_space
rootk=k(root)
q=deque([()])
seen={rootk}
expanded=0
interactions=0
max_depth=24
max_expand=5000
while q and expanded<max_expand:
    path=q.popleft()
    if len(path)>=max_depth:
        continue
    for act in A:
        env.step(GameAction.RESET,data={},reasoning={"probe":"bfs_reset"})
        interactions+=1
        cur=env.observation_space
        ok=True
        for aname in path:
            cur=env.step(getattr(GameAction, aname),data={},reasoning={"probe":"bfs_replay"})
            interactions+=1
            if cur.levels_completed>0:
                print("FOUND_ON_REPLAY",list(path),"depth",len(path),"interactions",interactions)
                raise SystemExit
        cur=env.step(act,data={},reasoning={"probe":"bfs_expand"})
        interactions+=1
        npth=path+(act.name,)
        if cur.levels_completed>0:
            print("FOUND",list(npth),"depth",len(npth),"interactions",interactions,"seen",len(seen))
            raise SystemExit
        kk=k(cur)
        if kk not in seen:
            seen.add(kk)
            q.append(npth)
    expanded+=1
    if expanded%100==0:
        print("expanded",expanded,"queue",len(q),"seen",len(seen),"depth",len(path),"interactions",interactions)
print("NOT_FOUND","expanded",expanded,"queue",len(q),"seen",len(seen),"interactions",interactions)
