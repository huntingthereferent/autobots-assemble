from arc_agi import Arcade,OperationMode
from arcengine import GameAction
P1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
P2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
P3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
P4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
P5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
for trial in (1,2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 previous=0;tr=[]
 for i,a in enumerate(P1+P2+P3+P4+P5):
  r=e.step(GameAction.from_id(a),data={})
  if r.levels_completed>previous:tr.append((i+1,r.levels_completed,e._game._current_level_index));previous=r.levels_completed
 g=e._game
 print('REPLAY',trial,'SEQLEN',len(P5),'TOTAL',len(P1+P2+P3+P4+P5),'TRANSITIONS',tr,'LEVEL',r.levels_completed,'IDX',g._current_level_index,'STATE',r.state.name,flush=True)
 print('CURRENT HITS',[[int(s.pixels[1,1]) for s in v] for v in g.vjfbwggsd.values()],'GEOM',[(s.x,s.y,len(g.mwfajkguqx[s])) for s in g.mwfajkguqx],'COUNTER',g.qiercdohl,flush=True)
