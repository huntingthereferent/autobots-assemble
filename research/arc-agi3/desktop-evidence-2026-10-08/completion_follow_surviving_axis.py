from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def bb(A,c):
 y,x=np.where(A==c)
 return (int(x.min()),int(x.max()),int(y.min()),int(y.max()),len(x)) if len(x) else None
# After first A4, horizontal relation closes under same action. Follow returned relation: remaining supported axis is vertical.
# At each vertical step inspect color4 and completion; then see whether horizontal relation reopens.
e=a.make('ar25');o=None
for z in BASE+[4]: o=e.step(GameAction.from_id(z),data={})
seq=[4]
for k in range(1,20):
 A=o.frame[0]
 print("P",k,"c4",bb(A,4),"c0",bb(A,0),"lvl",o.levels_completed)
 if o.levels_completed>1: print("SOLVED",seq);break
 o=e.step(GameAction.from_id(2),data={});seq.append(2)
 if o.levels_completed>1: print("SOLVED",seq,"lvl",o.levels_completed);break
 if 'GAME_OVER' in str(o.state): print("DEAD",seq);break
print("END",seq,o.levels_completed,o.state)
