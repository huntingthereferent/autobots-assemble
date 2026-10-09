from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
P=[1,2]
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 root=o.frame[0].copy()
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame:return root,o
 return o.frame[0].copy(),o
# recurse on P/A5 ordering, not individual directions
seqs={'P5':P+[5],'5P':[5]+P,'PP5':P+P+[5],'P5P':P+[5]+P,'5PP':[5]+P+P,
      '55P':[5,5]+P,'5P5':[5]+P+[5],'P55':P+[5,5]}
F={}
for k,s in seqs.items():
 f,o=run(s);F[k]=f
 print(k,'diffbase?', 'L',o.levels_completed,'state',o.state)
for u,v in [('P5','5P'),('PP5','P5P'),('P5P','5PP'),('55P','5P5'),('5P5','P55')]:
 ys,xs=np.where(F[u]!=F[v])
 print(u,v,'diff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
