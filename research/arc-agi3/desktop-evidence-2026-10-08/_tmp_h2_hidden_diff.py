from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from ab_horizon_normalized import horizon_signatures
import copy,hashlib,numpy as np
from collections import defaultdict

A=[1,2,3,4,7]
def H(r):
    return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

arc=Arcade(operation_mode=OperationMode.NORMAL)
root=arc.make("sk48")
nodes={}; envs={}; front=[((),root,"START")]
for dep in range(4):
    nxt=[]
    for p,e,o in front:
        envs[p]=copy.deepcopy(e)
        im=[]; ch={}
        for z in A:
            q=copy.deepcopy(e); r=q.step(GameAction.from_id(z),data={}); no=H(r)
            im.append((z,no,r.levels_completed,r.state.name))
            if r.state.name=="NOT_FINISHED":
                cp=p+(z,); ch[z]=cp
                if dep<3:nxt.append((cp,q,no))
        nodes[p]={"obs":o,"immediate":tuple(im),"children":ch}
    front=nxt

hs=horizon_signatures(nodes,A,3)
byobs=defaultdict(list)
for p in hs[2]:
    byobs[nodes[p]["obs"]].append(p)

for obs,ps in byobs.items():
    h1=defaultdict(list); h2=defaultdict(list)
    for p in ps:
        h1[repr(hs[1][p])].append(p)
        h2[repr(hs[2][p])].append(p)
    if len(h2)<=len(h1): continue
    print("\nOBS",obs,"H1",len(h1),"H2",len(h2))
    for members in h1.values():
        subs=defaultdict(list)
        for p in members: subs[repr(hs[2][p])].append(p)
        if len(subs)<=1: continue
        print(" SPLIT_H1",members)
        groups=list(subs.values())
        for i,g in enumerate(groups): print("  H2C",i,g)
        reps=[g[0] for g in groups]
        for i in range(len(reps)):
            for j in range(i+1,len(reps)):
                p,q=reps[i],reps[j]
                a=envs[p]._game; b=envs[q]._game
                print("  PAIR",p,q)
                dif=[]
                for k in sorted(set(vars(a))|set(vars(b))):
                    va=vars(a).get(k); vb=vars(b).get(k)
                    if isinstance(va,(int,float,bool,str,type(None))) and isinstance(vb,(int,float,bool,str,type(None))):
                        if va!=vb:dif.append(("SCALAR",k,va,vb))
                    elif isinstance(va,(list,tuple,set,dict)) and isinstance(vb,type(va)):
                        try:
                            if len(va)!=len(vb): dif.append(("LEN",k,len(va),len(vb)))
                        except: pass
                print("   DIFFS",dif)
