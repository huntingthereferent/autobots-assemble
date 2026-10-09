from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np,time
from collections import defaultdict
ACTS=[1,2,3,4,"M","A","B"];XY={"M":(0,0),"A":(45,17),"B":(45,34)}
def do(e,a):
 if isinstance(a,int):return e.step(GameAction.from_id(a),data={})
 x,y=XY[a];return e.step(GameAction.ACTION6,data={"x":x,"y":y})
def H(r):return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("dc22")
nodes={};front=[((),root,H(root._last_response))]
for dep in range(3):
 nxt=[];t=time.time()
 for p,e,o in front:
  im=[];ch={}
  for a in ACTS:
   q=copy.deepcopy(e);r=do(q,a);no=H(r)
   im.append((a,no,r.levels_completed,r.state.name))
   if r.state.name=="NOT_FINISHED":
    cp=p+(a,);ch[a]=cp
    if dep<2:nxt.append((cp,q,no))
  nodes[p]={"obs":o,"immediate":tuple(im),"children":ch}
 print("DEP",dep,"TOTAL",len(nodes),"NEXT",len(nxt),"SEC",round(time.time()-t,2))
 front=nxt
hs=horizon_signatures(nodes,ACTS,2)
for k in range(3):
 by=defaultdict(set)
 for p,s in hs[k].items():by[nodes[p]["obs"]].add(repr(s))
 print("H",k,"VALID",len(hs[k]),"OBS_SPLIT",sum(len(v)>1 for v in by.values()))
grow=[];byobs=defaultdict(list)
for p in set(hs[2])&set(hs[1]):byobs[nodes[p]["obs"]].append(p)
for obs,ps in byobs.items():
 prev=defaultdict(list)
 for p in ps:prev[repr(hs[1][p])].append(p)
 for members in prev.values():
  now=defaultdict(list)
  for p in members:now[repr(hs[2][p])].append(p)
  if len(now)>1:grow.append((obs,members,list(now.values())))
print("GROW1TO2",len(grow))
for x in grow:print(" G",x)
cand=[];byobs=defaultdict(list)
for p in hs[2]:
 if len(p)==1:byobs[nodes[p]["obs"]].append(p)
for obs,ps in byobs.items():
 g=defaultdict(list)
 for p in ps:g[repr(hs[2][p])].append(p)
 for m in g.values():
  if len(m)>1:cand.append((obs,m))
print("H3_CANDIDATE_GROUPS",len(cand))
for x in cand:print(" CAND",x)
