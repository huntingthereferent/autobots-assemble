from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import hashlib, numpy as np

names=["bp35","cd82","cn04","dc22","ft09","g50t","ka59","lf52","lp85","ls20","m0r0","r11l","re86","s5i5","sb26","sc25","sk48","sp80","su15","tn36","tr87","tu93","vc33","wa30"]
a=Arcade(operation_mode=OperationMode.NORMAL)

def norm(x):
    if isinstance(x,np.ndarray): return ("nd",x.shape,str(x.dtype),x.tobytes())
    if isinstance(x,(list,tuple)): return tuple(norm(v) for v in x)
    if isinstance(x,dict): return tuple(sorted((k,norm(v)) for k,v in x.items()))
    return x
def digest(frame):
    return hashlib.sha1(repr(norm(frame)).encode()).hexdigest()[:10]

for name in names:
    rows=[]
    for z in [1,2,3,4,5,7]:
        try:
            e=a.make(name)
            r=e.step(GameAction.from_id(z),data={})
            rows.append((z,digest(r.frame),str(r.state).split(".")[-1],r.levels_completed))
        except Exception as ex:
            rows.append((z,"ERR",type(ex).__name__,str(ex)[:30]))
    uniq=len({x[1] for x in rows if x[1]!="ERR"})
    print(name,"UNIQ",uniq,"ROWS",rows,flush=True)
