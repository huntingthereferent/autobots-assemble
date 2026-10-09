from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
near=(1,4,1,1,1,1,1,3,3,3,2,2,3,2,2,2)
for suffix in ((),(2,),(3,2),(4,2),(1,2),(2,2)):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 for a in p1+near+suffix:r=e.step(GameAction.from_id(a),data={})
 g=e._game
 print('EDGE',suffix,'PLAYER',(g.gudziatsk.x,g.gudziatsk.y),'ROT',g.cklxociuu,'GOAL_ROT',g.ehwheiwsk,'VALID',r.state.name,'LEVELS',r.levels_completed,'FAIL_TIMER',g.akoadfsur,'LIVES',g.aqygnziho,flush=True)
