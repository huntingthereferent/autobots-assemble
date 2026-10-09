from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_family_closure import Occurrence
from ab_trace_machine import build_ab_model,summarize

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def build_game(game):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
 nodes=[(root,"START",(),())];occ=[]
 for depth in range(3):
  nxt=[]
  for env,obs,oh,ah in nodes:
   outs=[]
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
    except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
   rel=[]
   for i in range(1,4):
    rel += [(f"prev_obs{i}",oh[-i] if len(oh)>=i else None),(f"prev_action{i}",ah[-i] if len(ah)>=i else None)]
   occ.append(Occurrence(obs,tuple(rel),tuple(outs)))
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:r=q.step(GameAction.from_id(z),data={})
    except:continue
    if r.state.name=="NOT_FINISHED":nxt.append((q,fh(r),oh+(obs,),ah+(z,)))
  nodes=nxt[:80]
 return build_ab_model(occ)

for game in ["bp35","dc22"]:
 m=build_game(game)
 print(game.upper(),summarize(m))
 print(" SPLITS",[(r,s.retained_names) for r,s in m.states.items() if s.retained_names])
print("PASS collapse/one-relation controls through same A/B machine")
