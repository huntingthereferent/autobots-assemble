from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
reps={'Q1':[1,1],'Q2':[1,3],'Q3':[1,5],'Q4':[3,3],'Q5':[3,5]}
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
roots={q:run(s+[7]*6)[0] for q,s in reps.items()}
# Follow the live A5 boundary from Q4/Q5 recursively, preserving returned whole board.
for q in ['Q4','Q5']:
 base=reps[q]+[7]*6
 prev=roots[q]
 print('\n',q)
 for n in range(1,17):
  b,o=run(base+[5]*n)
  ys,xs=np.where(prev!=b)
  dest=[k for k,v in roots.items() if np.array_equal(b,v)]
  print('5^',n,'stepdiff',len(xs),'dest',dest or '-','L',o.levels_completed,o.state,
        'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
  prev=b
