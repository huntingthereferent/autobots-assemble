from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import product
import copy,collections

A=[1,2,3,4,7]
arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("sk48")
rows=collections.Counter(); bad=[]
for L in range(4):
    for p in product(A,repeat=L):
        e=copy.deepcopy(root); ok=True
        for z in p:
            r=e.step(GameAction.from_id(z),data={})
            if r.state.name!="NOT_FINISHED": ok=False; break
        if not ok: continue
        g=e._game; pairs=list(g.xpmcmtbcv.items())
        active=[]
        for i,(a,b) in enumerate(pairs):
            if a is g.vzvypfsnt: active.append(("key",i))
            if b is g.vzvypfsnt: active.append(("mate",i))
        rows[(len(pairs),tuple(active))]+=1
        if len(pairs)!=1 or tuple(active)!=(("key",0),):
            bad.append((p,len(pairs),active))
print("STATES",sum(rows.values()))
print("PATTERNS",rows)
print("BAD",len(bad),bad[:20])
