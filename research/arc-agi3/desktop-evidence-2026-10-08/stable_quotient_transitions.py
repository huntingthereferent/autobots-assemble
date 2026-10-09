from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10; acts=[1,2,3,4,5,7]
# representatives of the five stable A7 quotient classes
reps={'Q1':[1,1],'Q2':[1,3],'Q3':[1,5],'Q4':[3,3],'Q5':[3,5]}
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
# normalize each representative into stable quotient with 7^6, then apply each relation.
roots={q:run(s+[7]*6)[0] for q,s in reps.items()}
print('TRANSITIONS FROM FIVE STABLE WHOLE-STATES')
for q,s in reps.items():
 for z in acts:
  b,o=run(s+[7]*6+[z])
  # exact destination if it lands on one of the five stable roots
  dest=[k for k,v in roots.items() if np.array_equal(b,v)]
  # evidence relative to current whole-state
  ys,xs=np.where(roots[q]!=b)
  print(q,'--',z,'-->',dest or '?','diff',len(xs),'L',o.levels_completed,o.state)
