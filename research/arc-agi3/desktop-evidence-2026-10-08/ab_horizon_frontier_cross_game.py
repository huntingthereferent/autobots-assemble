from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_recursive_partition import ab_fixed_point

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def build(game,depth=6,cap=60):
 a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
 nodes={};front=[((),root,"START")]
 for dep in range(depth):
  nxt=[]
  for path,env,obs in front:
   imm=[];children={}
   for z in [1,2,3,4,5]:
    q=copy.deepcopy(env)
    try:
     r=q.step(GameAction.from_id(z),data={});no=fh(r)
     imm.append((z,no,r.levels_completed,r.state.name))
     if r.state.name=="NOT_FINISHED":
      cp=path+(z,);children[z]=cp;nxt.append((cp,q,no))
    except Exception as ex:imm.append((z,"ERR",type(ex).__name__,None))
   nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children,"depth":dep}
  front=nxt[:cap]
 return nodes

def trunc(nodes,h):
 keep={p:n for p,n in nodes.items() if n["depth"]<h}
 return {p:{**n,"children":{z:cp for z,cp in n["children"].items() if cp in keep}} for p,n in keep.items()}

def first_diff(a,b,ca,cb):
 maxd=max(n["depth"] for n in a.values())
 for d in range(maxd+1):
  paths=[p for p,n in a.items() if n["depth"]<=d]
  for i,p in enumerate(paths):
   for q in paths[i+1:]:
    if (ca[p]==ca[q])!=(cb[p]==cb[q]):
     return d,(p,q)
 return None,None

for game in ["dc22","sk48"]:
 nodes=build(game)
 hs={}
 for h in [4,5,6]:
  n=trunc(nodes,h);cl,history=ab_fixed_point(n);hs[h]=(n,cl,[len(x) for x in history])
 print("\n",game.upper())
 for h in [4,5,6]:print("H",h,hs[h][2])
 for x,y in [(4,5),(5,6)]:
  d,w=first_diff(hs[x][0],hs[y][0],hs[x][1],hs[y][1])
  print(x,"v",y,"FIRST_DIFF_DEPTH",d,"WIT",w)
