from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np,math

A=[1,2,3,4,7]
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
def bar(q): return math.ceil(16*q/49)
def dist(q):
    b=bar(q); n=1
    while q-n>=0 and bar(q-n)==b:n+=1
    return n

arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("sk48")
nodes={};qs={};front=[((),root,"START")]
for dep in range(4):
    nxt=[]
    for p,e,o in front:
        qs[p]=e._game.qiercdohl
        im=[];ch={}
        for z in A:
            q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={});no=H(r)
            im.append((z,no,r.levels_completed,r.state.name))
            if r.state.name=="NOT_FINISHED":
                cp=p+(z,);ch[z]=cp
                if dep<3:nxt.append((cp,q,no))
        nodes[p]={"obs":o,"immediate":tuple(im),"children":ch}
    front=nxt

hs=horizon_signatures(nodes,A,3)
for k in [2,3]:
    valid=list(hs[k]);bad=[]
    for i,p in enumerate(valid):
        for q in valid[i+1:]:
            eh=(hs[k][p]==hs[k][q])
            ep=(hs[k-1][p]==hs[k-1][q] and min(dist(qs[p]),k+1)==min(dist(qs[q]),k+1))
            if eh!=ep: bad.append((p,q,eh,ep,qs[p],qs[q],dist(qs[p]),dist(qs[q])))
    print("K",k,"VALID",len(valid),"PAIR_MISMATCHES",len(bad))
    for x in bad[:20]:print(" BAD",x)
