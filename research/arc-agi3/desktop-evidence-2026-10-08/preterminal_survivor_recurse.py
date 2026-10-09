from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
parents={'34x2':([3]*13+[4]*21)*2,'43x2':([4]*9+[3]*21)*2}
# Follow each surviving nonterminal relation from the exact preterminal returned state.
for name,p in parents.items():
 for rel in ([3,7] if name=='34x2' else [4,7]): # 5 known exhaustor; inert omitted
  e=a.make('ar25')
  for z in pre+p:o=e.step(GameAction.from_id(z),data={})
  prev=o.frame[0].copy()
  print("\n",name,"=>",rel)
  for n in range(1,70):
   o=e.step(GameAction.from_id(rel),data={}); cur=o.frame[0].copy()
   diff=np.count_nonzero(prev!=cur)
   print(n,diff,o.levels_completed,o.state)
   if o.levels_completed>1:
    print("SOLVED",name,rel,n); raise SystemExit
   if 'GAME_OVER' in str(o.state) or diff==0: break
   prev=cur
