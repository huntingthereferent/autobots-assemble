from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]+[2]*8
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# The far-side step14 has diff105, same cardinality as L1 closure. Audit and test continuations there.
e,o,A=run(BASE+[3]*13); pre=A.copy(); oo=e.step(GameAction.from_id(3),data={});post=oo.frame[0]
m=pre!=post
print("STEP14",Counter(zip(pre[m].tolist(),post[m].tolist())),"diff",m.sum(),"lvl",oo.levels_completed)
P=BASE+[3]*14
for act in [1,2,3,4,5,7]:
 e,o,A=run(P); q=e.step(GameAction.from_id(act),data={})
 print("CHECK",act,"diff",int(np.sum(A!=q.frame[0])),"lvl",q.levels_completed,"state",q.state)
 if q.levels_completed>1: print("SOLVED",P+[act])
