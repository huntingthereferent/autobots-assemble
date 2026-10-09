from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_recursive_partition import ab_fixed_point

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def build(game,depth=4,cap=40):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
 nodes={};front=[((),root,"START")]
 for dep in range(depth):
  nxt=[]
  for path,env,obs in front:
   immediate=[];children={}
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:
     r=q.step(GameAction.from_id(z),data={});no=fh(r)
     immediate.append((z,no,r.levels_completed,r.state.name))
     if r.state.name=="NOT_FINISHED":
      cp=path+(z,);children[z]=cp;nxt.append((cp,q,no))
    except Exception as ex:
     immediate.append((z,"ERR",type(ex).__name__,None))
   nodes[path]={"obs":obs,"immediate":tuple(immediate),"children":children}
  front=nxt[:cap]
 return nodes

for game in ["bp35","dc22","cd82","sk48"]:
 try:
  nodes=build(game)
  classes,h=ab_fixed_point(nodes)
  sizes=[len(p) for p in h]
  print(game.upper(),"NODES",len(nodes),"A/B_CLASSES",sizes,"ROUNDS",len(h)-1,flush=True)
 except Exception as ex:
  print(game.upper(),"FAIL",type(ex).__name__,str(ex)[:120],flush=True)
