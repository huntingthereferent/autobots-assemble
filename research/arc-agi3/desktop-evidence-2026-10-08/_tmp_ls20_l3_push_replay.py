from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 for z in p1+p2:e.step(GameAction.from_id(z),data={})
 pickups=[];events=[];before_p=len(e._game.current_level.get_sprites_by_tag('npxgalaybz'))
 for i,z in enumerate(p3,1):
  g=e._game;pos=(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g._step_counter_ui.current_steps,g.aqygnziho)
  r=e.step(GameAction.from_id(z),data={})
  g=e._game;cnt=len(g.current_level.get_sprites_by_tag('npxgalaybz'))
  if cnt<before_p:pickups.append((i,g.gudziatsk.x,g.gudziatsk.y));before_p=cnt
  if i%10==0 or g.aqygnziho<3 or r.levels_completed>2:
   print('STEP',trial,i,'ACT',z,'FROM',pos,'TO',(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g.hiaauhahz,g._step_counter_ui.current_steps,g.aqygnziho),'LEVEL',r.levels_completed,'STATE',r.state.name,flush=True)
  if r.levels_completed>2 or r.state.name!='NOT_FINISHED':break
 print('RESULT',trial,'LEVEL',r.levels_completed,'USED',i,'PICKUPS',pickups,'STATE',r.state.name,flush=True)
