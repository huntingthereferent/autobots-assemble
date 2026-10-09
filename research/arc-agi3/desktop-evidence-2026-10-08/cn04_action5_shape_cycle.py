from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
g=e._game
s=g.xseexqzst
def arr(s): return np.array(s.render(),dtype=int)
print("BEFORE",arr(s).shape);print(arr(s))
for k in range(1,5):
 e.step(GameAction.from_id(5),data={})
 s=e._game.xseexqzst
 print("AFTER",k,arr(s).shape,"POS",s.x,s.y);print(arr(s))
