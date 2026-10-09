"""SK48: replay known direction sequence with public-frame click coordinates.

Non-general scripted route (directions are saved). No private _game reads.
This probes whether saved late switch actions can be grounded in public pixels.
"""
from pathlib import Path
import numpy as np, collections, logging, json, hashlib
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

source=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_complete_replay.py").read_text()
scope={}
exec(source.split("for trial in (0,1):")[0],scope)
actions=scope["prefix"] + scope["P6"]+scope["P7"]+scope["P8"]

def frame(r): return np.asarray(r.frame[-1],dtype=np.uint8).reshape((64,64))

def top_keys(r):
 a=frame(r); hits=[]
 for y in range(0,49):
  for x in range(0,59):
   b=int(a[y,x])
   if b not in (6,15):continue
   block=a[y:y+6,x:x+6]
   if (np.all(block[0,:]==b) and np.all(block[:,0]==b)
       and int(block[1,1]) in (0,4)
       and any(int(c)!=b for c in block[1:5,1:5].flat)):
    hits.append((x,y,b))
 # Unique visual keys are the bordered 6x6 tokens on the playing field.
 return sorted(hits,key=lambda t:t[0])

logging.disable(logging.CRITICAL)
for trial in range(2):
 a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make("sk48")
 prev=0;old_active=0;milestones=[];clicks=[];failed=False
 for k,z in enumerate(actions,1):
  obs=e.observation_space
  if z==6:
   keys=top_keys(obs)
   if len(keys)!=2:
    print("WALL",'keys',keys,'step',k,'level',obs.levels_completed,flush=True)
    failed=True;break
   chosen=1 if old_active==0 else 0
   x,y,color=keys[chosen]
   click=(x+2,y+2)
   clicks.append((k,obs.levels_completed,click,[it[:2] for it in keys],old_active))
   r=e.step(GameAction.ACTION6,data={'x':click[0],'y':click[1]})
   old_active=chosen
  else:
   r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>prev:
   prev=r.levels_completed
   milestones.append((k,prev))
   old_active=0
  if r.state is GameState.GAME_OVER:
   print("GAME_OVER",trial,k,prev,flush=True);failed=True;break
  if r.state is GameState.WIN:break
 print("SK48_PUBLIC_ROUTE",trial,"ACTIONS",k,"LEVELS",r.levels_completed,"STATE",r.state.name,
       "MILESTONES",milestones,"CLICKS",clicks,"FAILED",failed,flush=True)
