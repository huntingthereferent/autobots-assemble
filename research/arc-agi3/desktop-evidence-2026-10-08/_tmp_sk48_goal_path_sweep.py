from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
paths=[(4,)*n+((1,)*k) for n in range(3,8) for k in range(1,5)]
for p in paths:
 e=copy.deepcopy(root)
 for z in p:
  r=e.step(GameAction.from_id(z),data={})
 g=e._game
 body=[(s.x,s.y) for s in g.mwfajkguqx[g.vzvypfsnt]]
 pads=[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian]
 hits=[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()]
 print('PATH', ''.join(map(str,p)),'HEAD',body[0],'LEN',len(body),'TAIL',body[-1],'HITS',hits,'PADS',pads,'PHASE',(len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno),'LVL',g._current_level_index,flush=True)
