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
nodes=[(root,"START",(),())]
occ=[]
for depth in range(5):
 nxt=[]
 for env,obs,oh,ah in nodes:
  outs=[]
  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
   except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
  rel=[]
  for i in range(1,5):
   rel.append((f"prev_obs{i}",oh[-i] if len(oh)>=i else None))
   rel.append((f"prev_action{i}",ah[-i] if len(ah)>=i else None))
  occ.append(Occurrence(obs,tuple(rel),tuple(outs)))

  for z in [1,2,3,4,5]:
   q=copy.deepcopy(env)
   try:r=q.step(GameAction.from_id(z),data={})
   except:continue
   if r.state.name=="NOT_FINISHED":
    no=fh(r);nxt.append((q,no,oh+(obs,),ah+(z,)))
 nodes=nxt[:180]

states=ab_family(occ)
table=defaultdict(set)
for o in occ:
 s=states[o.referent]
 table[project(o,s)].add(o.future)
bad={k:v for k,v in table.items() if len(v)>1}
assert not bad,bad

dist=Counter(s.retained_names for s in states.values())
print("WITNESSES",len(occ),"RAW_REFERENTS",len(states),"AB_STATES",len(table),"EXTRA",len(table)-len(states))
print("RELATION_SET_COUNTS")
for k,v in sorted(dist.items(),key=lambda kv:(len(kv[0]),kv[0])):print(" ",k,":",v)

split={ref:s for ref,s in states.items() if s.retained_names}
print("SPLIT_REFERENTS",len(split))
for ref,s in sorted(split.items(),key=lambda kv:(len(kv[1].retained_names),kv[0])):
 print(" ",ref,"=>",s.retained_names)

# Explicitly ensure at least one real joint relation set exists.
joint=[(ref,s) for ref,s in split.items() if len(s.retained_names)>1]
print("JOINT",len(joint))
for ref,s in joint[:10]:print(" ",ref,s.retained_names)
assert joint
print("PASS cd82 generic A/B predictive table with real joint relation closure")
