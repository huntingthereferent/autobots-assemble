from collections import deque
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

NAMES=("ACTION1","ACTION2","ACTION3","ACTION4")

def grid(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64).astype(np.int8)

def latent(o):
 a=grid(o)
 ys,xs=np.where(a==12)
 if len(xs)<10:return None
 # use the compact color12 component nearest the main playfield, not UI if later duplicated
 # current public level has exactly the moving 10-cell cap.
 x0,x1=int(xs.min()),int(xs.max()); y0,y1=int(ys.min()),int(ys.max())
 pos=(x0,y0,x1,y1)
 # normalized local appearance around the mover; same position means static background
 # cancels, while shape/color/rotation and local interaction state remain observable.
 xa=max(0,x0-3); xb=min(64,x1+4); ya=max(0,y0-3); yb=min(64,y1+7)
 crop=a[ya:yb,xa:xb]
 return pos,crop.tobytes()

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
root=latent(env.observation_space)
q=deque([(root,())]);seen={root};expanded=0;interactions=0
max_depth=32;max_expand=500
while q and expanded<max_expand:
 state,path=q.popleft()
 if len(path)>=max_depth:continue
 for aname in NAMES:
  env.step(GameAction.RESET,data={},reasoning={"probe":"latent_reset"});interactions+=1
  o=env.observation_space
  bad=False
  for prev in path:
   o=env.step(getattr(GameAction,prev),data={},reasoning={"probe":"latent_replay"});interactions+=1
   if o.levels_completed>0:
    print("FOUND_REPLAY",path,"depth",len(path),"interactions",interactions);raise SystemExit
   if "GAME_OVER" in str(o.state):bad=True;break
  if bad:continue
  o=env.step(getattr(GameAction,aname),data={},reasoning={"probe":"latent_expand"});interactions+=1
  npth=path+(aname,)
  if o.levels_completed>0:
   print("FOUND",npth,"depth",len(npth),"interactions",interactions,"seen",len(seen));raise SystemExit
  if "GAME_OVER" in str(o.state):continue
  st=latent(o)
  if st is not None and st not in seen:
   seen.add(st);q.append((st,npth))
 expanded+=1
 if expanded%25==0:print("expanded",expanded,"seen",len(seen),"queue",len(q),"depth",len(path),"interactions",interactions)
print("NOT_FOUND","expanded",expanded,"seen",len(seen),"queue",len(q),"interactions",interactions)
