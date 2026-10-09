from arc_agi import Arcade,OperationMode
from arcengine import GameAction
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in (3,3,3,1,1,1,1,4,4,4,1,1,1):e.step(GameAction.from_id(z),data={})
g=e._game
print('LEVEL',g._current_level_index,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'CURRENT',(g.fwckfzsyc,g.hiaauhahz,g.cklxociuu),'GOAL',[(x.x,x.y) for x in g.plrpelhym],'GOAL_ATTRS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),'WALL_COUNT',len(g.current_level.get_sprites_by_tag('ihdgageizm')),'MOVER_COUNT',len(g.hasivfwip),'ANIMS',len(g.euemavvxz),'ENERGY',g._step_counter_ui.osgviligwp,flush=True)
for n in ('rhsxkxzdjz','soyhouuebz','ttfwljgohq','npxgalaybz','ihdgageizm','xfmluydglp','rjlbuycveu','gbvqrjtaqo'):
 v=g.current_level.get_sprites_by_tag(n)
 print('N',n,'NUM',len(v),'POSITIONS',[(x.x,x.y) for x in v[:20]],flush=True)
