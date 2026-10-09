from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for p in [(1,2,1),(2,2,1)]:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 for i in range(5):
  g=e._game
  print('PATH',p,'UNDO',i,'POS',[(s.x,s.y) for s in g.xpmcmtbcv],'Q',g.qiercdohl,'H',len(g.seghobzez),'REC',[(f[0][1],f[0][2]) for f in g.seghobzez],flush=True)
  e.step(GameAction.ACTION7,data={})
