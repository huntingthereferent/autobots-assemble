from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
# One layer up: transformations, represented by earned equivalent realizations.
R={'I':[7],'U':[1],'D':[2],'L':[3],'R':[4],'O':[5],
   'T12':[1,2],'T21':[2,1],'T34':[3,4],'T43':[4,3],'T55':[5,5]}
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
root,_=run([])
# Transformation signatures from root, quotient exact whole outputs.
groups={}
for name,seq in R.items():
 b,o=run(seq); groups.setdefault(b.tobytes(),[]).append(name)
print('ROOT TRANSFORMATION QUOTIENT')
for g in groups.values(): print(g)
# recurse each transformation with itself: F(X), F(F(X)); compare whether idempotent,
# involutive (F2=root), or continuing.
print('\nSELF-COMPOSITION')
for name,seq in R.items():
 b1,o1=run(seq); b2,o2=run(seq+seq)
 print(name,'F2=F',np.array_equal(b2,b1),'F2=root',np.array_equal(b2,root),
       'd1',np.count_nonzero(root!=b1),'d2',np.count_nonzero(b1!=b2),
       'L',o2.levels_completed,o2.state)
# Composition quotient of the distinct primitive transformation classes from root.
prims={'A':[1], 'B':[3], 'C':[4], 'D':[5]} # A represents earned {1,2,7} at first returned step
outs={}
for x,sx in prims.items():
 for y,sy in prims.items():
  b,o=run(sx+sy); outs.setdefault(b.tobytes(),[]).append(x+y)
print('\nCOMPOSITION CLASSES',len(outs))
for g in outs.values(): print(g)
