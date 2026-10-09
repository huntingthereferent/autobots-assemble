from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
for trial in range(2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 for i,a in enumerate(p):
  r=e.step(GameAction.from_id(a),data={})
  if r.levels_completed>0:print('TRANSITION',trial,'STEP',i+1,'ACTION',a,'LEVELS',r.levels_completed,'IDX',e._game._current_level_index,flush=True)
 g=e._game
 print('REPLAY',trial,'LEVEL',r.levels_completed,'INDEX',g._current_level_index,'STATE',r.state.name,'COUNTER',g.qiercdohl,'ACTIVE',[(int(s.x),int(s.y)) for s in g.mwfajkguqx[g.vzvypfsnt]],'TARGET',[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()],'PADS',[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian],flush=True)
