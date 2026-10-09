from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy,pickle
from collections import defaultdict
from ab_horizon_normalized import horizon_signatures

ACTIONS=[1,2,3,4,5]
TARGET="856913b32d2c"

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make("sk48")
nodes={};front=[((),root,"START")]
for dep in range(4):
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
   except Exception as ex:imm.append((z,"ERR",type(ex).__name__,None))
  nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children}
 front=nxt
hs=horizon_signatures(nodes,ACTIONS,3)

for k in [0,1,2,3]:
 valid=[p for p in hs[k] if nodes[p]["obs"]==TARGET]
 groups=defaultdict(list)
 for p in valid:groups[repr(hs[k][p])].append(p)
 print("H",k,"N",len(valid),"CLASSES",len(groups))
 for i,ps in enumerate(groups.values()):
  print(" C",i,ps)
  for p in ps:
   print("  PATH",p,"IMMEDIATE",nodes[p]["immediate"])

# For the two H3-valid occurrences, show H1/H2/H3 equality movement directly.
v3=[p for p in hs[3] if nodes[p]["obs"]==TARGET]
print("H3_VALID",v3)
if len(v3)>=2:
 p,q=v3[:2]
 for k in [0,1,2,3]:
  print("PAIR_H",k,hs[k].get(p)==hs[k].get(q))

with open(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_depth4_nodes.pkl","wb") as f:pickle.dump(nodes,f)
