from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,1,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for i,z in enumerate(p1+p):r=e.step(GameAction.from_id(z),data={})
g=e._game
print('REFERENCE',(g.gudziatsk.x,g.gudziatsk.y),'ROT',g.cklxociuu,'SHAPE',g.fwckfzsyc,'COLOR',g.hiaauhahz,'LIVES',g.aqygnziho,'ENERGY',g._step_counter_ui.osgviligwp,flush=True)
for z in (1,2,3,4):
 q=copy.deepcopy(e);r=q.step(GameAction.from_id(z),data={});h=q._game
 print('NEXT',z,'POS',(h.gudziatsk.x,h.gudziatsk.y),'ROT',h.cklxociuu,'LIVES',h.aqygnziho,'FAIL',h.akoadfsur,'LEVEL',r.levels_completed,'ANIM',h.ebfuxzbvn,'STATE',r.state.name,flush=True)
