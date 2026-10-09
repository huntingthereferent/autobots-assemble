from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict,Counter
from ab_family_closure import Occurrence,ab_family,project

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
root=a.make("cd82")
nodes=[(root,"START",(),())];occ=[]
for depth in range(4):
 nxt=[]
 for env,obs,oh,ah in nodes:
  outs=[]
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
   except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
  rel=[]
  for i in range(1,5):
   rel += [(f"prev_obs{i}",oh[-i] if len(oh)>=i else None),(f"prev_action{i}",ah[-i] if len(ah)>=i else None)]
  occ.append(Occurrence(obs,tuple(rel),tuple(outs)))
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={})
   except:continue
   if r.state.name=="NOT_FINISHED":nxt.append((q,fh(r),oh+(obs,),ah+(z,)))
 nodes=nxt[:120]

states=ab_family(occ)
table=defaultdict(set)
for o in occ:table[project(o,states[o.referent])].add(o.future)
assert all(len(v)==1 for v in table.values())
dist=Counter(s.retained_names for s in states.values())
print("WIT",len(occ),"RAW",len(states),"AB",len(table),"EXTRA",len(table)-len(states))
for rels,n in sorted(dist.items(),key=lambda kv:(len(kv[0]),kv[0])):
 print("SET",rels,"N",n)
joint=[(ref,s.retained_names) for ref,s in states.items() if len(s.retained_names)>1]
print("JOINT_N",len(joint))
for x in joint[:20]:print("JOINT",x)
assert any(rels==("prev_action1","prev_action2") for ref,rels in joint)
print("PASS cd82 real joint A/B closure")
