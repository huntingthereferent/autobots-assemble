from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 for z in p1+p2+p3:e.step(GameAction.from_id(z),data={})
 cp=[];lost=[];ref=[]
 oldcol=len(e._game.current_level.get_sprites_by_tag('npxgalaybz'))
 for i,z in enumerate(p4,1):
  r=e.step(GameAction.from_id(z),data={})
  g=e._game
  nc=len(g.current_level.get_sprites_by_tag('npxgalaybz'))
  if nc<oldcol:ref.append((i,g.gudziatsk.x,g.gudziatsk.y));oldcol=nc
  if g.aqygnziho<3:lost.append(i)
  if i%10==0 or r.levels_completed>3:print('TICK',trial,i,'POS',(g.gudziatsk.x,g.gudziatsk.y),'ATTR',(g.cklxociuu,g.hiaauhahz,g.fwckfzsyc),'LEFT',g._step_counter_ui.current_steps,'LV',r.levels_completed,'STATE',r.state.name,flush=True)
  if r.levels_completed>3 or r.state.name!='NOT_FINISHED':break
 print('RESULT',trial,'LEVEL',r.levels_completed,'LENGTH',i,'PICKUPS',ref,'LOST',lost[:10],flush=True)
