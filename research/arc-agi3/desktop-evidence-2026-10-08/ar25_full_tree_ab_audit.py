from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_recursive_partition import ab_fixed_point

ACTIONS=[1,2,3,4,5,7]

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make("ar25")
nodes={};front=[((),root,"START")]
DEPTH=4
for dep in range(DEPTH):
 nxt=[]
 for path,env,obs in front:
  imm=[];children={}
  for z in ACTIONS:
   q=copy.deepcopy(env)
   try:
    r=q.step(GameAction.from_id(z),data={});no=fh(r)
    imm.append((z,no,r.levels_completed,r.state.name))
    if r.state.name=="NOT_FINISHED":
     cp=path+(z,);children[z]=cp;nxt.append((cp,q,no))
   except Exception as ex:
    imm.append((z,"ERR",type(ex).__name__,None))
  nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children}
 front=nxt
 print("DEP",dep+1,"NEXT",len(front),"NODES",len(nodes),flush=True)

classes,h=ab_fixed_point(nodes)
print("A/B",[len(p) for p in h])

raw=defaultdict(set)
members=defaultdict(list)
for p,n in nodes.items():
 raw[n["obs"]].add(classes[p]);members[n["obs"]].append(p)
split={o:s for o,s in raw.items() if len(s)>1}
print("RAW",len(raw),"SPLIT",len(split))

causes=defaultdict(int)
for obs,s in split.items():
 ms=members[obs];vary=[]
 for z in ACTIONS:
  vals={next(t for t in nodes[p]["immediate"] if t[0]==z)[1:] for p in ms}
  if len(vals)>1:vary.append(z)
 causes[tuple(vary)]+=1
 print("SPLIT",obs,"AB",len(s),"VARY",vary,"N",len(ms))
print("CAUSES",dict(causes))

target=max(split,key=lambda o:len(split[o])) if split else None
if target:
 ms=members[target]
 a7=defaultdict(list)
 for p in ms:
  out=next(t for t in nodes[p]["immediate"] if t[0]==7)[1:]
  a7[out].append(p)
 bp=defaultdict(list)
 for p in ms:bp[classes[p]].append(p)
 pab=frozenset(frozenset(v) for v in bp.values())
 p7=frozenset(frozenset(v) for v in a7.values())
 print("TARGET",target,"AB",len(bp),"A7",len(a7),"MATCH",pab==p7)
# Equal-horizon A/B audit: never compare occurrences with unequal remaining evidence.
from ab_horizon_normalized import horizon_signatures
hs=horizon_signatures(nodes,ACTIONS,4)
print("HORIZON_NORMALIZED")
for k,valid in hs.items():
 groups=defaultdict(set)
 counts=defaultdict(int)
 for p,sig in valid.items():
  obs=nodes[p]["obs"];groups[obs].add(sig);counts[obs]+=1
 splitk={o:v for o,v in groups.items() if len(v)>1}
 targetk=len(groups.get("1f013c964a65",set()))
 print(" H",k,"VALID",len(valid),"SPLIT_OBS",len(splitk),"TARGET_CLASSES",targetk,
       "TARGET_N",counts.get("1f013c964a65",0))

import pickle
with open(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_full_tree_nodes.pkl","wb") as f:
 pickle.dump(nodes,f)

print("PASS prefix-complete AR25 A/B audit")
