from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np
from collections import defaultdict
def H(r):return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
games=["g50t","ls20","re86","tr87","tu93","wa30"]
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in games:
 root=arc.make(name);ACTS=[getattr(x,"value",x) for x in root._last_response.available_actions]
 nodes={};front=[((),root,H(root._last_response))]
 for dep in range(3):
  nxt=[]
  for p,e,o in front:
   im=[];ch={}
   for a in ACTS:
    q=copy.deepcopy(e);r=q.step(GameAction.from_id(a),data={});no=H(r)
    im.append((a,no,r.levels_completed,r.state.name))
    if r.state.name=="NOT_FINISHED":
     cp=p+(a,);ch[a]=cp
     if dep<2:nxt.append((cp,q,no))
   nodes[p]={"obs":o,"immediate":tuple(im),"children":ch}
  front=nxt
 hs=horizon_signatures(nodes,ACTS,2)
 grow=[];byobs=defaultdict(list)
 for p in set(hs[2])&set(hs[1]):byobs[nodes[p]["obs"]].append(p)
 for obs,ps in byobs.items():
  prev=defaultdict(list)
  for p in ps:prev[repr(hs[1][p])].append(p)
  for members in prev.values():
   now=defaultdict(list)
   for p in members:now[repr(hs[2][p])].append(p)
   if len(now)>1:grow.append((obs,members,list(now.values())))
 cand=[];byobs=defaultdict(list)
 for p in hs[2]:
  if len(p)==1:byobs[nodes[p]["obs"]].append(p)
 for obs,ps in byobs.items():
  g=defaultdict(list)
  for p in ps:g[repr(hs[2][p])].append(p)
  for m in g.values():
   if len(m)>1:cand.append((obs,m))
 print("\nGAME",name,"ACTS",ACTS,"NODES",len(nodes),
       "H1VALID",len(hs[1]),"H2VALID",len(hs[2]),
       "GROW1TO2",len(grow),"H3CAND",len(cand))
 for x in grow[:20]:print(" G",x)
 for x in cand[:20]:print(" C",x)
