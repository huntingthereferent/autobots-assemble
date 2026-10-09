from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
words={'12':[1,2],'21':[2,1],'34':[3,4],'43':[4,3],'55':[5,5]}
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
 return o
# Test whether all earned realizations are the same state transition, then whether mixed recursion is representation-independent.
F={k:run(v).frame[0] for k,v in words.items()}
for u in words:
 for v in words:
  if u<v: print(u,v,np.count_nonzero(F[u]!=F[v]))
mixes=[[1,2,5,5],[5,5,1,2],[3,4,5,5],[5,5,3,4],[1,2,3,4],[3,4,1,2]]
R=[]
for s in mixes:
 o=run(s);R.append(o.frame[0]);print('mix',''.join(map(str,s)),'L',o.levels_completed,o.state)
print('mixed pairwise diffs')
for i in range(len(R)):
 for j in range(i+1,len(R)): print(i,j,np.count_nonzero(R[i]!=R[j]))
