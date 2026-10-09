from collections import deque
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

ACTS=[GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4]

def pos(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 a=a.reshape(64,64)
 # moving cap: connected 10-cell color12 component; only color12 in level
 ys,xs=np.where(a==12)
 if len(xs)<10:return None
 # bbox of all color12 is okay for first level
 return (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
start=pos(env.observation_space)
q=deque([(start,())]);seen={start};expanded=0;interactions=0
max_depth=30
while q and expanded<300:
 pthpos,path=q.popleft()
 if len(path)>=max_depth:continue
 for aname in ["ACTION1","ACTION2","ACTION3","ACTION4"]:
  env.step(GameAction.RESET,data={},reasoning={"probe":"nav_reset"});interactions+=1
  o=env.observation_space
  bad=False
  for prev in path:
   o=env.step(getattr(GameAction,prev),data={},reasoning={"probe":"nav_replay"});interactions+=1
   if o.levels_completed>0:
    print("FOUND_REPLAY",path,"actions",len(path),"interactions",interactions);raise SystemExit
   if "GAME_OVER" in str(o.state):bad=True;break
  if bad:continue
  o=env.step(getattr(GameAction,aname),data={},reasoning={"probe":"nav_expand"});interactions+=1
  npth=path+(aname,)
  if o.levels_completed>0:
   print("FOUND",npth,"depth",len(npth),"interactions",interactions,"seen",len(seen));raise SystemExit
  if "GAME_OVER" in str(o.state):continue
  pp=pos(o)
  if pp is not None and pp not in seen:
   seen.add(pp);q.append((pp,npth))
 expanded+=1
 if expanded%25==0:print("expanded",expanded,"seen",len(seen),"queue",len(q),"depth",len(path),"interactions",interactions)
print("NO_POSITION_PATH","expanded",expanded,"seen",len(seen),"maxdepth",max((len(p) for _,p in q),default=0),"interactions",interactions)
print("POSITIONS",sorted(seen,key=lambda z:(z[1],z[0])))
