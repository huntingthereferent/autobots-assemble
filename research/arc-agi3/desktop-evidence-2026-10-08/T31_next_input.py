from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]; T=[5,5]
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame:return None,o
 return o.frame[0].copy(),o
# T^31 is the maximal closed recursive state. Let that returned board be the next input.
# Ask every permitted simple relation from THERE, rather than extending T blindly.
root,o=run(T*31)
print('root',o.levels_completed,o.state,'edge63',[(y,int(root[y,63])) for y in range(59,64)])
for act in [1,2,3,4,5,7]:
 f,z=run(T*31+[act])
 if f is None:
  print('A',act,'NOFRAME',z.levels_completed,z.state);continue
 ys,xs=np.where(root!=f)
 trans={}
 for y,x in zip(ys,xs):
  k=(int(root[y,x]),int(f[y,x]));trans[k]=trans.get(k,0)+1
 print('A',act,'diff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'trans',trans,'L',z.levels_completed,z.state,'edge63',[(y,int(f[y,63])) for y in range(59,64)])
