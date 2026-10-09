from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_recursive_partition import ab_fixed_point

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

def build(game,depth=5,cap=80):
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
    except Exception as ex:
     imm.append((z,"ERR",type(ex).__name__,None))
   nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children,"depth":dep}
  front=nxt[:cap]
 return nodes

def truncate(nodes,h):
 keep={p:n for p,n in nodes.items() if n["depth"]<h}
 out={}
 for p,n in keep.items():
  out[p]=dict(n)
  out[p]["children"]={z:cp for z,cp in n["children"].items() if cp in keep}
 return out

def same_equiv(c1,c2,paths):
 for i,p in enumerate(paths):
  for q in paths[i+1:]:
   if (c1[p]==c1[q])!=(c2[p]==c2[q]):return False,(p,q,c1[p],c1[q],c2[p],c2[q])
 return True,None

nodes=build("cd82",7,80)
n4=truncate(nodes,4);n5=truncate(nodes,5);n6=truncate(nodes,6);n7=truncate(nodes,7)
c4,h4=ab_fixed_point(n4);c5,h5=ab_fixed_point(n5);c6,h6=ab_fixed_point(n6);c7,h7=ab_fixed_point(n7)
print("H4",[len(p) for p in h4],"H5",[len(p) for p in h5],"H6",[len(p) for p in h6],"H7",[len(p) for p in h7])

for a,b,ca,cb,label in [(n4,n5,c4,c5,"4v5"),(n5,n6,c5,c6,"5v6"),(n6,n7,c6,c7,"6v7")]:
 for maxdepth in [0,1,2,3]:
  paths=sorted([p for p,n in a.items() if n["depth"]<=maxdepth])
  ok,w=same_equiv(ca,cb,paths)
  print(label,"INTERIOR_DEPTH",maxdepth,"N",len(paths),"SAME",ok,"WIT",w)
