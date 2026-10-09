from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
paths=[(),(7,),(1,2),(2,1,7),(1,2,7),(2,1),(1,2,7,7),(2,1,7,7)]
for p in paths:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 g=e._game
 print('PATH',p,'POS',(g.vzvypfsnt.x,g.vzvypfsnt.y),'Q',g.qiercdohl,'H',len(g.seghobzez),'HYS',[(frame[0][1],frame[0][2]) for frame in g.seghobzez],flush=True)
