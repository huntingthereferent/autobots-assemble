from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
p6=(1,1,2,1,2,4,4,1,4,1,1,1,3,3,4,4,1,1,4,4,1,1,4,2,2,1,1,3,1,2,3,3,3,3,1,2,3,3,2,2,2,2,1,4,4,4,3,3,3,1,1,1,1,1,1,4,4,4,4,4,4,2,4,4,1,1,4,2,2,2,2,2)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 checkpoints=[];old=0
 for z in p1+p2+p3+p4+p5:
  r=e.step(GameAction.from_id(z),data={})
 for i,z in enumerate(p6,1):
  r=e.step(GameAction.from_id(z),data={})
  g=e._game
  goals=sum(g.lvrnuajbl)
  if goals>old:checkpoints.append((i,goals,g.gudziatsk.x,g.gudziatsk.y));old=goals
  if i%10==0 or r.levels_completed>=6 or g.aqygnziho<3:
   print('STATE',trial,i,'LV',r.levels_completed,'ATTR',(g.cklxociuu,g.hiaauhahz,g.fwckfzsyc),'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'LEFT',g._step_counter_ui.current_steps,'GOALS',g.lvrnuajbl,'LIVES',g.aqygnziho,flush=True)
  if r.levels_completed>=6 or r.state.name!='NOT_FINISHED':break
 print('RESULT',trial,'LEVEL',r.levels_completed,'ACTIONS_USED',i,'VISITED',checkpoints,'STATE',r.state.name,flush=True)
