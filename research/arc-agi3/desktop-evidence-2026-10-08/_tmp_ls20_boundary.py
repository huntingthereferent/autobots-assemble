from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
arc=Arcade(operation_mode=OperationMode.NORMAL)
e=arc.make('ls20')
g=e._game
print('LEVEL',g._current_level_index,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'SIZE',(g.gisrhqpee,g.tbwnoxqgc),'TARGETS',[(s.x,s.y) for s in g.plrpelhym],'GOAL_ATTRS',list(zip(g.ldxlnycps,g.yjdexjsoa,g.ehwheiwsk)),'START_ATTRS',(g.fwckfzsyc,g.hiaauhahz,g.cklxociuu),'STEP_COUNTER',g._step_counter_ui.osgviligwp,'GRID',(g.drtdqwdbc,g.qlgmdayuo),flush=True)
for name in ('ihdgageizm','ttfwljgohq','soyhouuebz','rhsxkxzdjz','npxgalaybz','rjlbuycveu'):
 print('CATEGORY',name,[(s.x,s.y) for s in g.current_level.get_sprites_by_tag(name)][:50],flush=True)
for z in (1,2,3,4):
 q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={});h=q._game
 print('ACTION',z,'PLAYER',(h.gudziatsk.x,h.gudziatsk.y),'ATTRS',(h.fwckfzsyc,h.hiaauhahz,h.cklxociuu),'VISITED',h.lvrnuajbl,'COUNT',h._step_counter_ui.osgviligwp,'LEVEL',r.levels_completed,flush=True)
