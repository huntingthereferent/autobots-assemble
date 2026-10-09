from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3+p4+p5:r=e.step(GameAction.from_id(z),data={})
g=e._game
print('LEVEL',r.levels_completed,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'ATTRS',(g.fwckfzsyc,g.hiaauhahz,g.cklxociuu),'GOALS',[(s.x,s.y) for s in g.plrpelhym],'GOAL_ATTRS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),'COUNTER',(g._step_counter_ui.osgviligwp,g._step_counter_ui.current_steps,g._step_counter_ui.efipnixsvl),'LIVES',g.aqygnziho,flush=True)
for tag in ('ihdgageizm','rjlbuycveu','npxgalaybz','rhsxkxzdjz','soyhouuebz','ttfwljgohq','xfmluydglp','gbvqrjtaqo'):
 ss=g.current_level.get_sprites_by_tag(tag)
 print('TAG',tag,'COUNT',len(ss),'POSITIONS',[(s.x,s.y) for s in ss[:12]],flush=True)
print('LAUNCHERS',[(p.sprite.x+p.dx,p.sprite.y+p.dy,p.dx,p.dy,p.ullzqnksoj(g.gudziatsk)) for p in g.hasivfwip],flush=True)
print('GEARS',[(m._sprite.x,m._sprite.y,m._dir,m.bfdcztirdu.x,m.bfdcztirdu.y,m.bfdcztirdu.width,m.bfdcztirdu.height) for m in g.wsoslqeku],flush=True)
