from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_closure import Occurrence,ab_family

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
root=a.make("cd82")
nodes=[(root,"START",(),())]
raw=[]
for depth in range(4):
 nxt=[]
 for env,obs,oh,ah in nodes:
  outs=[]
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
   except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
  raw.append((obs,tuple(outs),oh,ah))
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={})
   except:continue
   if r.state.name=="NOT_FINISHED":
    no=fh(r);nxt.append((q,no,oh+(obs,),ah+(z,)))
 nodes=nxt[:120]

target="be775c83b8f0"
hits=[x for x in raw if x[0]==target]
print("TARGET_HITS",len(hits))
for j,(obs,fut,oh,ah) in enumerate(hits):
 print("HIT",j,"OH",oh,"AH",ah,"FUT",fut)

# Try successive evidence sets through the SAME A/B kernel.
for mode in ["obs","actions","both"]:
 occ=[]
 for obs,fut,oh,ah in raw:
  rel=[]
  if mode in ("obs","both"):
   for i in range(1,5):rel.append((f"prev_obs{i}",oh[-i] if len(oh)>=i else None))
  if mode in ("actions","both"):
   for i in range(1,5):rel.append((f"prev_action{i}",ah[-i] if len(ah)>=i else None))
  occ.append(Occurrence(obs,tuple(rel),fut))
 try:
  states=ab_family(occ)
  s=states[target]
  print("MODE",mode,"TARGET_RETAINED",s.retained_names)
 except Exception as ex:
  print("MODE",mode,"FAIL",type(ex).__name__,str(ex))
