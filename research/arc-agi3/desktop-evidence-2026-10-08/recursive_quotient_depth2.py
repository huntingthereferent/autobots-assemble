from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
acts=[1,2,3,4,5,7]
def board(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return None if not o.frame else o.frame[0].copy(),o
# Recursively quotient ALL length-2 histories by exact returned whole board.
groups={}
for x in acts:
 for y in acts:
  b,o=board([x,y])
  key=('terminal',str(o.state)) if b is None else b.tobytes()
  groups.setdefault(key,[]).append((x,y,o.levels_completed,str(o.state)))
print('classes',len(groups))
for n,g in enumerate(groups.values(),1):
 print('C',n,[p[:2] for p in g],'state',g[0][3])
# For each exact class, test one more action and record class count, preserving only state equality.
seqs=[p[:2] for g in groups.values() for p in g]
for z in acts:
 gg={}
 for s in seqs:
  b,o=board(list(s)+[z]);key=('terminal',str(o.state)) if b is None else b.tobytes()
  gg.setdefault(key,[]).append(s)
 print('z',z,'classes',len(gg),'groups',[v for v in gg.values() if len(v)>1])
