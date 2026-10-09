from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
def H(r): return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12],r.state.name,r.levels_completed)
arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("cd82")
def act(xy):
 q=copy.deepcopy(root);r=q.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]});return q,r
a,ra=act((0,0));b,rb=act((43,4))
print("PUBLIC",H(ra),H(rb),H(ra)==H(rb))
dif=[]
for k in sorted(set(vars(a._game))|set(vars(b._game))):
 x=vars(a._game).get(k);y=vars(b._game).get(k)
 if isinstance(x,(int,float,bool,str,type(None))) and isinstance(y,(int,float,bool,str,type(None))) and x!=y:dif.append((k,x,y))
print("SCALAR",dif)
for lab,z,dat in [("S1",1,None),("S2",2,None),("S3",3,None),("S4",4,None),("S5",5,None),("MISS",6,(0,0)),("P0",6,(37,4)),("P1",6,(43,4))]:
 qa,qb=copy.deepcopy(a),copy.deepcopy(b)
 if z==6:
  ra2=qa.step(GameAction.ACTION6,data={"x":dat[0],"y":dat[1]});rb2=qb.step(GameAction.ACTION6,data={"x":dat[0],"y":dat[1]})
 else:
  ra2=qa.step(GameAction.from_id(z),data={});rb2=qb.step(GameAction.from_id(z),data={})
 print(lab,H(ra2)==H(rb2),H(ra2),H(rb2))
