from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
def make(path):
 e=copy.deepcopy(root)
 for z in path:e.step(GameAction.from_id(z),data={})
 return e
a,b=make((1,2)),make((2,1))
for name,e in [('12',a),('21',b)]:
 g=e._game
 print('STATE',name,'counter',g.qiercdohl,'action_count',g._action_count,flush=True)
 for k,v in vars(g).items():
  if isinstance(v,(bool,int,float,str,type(None),tuple)):
   print('SCALAR',k,repr(v)[:160],flush=True)
 print('ACTIVE',g.vzvypfsnt.x,g.vzvypfsnt.y,g.vzvypfsnt.rotation,flush=True)
 print('PAIR',[(x.x,x.y,x.rotation,y.x,y.y,y.rotation) for x,y in g.xpmcmtbcv.items()],flush=True)
 print('BODY',[(x.x,x.y,x.rotation) for x in g.mwfajkguqx[g.vzvypfsnt]],flush=True)
