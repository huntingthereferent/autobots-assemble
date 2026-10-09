from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
for trial in (1,2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 transitions=[]
 for i,a in enumerate(p1+p2+p3):
  r=e.step(GameAction.from_id(a),data={})
  if r.levels_completed>len(transitions):transitions.append((i+1,r.levels_completed,e._game._current_level_index))
 g=e._game
 print('REPLAY',trial,'TRANSITIONS',transitions,'LEVELS_COMPLETED',r.levels_completed,'IDX',g._current_level_index,'STATE',r.state.name,'ACTION_COUNT',len(p1+p2+p3),'BODYCOUNT',len(g.mwfajkguqx),'TARGET',[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()],'PAD',[(s.x,s.y,int(s.pixels[1,1])) for s in g.vbelzuaian if s.y<53],flush=True)
