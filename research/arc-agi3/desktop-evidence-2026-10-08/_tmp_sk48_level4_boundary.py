from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in p1+p2+p3:e.step(GameAction.from_id(a),data={})
g=e._game
print('ACTIVE',g.vzvypfsnt.name,g.vzvypfsnt.x,g.vzvypfsnt.y,'PAIRS',len(g.xpmcmtbcv),flush=True)
for k,m in g.xpmcmtbcv.items():
 print('PAIR',k.name,(k.x,k.y),k.tags,'->',m.name,(m.x,m.y),m.tags,'HITS',[(int(t.pixels[1,1])) for t in g.vjfbwggsd[k]],[(int(t.pixels[1,1])) for t in g.vjfbwggsd[m]],flush=True)
print('BODIES',[(s.name,(s.x,s.y),len(body)) for s,body in g.mwfajkguqx.items()],flush=True)
for z in (1,2,3,4,6):
 q=copy.deepcopy(e)
 r=q.step(GameAction.from_id(z),data={'x':0,'y':0} if z==6 else {})
 h=q._game
 print('ACT',z,'ACTIVE',(h.vzvypfsnt.x,h.vzvypfsnt.y),'PAIRS',[(k.x,k.y,[int(t.pixels[1,1]) for t in h.vjfbwggsd[k]],[int(t.pixels[1,1]) for t in h.vjfbwggsd[m]]) for k,m in h.xpmcmtbcv.items()],'COUNTER',h.qiercdohl,'STATE',r.state.name,flush=True)
