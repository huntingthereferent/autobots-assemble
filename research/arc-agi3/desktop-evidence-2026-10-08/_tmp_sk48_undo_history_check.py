from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for p in [(1,2),(2,1)]:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 g=e._game
 print('PATH',p,'history_len',len(g.seghobzez),'last',[(x,y,n) for _,x,y,n in g.seghobzez[-1]],flush=True)
 for kind in ['miss','key','mate']:
  q=copy.deepcopy(e);k,m=list(q._game.xpmcmtbcv.items())[0]
  x,y= ((0,0) if kind=='miss' else (int(k.x+2),int(k.y+2)) if kind=='key' else (int(m.x+2),int(m.y+2)))
  q.step(GameAction.ACTION6,data={'x':x,'y':y})
  print(kind,'pos',q._game.vzvypfsnt.y,'hist',len(q._game.seghobzez),flush=True)
