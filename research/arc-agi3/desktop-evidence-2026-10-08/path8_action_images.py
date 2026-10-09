from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
# At B8, test permitted movements as transformations of the bent 8-path.
def run(seq):
 e=a.make('ar25');o=None
 for z in BASE+seq:o=e.step(GameAction.from_id(z),data={})
 return e,o
def black(B):
 y,x=np.where(B==0); return sorted(zip(x.tolist(),y.tolist()))
for act in [1,2,3,4,5,7]:
 e,o=run([])
 prev=o.frame[0].copy(); o=e.step(GameAction.from_id(act),data={})
 print("ACT",act,"lvl",o.levels_completed,"state",o.state,"diff",np.count_nonzero(prev!=o.frame[0]),"black",black(o.frame[0]))
