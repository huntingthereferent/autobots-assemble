from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,time

def H(r): return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12],r.state.name,r.levels_completed)
arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("cd82")
def branch(kind):
    q=copy.deepcopy(root)
    if kind=="C0": q.step(GameAction.ACTION6,data={"x":0,"y":0})
    else: q.step(GameAction.from_id(int(kind[1:])),data={})
    return q

pairs=[("S1","S2"),("S1","S5"),("S1","C0"),("S5","C0")]
for a,b in pairs:
    ea,eb=branch(a),branch(b); t=time.time(); found=None
    for z in [1,2,3,4,5]:
        qa,qb=copy.deepcopy(ea),copy.deepcopy(eb)
        ra=qa.step(GameAction.from_id(z),data={}); rb=qb.step(GameAction.from_id(z),data={})
        if H(ra)!=H(rb): found=("S",z,H(ra),H(rb)); break
    checked=0
    if found is None:
        for y in range(64):
            for x in range(64):
                qa,qb=copy.deepcopy(ea),copy.deepcopy(eb)
                ra=qa.step(GameAction.ACTION6,data={"x":x,"y":y}); rb=qb.step(GameAction.ACTION6,data={"x":x,"y":y})
                checked+=1
                if H(ra)!=H(rb):
                    found=("C",(x,y),H(ra),H(rb)); break
            if found is not None: break
    print(a,b,"FOUND",found,"C_CHECKED",checked,"SEC",round(time.time()-t,2))
