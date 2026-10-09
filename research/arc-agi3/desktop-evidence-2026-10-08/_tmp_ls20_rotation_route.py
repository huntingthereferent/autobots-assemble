from arc_agi import Arcade,OperationMode
from arcengine import GameAction
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
path=(3,3,3,1,1,1,4,4,4,1,1,1,1)
for i,z in enumerate(path):
 r=e.step(GameAction.from_id(z),data={})
 g=e._game
 print(i+1,z,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'ROT',g.cklxociuu,'REMAIN',g._step_counter_ui.osgviligwp,'LEVEL',r.levels_completed,'STATE',r.state.name,flush=True)
 if r.levels_completed>0:break
