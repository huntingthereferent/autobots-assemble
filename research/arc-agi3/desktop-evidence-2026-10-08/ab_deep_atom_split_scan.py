from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict
from ab_family_all_minima import Occurrence,ab_family_all

GAMES=["dc22","cd82","sk48"]

def fh(r):
    if not getattr(r,"frame",None): return "EMPTY"
    try:return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
    except:return hashlib.sha1(repr(r.frame).encode()).hexdigest()[:12]

def scan(game,depth=5,cap=40):
    a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make(game)
    nodes=[(root,"START",(),())];occ=[]
    for dep in range(depth):
        nxt=[]
        for env,obs,oh,ah in nodes:
            outs=[]
            for z in [1,2,3,4,5]:
                q=copy.deepcopy(env)
                try:r=q.step(GameAction.from_id(z),data={});outs.append((z,fh(r),r.levels_completed,r.state.name))
                except Exception as ex:outs.append((z,"ERR",type(ex).__name__,None))
            rel=[]
            for i in range(1,6):
                rel += [(f"prev_obs{i}",oh[-i] if len(oh)>=i else None),
                        (f"prev_action{i}",ah[-i] if len(ah)>=i else None)]
            occ.append(Occurrence(obs,tuple(rel),tuple(outs)))
            for z in [1,2,3,4,5]:
                q=copy.deepcopy(env)
                try:r=q.step(GameAction.from_id(z),data={})
                except:continue
                if r.state.name=="NOT_FINISHED":
                    nxt.append((q,fh(r),oh+(obs,),ah+(z,)))
        nodes=nxt[:cap]
        print(game,"DEPTH",dep+1,"NODES",len(nodes),"OCC",len(occ),flush=True)
    st=ab_family_all(occ)
    fams=defaultdict(int)
    for s in st.values():
        if s.minimal_separator_sets!=((),):
            fams[s.minimal_separator_sets]+=1
    print(game,"RAW",len(st),"SPLIT",sum(fams.values()),flush=True)
    for fam,n in sorted(fams.items(),key=lambda kv:repr(kv[0])):
        print("FAM",fam,"N",n,flush=True)
    return st

for g in GAMES:
    try:scan(g)
    except Exception as ex:
        print(g,"FAIL",type(ex).__name__,str(ex)[:200],flush=True)
