from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
from itertools import product

A=[1,2,3,4,7]
PAIRS=[
 ("O1",(1,),(2,1)),
 ("O2",(2,),(2,2)),
 ("O3",(3,),(2,3)),
 ("O4",(4,),(2,4)),
]
def H(r):
    return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("sk48")
def make(path):
    e=copy.deepcopy(root); r=None
    for z in path:r=e.step(GameAction.from_id(z),data={})
    return e

def sig(e,maxd=2):
    out=[]
    for d in range(maxd+1):
        for suf in product(A,repeat=d):
            q=copy.deepcopy(e); r=q._last_response
            ok=True
            for z in suf:
                try:r=q.step(GameAction.from_id(z),data={})
                except Exception as ex:
                    out.append((suf,"ERR",type(ex).__name__)); ok=False; break
            if ok: out.append((suf,H(r),r.state.name,r.levels_completed))
    return tuple(out)

for name,pa,pb in PAIRS:
    ea=make(pa); eb=make(pb)
    raw=sig(ea)==sig(eb)

    qb=copy.deepcopy(eb)
    qb._game.qiercdohl=ea._game.qiercdohl
    qonly=sig(ea)==sig(qb)

    ab=copy.deepcopy(eb)
    ab._game._action_count=ea._game._action_count
    acount=sig(ea)==sig(ab)

    both=copy.deepcopy(eb)
    both._game.qiercdohl=ea._game.qiercdohl
    both._game._action_count=ea._game._action_count
    bothok=sig(ea)==sig(both)

    print(name,"RAW",raw,"Q_ONLY",qonly,"ACTION_COUNT_ONLY",acount,"BOTH",bothok,
          "q",ea._game.qiercdohl,eb._game.qiercdohl,
          "ac",ea._game._action_count,eb._game._action_count)

    if not qonly:
        sa,sb=sig(ea),sig(qb)
        for x,y in zip(sa,sb):
            if x!=y:
                print(" Q_FIRST_DIFF",x,y);break
