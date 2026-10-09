from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in p1+p2+p3+p4:e.step(GameAction.from_id(a),data={})
paths=[(),(2,),(4,),(1,),(1,4,4),(2,3,4,4,4,2,4,1,3,3,3,1,1,4,4,4,4)]
for p in paths:
 q=copy.deepcopy(e)
 for a in p:q.step(GameAction.from_id(a),data={})
 g=q._game
 print('PATH',p,'Q',g.qiercdohl,'ACTIVE',g.vzvypfsnt.x,g.vzvypfsnt.y,'BODY',[(s.x,s.y,s.rotation) for s in g.mwfajkguqx[g.vzvypfsnt]],'UPPER',sorted([(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53]),'BOTTOM',[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y>=53],'HITS',[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()],'PENDING',(len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno),flush=True)
