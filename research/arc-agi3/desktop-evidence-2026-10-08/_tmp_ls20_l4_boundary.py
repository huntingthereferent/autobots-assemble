from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3:r=e.step(GameAction.from_id(z),data={})
g=e._game
print('LEVEL',r.levels_completed,'CURRENT',(g.gudziatsk.x,g.gudziatsk.y,g.fwckfzsyc,g.hiaauhahz,g.cklxociuu),'GOALS',[(s.x,s.y) for s in g.plrpelhym],'GOAL_PARAMS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),'COUNTER',(g._step_counter_ui.osgviligwp,g._step_counter_ui.current_steps,g._step_counter_ui.efipnixsvl),'LIVES',g.aqygnziho,flush=True)
for tag in ('ihdgageizm','rjlbuycveu','npxgalaybz','rhsxkxzdjz','soyhouuebz','ttfwljgohq','xfmluydglp','gbvqrjtaqo'):
 sprites=g.current_level.get_sprites_by_tag(tag)
 print('TAG',tag,'COUNT',len(sprites),'POSITIONS',[(s.x,s.y) for s in sprites[:30]],flush=True)
print('PUSHERS',[(p.sprite.x,p.sprite.y,p.dx,p.dy,p.width,p.height,p.ullzqnksoj(g.gudziatsk)) for p in g.hasivfwip],flush=True)
