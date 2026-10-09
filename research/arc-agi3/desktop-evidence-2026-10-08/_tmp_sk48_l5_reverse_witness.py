from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
P1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4);P2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4);P3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4);P4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for z in P1+P2+P3+P4:root.step(GameAction.from_id(z),data={})
for p in [(),(3,),(3,3),(1,3),(1,4,3),(1,4,4,3)]:
 q=copy.deepcopy(root)
 for a in p:q.step(GameAction.from_id(a),data={})
 g=q._game
 print('PATH',p,'HEAD',(g.vzvypfsnt.x,g.vzvypfsnt.y),'BODY',[(s.x,s.y) for s in g.mwfajkguqx[g.vzvypfsnt]],'PADS',[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53],'PENDING',(len(g.ljprkjlji),len(g.pzzwlsmdt)),'COUNTER',g.qiercdohl,flush=True)
