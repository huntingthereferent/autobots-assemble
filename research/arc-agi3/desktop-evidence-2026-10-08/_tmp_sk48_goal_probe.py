from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
seqs=[(),(1,),(4,),(4,4),(1,1),(1,1,1),(4,4,1,1),(1,1,4,4),(4,4,4),(1,4,1,4),(4,4,1,1,1)]
for p in seqs:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 g=e._game
 body=[(s.x,s.y) for s in g.mwfajkguqx[g.vzvypfsnt]]
 pad=[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian]
 match=[(k.x,k.y,[(s.x,s.y,int(s.pixels[1,1])) for s in v]) for k,v in g.vjfbwggsd.items()]
 print('PATH',p,'BODY',body,'Q',g.qiercdohl,'PENDING',(len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno),'MATCH',match,'GOAL',g.gvtmoopqgy(),flush=True)
