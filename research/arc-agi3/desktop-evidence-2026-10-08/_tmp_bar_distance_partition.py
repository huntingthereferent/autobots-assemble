from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np,math
from collections import defaultdict

A=[1,2,3,4,7]
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
def bar(q): return math.ceil(16*q/49)
def dist(q):
    b=bar(q)
    n=1
    while q-n>=0 and bar(q-n)==b:n+=1
    return n

arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("sk48")
nodes={}; qs={}; front=[((),root,"START")]
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
    valid=list(hs[k])
    # Compare equivalence relations: Hk versus (H{k-1}, distance-to-next-bar-drop)
    bad=[]
    for i,p in enumerate(valid):
        for q in valid[i+1:]:
            eq_h = hs[k][p]==hs[k][q]
            eq_d = (hs[k-1][p]==hs[k-1][q] and dist(qs[p])==dist(qs[q]))
            if eq_h!=eq_d:
                bad.append((p,q,eq_h,eq_d,nodes[p]["obs"],nodes[q]["obs"],qs[p],qs[q],dist(qs[p]),dist(qs[q])))
    print("H",k,"VALID",len(valid),"BAD",len(bad))
    for x in bad[:20]: print(" BAD",x)

print("DISTINCT_Q_BAR_DIST")
seen={}
coll=[]
for q in range(1,197):
    key=(bar(q),dist(q))
    if key in seen: coll.append((seen[key],q,key))
    else: seen[key]=q
print("pairs",len(seen),"collisions",len(coll))
print("TOP",[(q,bar(q),dist(q)) for q in range(196,188,-1)])
