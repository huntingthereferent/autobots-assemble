from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
for trial in (1,2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 for i,a in enumerate(p1+p2):
  r=e.step(GameAction.from_id(a),data={})
  if r.levels_completed and i+1 in (14,44):print('TRANSITION',trial,i+1,r.levels_completed,e._game._current_level_index,flush=True)
 g=e._game
 print('REPLAY',trial,'LEVEL',r.levels_completed,'INDEX',g._current_level_index,'STATE',r.state.name,'COUNTER',g.qiercdohl,'TOP',[(int(s.x),int(s.y),int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53],flush=True)
 print('TARGET',[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()],'ACTIVE',[(int(s.x),int(s.y)) for s in g.mwfajkguqx[g.vzvypfsnt]],flush=True)
