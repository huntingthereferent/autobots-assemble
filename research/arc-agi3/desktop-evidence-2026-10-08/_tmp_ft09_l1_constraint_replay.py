from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p=((36,36),(36,44),(36,52),(52,44))
for k in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ft09')
 for i,(x,y) in enumerate(p,1):
  r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
  print('TRIAL',k,'STEP',i,'XY',(x,y),'LEVEL',r.levels_completed,'STATE',r.state.name,'BUDGET',e._game.lpw.dzy,flush=True)
 print('RESULT',k,r.levels_completed,r.state.name,'LEVEL_INDEX',e._game.level_index,flush=True)
