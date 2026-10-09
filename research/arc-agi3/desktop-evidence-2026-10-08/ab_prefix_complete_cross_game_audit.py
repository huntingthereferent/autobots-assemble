from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_horizon_normalized import horizon_signatures

ACTIONS=[1,2,3,4,5]

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def build(game,depth=4):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
 nodes={};front=[((),root,"START")]
 for dep in range(depth):
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
  print(game,"DEP",dep+1,"NEXT",len(front),"NODES",len(nodes),flush=True)
 return nodes

def growth(nodes,maxh=3):
 hs=horizon_signatures(nodes,ACTIONS,maxh)
 for k in range(1,maxh+1):
  valid=hs[k]
  groups=defaultdict(list)
  for p in valid:groups[nodes[p]["obs"]].append(p)
  split=sum(1 for obs,ps in groups.items() if len({hs[k][p] for p in ps})>1)
  print(" H",k,"VALID",len(valid),"SPLIT",split)
  if k>=2:
   grow=[]
   for obs,ps in groups.items():
    c0=len({hs[k-1][p] for p in ps})
    c1=len({hs[k][p] for p in ps})
    if c1>c0:grow.append((obs,c0,c1,len(ps)))
   print("  GROWTH_FROM",k-1,"TO",k,len(grow),grow[:12])

for game in ["dc22","cd82","sk48"]:
 print("\nGAME",game)
 nodes=build(game)
 growth(nodes,3)
