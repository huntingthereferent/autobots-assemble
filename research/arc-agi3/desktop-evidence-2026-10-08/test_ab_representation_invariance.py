from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_recursive_partition import ab_fixed_point,partition

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

# Real CD82 depth-4 tree.
a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make("cd82")
nodes={};front=[((),root,"START")]
for dep in range(4):
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
  nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children}
 front=nxt[:40]

c1,h1=ab_fixed_point(nodes)
p1=partition(c1)

# Consistent bijective renaming.
action_map={1:4,2:5,3:1,4:2,5:3}
obs_values=sorted({n["obs"] for n in nodes.values()}|{x[1] for n in nodes.values() for x in n["immediate"]})
obs_map={o:f"Q{i}" for i,o in enumerate(obs_values)}

ren={}
for path,n in nodes.items():
 imm=[]
 for z,no,lc,st in n["immediate"]:
  imm.append((action_map.get(z,z),obs_map.get(no,no),lc,st))
 children={action_map.get(z,z):cp for z,cp in n["children"].items()}
 ren[path]={"obs":obs_map.get(n["obs"],n["obs"]),"immediate":tuple(sorted(imm)),"children":children}

c2,h2=ab_fixed_point(ren)
p2=partition(c2)

print("ORIGINAL",[len(x) for x in h1])
print("RENAMED",[len(x) for x in h2])
print("SAME_FINAL_PARTITION",p1==p2)
assert p1==p2
print("PASS A/B invariant under consistent action/observation renaming")
