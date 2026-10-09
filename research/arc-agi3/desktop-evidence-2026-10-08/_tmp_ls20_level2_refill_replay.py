from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 for z in p1:e.step(GameAction.from_id(z),data={})
 trans=[];pickups=[]
 lastcol=len(e._game.current_level.get_sprites_by_tag('npxgalaybz'))
 for i,z in enumerate(p2,1):
  bef=e._game
  last=(bef.gudziatsk.x,bef.gudziatsk.y,bef.cklxociuu,bef._step_counter_ui.current_steps,bef.aqygnziho)
  r=e.step(GameAction.from_id(z),data={})
  g=e._game;nn=len(g.current_level.get_sprites_by_tag('npxgalaybz'))
  if nn<lastcol:pickups.append((i,g.gudziatsk.x,g.gudziatsk.y,g._step_counter_ui.current_steps));lastcol=nn
  if r.levels_completed>1:trans.append((i,r.levels_completed))
  if g.aqygnziho<3 or g.akoadfsur>0 or i%8==0 or r.levels_completed>1:
   print('CHECK',trial,i,'A',z,'BEFORE',last,'AFTER',(g.gudziatsk.x,g.gudziatsk.y,g.cklxociuu,g._step_counter_ui.current_steps,g.aqygnziho),'LEVEL',r.levels_completed,'STATE',r.state.name,flush=True)
  if r.levels_completed>1 or r.state.name!='NOT_FINISHED':break
 print('RESULT',trial,'LEVEL',r.levels_completed,'PATH_USED',i,'PICKUPS',pickups,'TRANS',trans,flush=True)
