from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10; prefix=[3,3]+[7]*6
def run(seq):
 e=a.make('ar25')
 for i in solve+prefix+seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
# At each A5 parity, ask which simple actions preserve/cancel the reversible 29-cell component
# versus which advance the irreversible boundary. Compare Ai then 5 against 5 then Ai.
for parity in [0,1]:
 base=[5]*parity; B,_=run(base)
 print('\nPARITY',parity)
 for i in [1,2,3,4,7]:
  x,ox=run(base+[i,5]); y,oy=run(base+[5,i])
  ys,xs=np.where(x!=y)
  print('comm',i,'diff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),
        'states',ox.state,oy.state)
# Test whether a simple action can cancel the one-cell irreversible residue of one A5:
# compare base->5->Ai against base itself and against base->55.
for parity in [0,1]:
 base=[5]*parity; B,_=run(base); T,_=run(base+[5,5])
 print('\nCANCEL TEST parity',parity)
 for i in [1,2,3,4,7]:
  X,o=run(base+[5,i])
  print(i,'to_base',np.count_nonzero(B!=X),'to_A5sq',np.count_nonzero(T!=X),'L',o.levels_completed,o.state)
