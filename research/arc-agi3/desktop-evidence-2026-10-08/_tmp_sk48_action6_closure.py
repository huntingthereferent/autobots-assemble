from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
from collections import Counter,defaultdict

A=[1,2,3,4,7]
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("sk48")
front=[((),root)]
stats=Counter(); active_patterns=Counter(); examples={}
for dep in range(5):
    nxt=[]
    for p,e in front:
        g=e._game
        pairs=list(g.xpmcmtbcv.items())
        stats[len(pairs)]+=1
        active=None
        for i,(a,b) in enumerate(pairs):
            if a is g.vzvypfsnt: active=("key",i)
            elif b is g.vzvypfsnt: active=("mate",i)
        active_patterns[(len(pairs),active)]+=1
        examples.setdefault((len(pairs),active),(p,copy.deepcopy(e)))
        if dep<4:
            for z in A:
                q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={})
                if r.state.name=="NOT_FINISHED":nxt.append((p+(z,),q))
    front=nxt
print("PAIR_COUNTS",stats)
print("ACTIVE_PATTERNS",active_patterns)

for key,(p,e) in examples.items():
    g=e._game; pairs=list(g.xpmcmtbcv.items())
    tests=[("miss",0,0)]
    for i,(a,b) in enumerate(pairs):
        tests.append((f"k{i}",int(a.x+2),int(a.y+2)))
        tests.append((f"m{i}",int(b.x+2),int(b.y+2)))
    outs=[]
    for name,x,y in tests:
        q=copy.deepcopy(e);r=q.step(GameAction.ACTION6,data={"x":x,"y":y})
        outs.append((name,H(r),getattr(q._game,"qiercdohl",None),
                     [(int(s.x),int(s.y)) for s in q._game.xpmcmtbcv.keys()],
                     (int(q._game.vzvypfsnt.x),int(q._game.vzvypfsnt.y))))
    print("EX",key,"PATH",p,"OUTS",outs)
