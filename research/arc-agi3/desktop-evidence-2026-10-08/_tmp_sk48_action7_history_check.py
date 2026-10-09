from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for p in [(1,2),(2,1),(1,2,7),(2,1,7)]:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 g=e._game
 print('PATH',p,'pos',(g.vzvypfsnt.x,g.vzvypfsnt.y),'counter',g.qiercdohl,'history',len(g.seghobzez),'last',[(x,y,n) for _,x,y,n in g.seghobzez[-1]][:2],flush=True)
