from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for p in [(1,2),(2,1,7)]:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 before=(e._game.vzvypfsnt.x,e._game.vzvypfsnt.y,e._game.qiercdohl,len(e._game.seghobzez))
 e.step(GameAction.ACTION7,data={})
 after=(e._game.vzvypfsnt.x,e._game.vzvypfsnt.y,e._game.qiercdohl,len(e._game.seghobzez))
 print(p,before,'->',after,flush=True)
