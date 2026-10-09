from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np,time
from collections import defaultdict

CS=[("M",(0,0)),("C1",(12,0)),("C2",(18,0)),("C3",(24,0)),("C4",(30,12)),("C5",(36,12)),("C6",(42,12)),("C7",(48,12))]
ACTS=[3,4,7]+[x[0] for x in CS]; D=dict(CS)
def do(e,a):
    if isinstance(a,int): return e.step(GameAction.from_id(a),data={})
    x,y=D[a]; return e.step(GameAction.ACTION6,data={"x":x,"y":y})
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("bp35")
rootobs=H(root._last_response);nodes={};paths=[()]
for dep in range(4):
    nxt=[];t=time.time()
    for p in paths:
        e=copy.deepcopy(root); r=e._last_response; ok=True
        for a in p:
            r=do(e,a)
            if r.state.name!="NOT_FINISHED":ok=False;break
        if not ok:continue
        o=rootobs if not p else H(r); im=[];ch={}
        for a in ACTS:
            q=copy.deepcopy(e); rr=do(q,a); no=H(rr)
            im.append((a,no,rr.levels_completed,rr.state.name))
            if rr.state.name=="NOT_FINISHED":
                cp=p+(a,);ch[a]=cp
                if dep<3:nxt.append(cp)
        nodes[p]={"obs":o,"immediate":tuple(im),"children":ch}
    print("DEP",dep,"NODES_TOTAL",len(nodes),"NEXT",len(nxt),"SEC",round(time.time()-t,2),flush=True)
    paths=nxt

hs=horizon_signatures(nodes,ACTS,3)
print("NODES",len(nodes))
for k in range(4):
    by=defaultdict(set)
    for p,s in hs[k].items():by[nodes[p]["obs"]].add(repr(s))
    print("H",k,"VALID",len(hs[k]),"OBS_SPLIT",sum(len(v)>1 for v in by.values()))
for k in [1,2,3]:
    grow=[];byobs=defaultdict(list)
    for p in set(hs[k])&set(hs[k-1]):byobs[nodes[p]["obs"]].append(p)
    for obs,ps in byobs.items():
        prev=defaultdict(list)
        for p in ps:prev[repr(hs[k-1][p])].append(p)
        for members in prev.values():
            now=defaultdict(list)
            for p in members:now[repr(hs[k][p])].append(p)
            if len(now)>1:grow.append((obs,members,list(now.values())))
    print("GROW",k-1,"->",k,"N",len(grow))
    for x in grow[:12]:print(" ",x)
