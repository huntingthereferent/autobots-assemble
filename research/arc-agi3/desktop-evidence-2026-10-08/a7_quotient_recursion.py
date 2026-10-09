from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame:return None,o
 return o.frame[0].copy(),o
# A7 erased distinctions at depth3. Recurse A7 itself and see whether quotient stabilizes.
seqs=[(x,y) for x in acts for y in acts]
for k in range(0,7):
 groups={}
 levels=set(); states=set()
 for s in seqs:
  b,o=run(list(s)+[7]*k)
  key=('terminal',str(o.state)) if b is None else b.tobytes()
  groups.setdefault(key,[]).append(s);levels.add(o.levels_completed);states.add(str(o.state))
 print('7pow',k,'classes',len(groups),'sizes',sorted([len(v) for v in groups.values()],reverse=True),'levels',levels,'states',states)
 print(' groups',[v for v in groups.values() if len(v)>1])
