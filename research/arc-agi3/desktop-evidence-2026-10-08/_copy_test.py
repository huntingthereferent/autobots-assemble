from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
e=a.make('ar25')
o=None
for z in SOL:o=e.step(GameAction.from_id(z),data={})
base=copy.deepcopy(e)
for z in [1,2,3,4,5,7]:
    x=copy.deepcopy(base)
    r=x.step(GameAction.from_id(z),data={})
    print(z,r.levels_completed,r.state.name,len(np.argwhere(o.frame[0]!=r.frame[0])))
