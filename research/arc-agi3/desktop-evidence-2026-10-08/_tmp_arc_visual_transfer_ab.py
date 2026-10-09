from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import defaultdict,Counter
import numpy as np,hashlib,json
arc=Arcade(operation_mode=OperationMode.NORMAL)
def framehash(e):
 a=np.asarray(e._last_response.frame[-1],dtype=np.int16)
 return hashlib.sha1(a.tobytes()).hexdigest()[:16]
def run(game,mode,budget=80):
 e=arc.make(game);seen=set();edges=defaultdict(Counter);counts=Counter();transitions=[];changed=0;stale=0;failruns=0;prev=framehash(e)
 for t in range(budget):
  key=framehash(e);seen.add(key)
  if mode=='A':
   action=1
  else:
   # A/B at each visual referent: test least-tried action, avoid reusing a failed action.
   action=min((1,2,3,4),key=lambda a:(edges[key][a],counts[a],(a*7+t)%4))
  before=framehash(e)
  r=e.step(GameAction.from_id(action),data={})
  after=framehash(e);edges[before][action]+=1;counts[action]+=1
  changed+=int(before!=after)
  stale+=int(before==after)
  if r.levels_completed>len(transitions):transitions.append((t+1,r.levels_completed))
  seen.add(after)
  if r.state.name!='NOT_FINISHED':break
 return {'game':game,'policy':mode,'actions':sum(counts.values()),'action_histogram':dict(counts),'unique_frames':len(seen),'changed_frames':changed,'unchanged_frames':stale,'levels':r.levels_completed,'terminal_state':r.state.name,'transitions':transitions}
results=[]
for game in ('ls20','sk48'):
 for mode in ('A','B'):
  result=run(game,mode)
  results.append(result)
  print('TEST',json.dumps(result,sort_keys=True),flush=True)
