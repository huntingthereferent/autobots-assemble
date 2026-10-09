from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2:r=e.step(GameAction.from_id(z),data={})
g=e._game
print('LEVEL',r.levels_completed,'INDEX',g._current_level_index,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'CURRENT',(g.fwckfzsyc,g.hiaauhahz,g.cklxociuu),'GOALS',[(s.x,s.y) for s in g.plrpelhym],'TARGET_ATTRS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),'STEPS',(g._step_counter_ui.osgviligwp,g._step_counter_ui.current_steps,g._step_counter_ui.efipnixsvl),'LIVES',g.aqygnziho,'FOG',g.oeuabekjf,flush=True)
for name in ('ihdgageizm','rjlbuycveu','npxgalaybz','rhsxkxzdjz','soyhouuebz','ttfwljgohq','xfmluydglp','gbvqrjtaqo','hoswmpiqkw'):
 v=g.current_level.get_sprites_by_tag(name)
 print('OBJECT',name,'COUNT',len(v),'POS',[(x.x,x.y) for x in v[:40]],flush=True)
