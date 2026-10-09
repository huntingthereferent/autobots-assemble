"""Bounded public-state action exploration; no saved SK48 route or _game reads."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy,collections,time,logging
logging.disable(logging.CRITICAL)
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def key(e):
 r=e.observation_space
 a=np.asarray(r.frame[-1],dtype=np.uint8)
 return hashlib.blake2s(a.tobytes(),digest_size=12).digest(),r.levels_completed,r.state.name
front=[(root,())]
seen={key(root)}
start=time.time()
for depth in range(1,27):
 nxt=[]
 changes=collections.Counter()
 for env,path in front:
  current=key(env)
  for z in (1,2,3,4):
   e=copy.deepcopy(env)
   obs=e.step(GameAction.from_id(z),data={})
   new=key(e)
   if obs.levels_completed>0 or obs.state.name=="WIN":
    print("SOLUTION",path+(z,),"STEP",depth,"LEVEL",obs.levels_completed,flush=True)
    raise SystemExit
   changes[(z,new[0]!=current[0])]+=1
   if new in seen:continue
   seen.add(new);nxt.append((e,path+(z,)))
 if len(nxt)>13000:
  print("BOUND_CAP",depth,len(nxt),flush=True);break
 print("DEPTH",depth,"UNIQUE_NEW",len(nxt),"SEEN",len(seen),
       "MOVEMENT",dict(changes),"SECONDS",round(time.time()-start,1),flush=True)
 front=nxt
 if not front:break
