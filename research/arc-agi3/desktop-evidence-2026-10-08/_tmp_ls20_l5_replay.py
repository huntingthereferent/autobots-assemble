from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,2,1,2,2,4,2,4,4,4,4,4,4,4,1)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 for z in p1+p2+p3+p4:e.step(GameAction.from_id(z),data={})
 for i,z in enumerate(p5,1):
  g=e._game;before=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps)
  r=e.step(GameAction.from_id(z),data={})
  g=e._game;after=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g.fwckfzsyc,g._step_counter_ui.current_steps)
  if i%5==0 or r.levels_completed>4 or g.aqygnziho<3:print('STEP',trial,i,z,before,after,'LEVEL',r.levels_completed,'LIVES',g.aqygnziho,flush=True)
  if r.levels_completed>4 or r.state.name!='NOT_FINISHED':break
 print('RESULT',trial,'LEVEL',r.levels_completed,'USED',i,'WIN',r.state.name,flush=True)
