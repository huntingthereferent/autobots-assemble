from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p=(3,3,3,1,1,1,1,4,4,4,1,1,1)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 checkpoints=[]
 for i,z in enumerate(p,1):
  r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>0:checkpoints.append((i,r.levels_completed))
 g=e._game
 print('TRIAL',trial,'CHECKPOINTS',checkpoints,'LEVELS',r.levels_completed,'STATE',r.state.name,'ACTION_COUNT',len(p),'NEXT_START',(g.gudziatsk.x,g.gudziatsk.y),'NEXT_GOALS',[(x.x,x.y) for x in g.plrpelhym],'NEXT_TARGETS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),flush=True)
