from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
from itertools import product
A=[1,2,3,4,7]
def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("sk48")
def make(path):
    e=copy.deepcopy(root)
    for z in path:e.step(GameAction.from_id(z),data={})
    return e
def sig(e,maxd):
    out=[]
    for d in range(maxd+1):
        for suf in product(A,repeat=d):
            q=copy.deepcopy(e); r=q._last_response
            for z in suf:r=q.step(GameAction.from_id(z),data={})
            out.append((suf,H(r),r.state.name,r.levels_completed))
    return tuple(out)

a=make((2,)); b=make((7,))
print("RAW",sig(a,3)==sig(b,3),"q",a._game.qiercdohl,b._game.qiercdohl,
      "ac",a._game._action_count,b._game._action_count)
qb=copy.deepcopy(b); qb._game.qiercdohl=a._game.qiercdohl
print("Q_ONLY",sig(a,3)==sig(qb,3))
if sig(a,3)!=sig(qb,3):
    for x,y in zip(sig(a,3),sig(qb,3)):
        if x!=y: print("FIRST_DIFF",x,y); break
