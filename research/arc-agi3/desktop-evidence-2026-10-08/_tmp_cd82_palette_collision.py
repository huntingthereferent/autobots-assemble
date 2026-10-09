from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
def H(r): return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12],r.state.name,r.levels_completed)
arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("cd82")
def hit(xy):
    q=copy.deepcopy(root);r=q.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]});return q,r
a,ra=hit((37,4));b,rb=hit((43,4))
print("ROOT_PUBLIC",H(ra),H(rb),H(ra)==H(rb))
dif=[]
for k in sorted(set(vars(a._game))|set(vars(b._game))):
    x=vars(a._game).get(k);y=vars(b._game).get(k)
    if isinstance(x,(int,float,bool,str,type(None))) and isinstance(y,(int,float,bool,str,type(None))) and x!=y:dif.append((k,x,y))
print("SCALAR_DIFF",dif)
acts=[("S1",1,None),("S2",2,None),("S3",3,None),("S4",4,None),("S5",5,None),
      ("CM",6,(0,0)),("CP0",6,(37,4)),("CP1",6,(43,4))]
for lab,z,xy in acts:
    qa,qb=copy.deepcopy(a),copy.deepcopy(b)
    if z==6:
        x,y=xy;xa=qa.step(GameAction.ACTION6,data={"x":x,"y":y});xb=qb.step(GameAction.ACTION6,data={"x":x,"y":y})
    else:
        xa=qa.step(GameAction.from_id(z),data={});xb=qb.step(GameAction.from_id(z),data={})
    print(lab,H(xa)==H(xb),H(xa),H(xb))
