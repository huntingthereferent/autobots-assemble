from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
g=root._game
pairs=list(g.xpmcmtbcv.items())
for k,m in g.xpmcmtbcv.items():
 print('PAIR',k.name,'UP',(k.x,k.y,k.rotation),'DOWN',(m.x,m.y,m.rotation),'UPBODY',[(x.x,x.y) for x in g.mwfajkguqx[k]],'DOWNBODY',[(x.x,x.y) for x in g.mwfajkguqx[m]],flush=True)
print('INITIAL_ACTIVE',(g.vzvypfsnt.name,g.vzvypfsnt.x,g.vzvypfsnt.y),flush=True)
for x,y in [(30,3),(31,4),(32,5),(36,55),(38,58),(8,28),(0,0)]:
 q=copy.deepcopy(root)
 r=q.step(GameAction.ACTION6,data={'x':x,'y':y})
 gg=q._game
 print('CLICK',x,y,'ACTIVE',(gg.vzvypfsnt.name,gg.vzvypfsnt.x,gg.vzvypfsnt.y),'SIGNAL',gg.xsoixcero,'Q',gg.qiercdohl,'STATE',r.state.name,flush=True)
