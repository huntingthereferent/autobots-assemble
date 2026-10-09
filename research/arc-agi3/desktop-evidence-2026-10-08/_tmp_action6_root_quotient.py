from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,collections,time

def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in ["bp35","dc22","cd82"]:
    root=arc.make(name); t=time.time()
    outs=collections.defaultdict(list)
    errs=collections.Counter()
    for y in range(64):
        for x in range(64):
            q=copy.deepcopy(root)
            try:
                r=q.step(GameAction.ACTION6,data={"x":x,"y":y})
                key=(H(r),r.state.name,r.levels_completed)
                outs[key].append((x,y))
            except Exception as e:
                errs[type(e).__name__]+=1
    print("\nGAME",name,"OUT_CLASSES",len(outs),"ERRORS",dict(errs),"SEC",round(time.time()-t,2))
    ss=sorted(outs.items(),key=lambda kv:-len(kv[1]))
    for i,(k,pts) in enumerate(ss[:20]):
        print(" C",i,"N",len(pts),"REP",pts[0],"KEY",k)
