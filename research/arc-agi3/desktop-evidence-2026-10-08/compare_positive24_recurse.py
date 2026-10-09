from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
L1PRE=[3]*5+[2]*9; L1C=L1PRE+[2]
ROOT=[3]*5+[2]*10+[7,5]+[2]*4
L224=ROOT+[2,5,3]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
A,_=run(L1PRE); B,_=run(L1C); C,_=run(L224)
# Compare the exact 24-cell 11->4 masks normalized and their surrounding color neighborhoods.
m1=np.argwhere((A==11)&(B==4))
R,_=run(ROOT); m2=np.argwhere((R==11)&(C==4))
def norm(m):
 y0,x0=m.min(0); return sorted((int(x-x0),int(y-y0)) for y,x in m)
print('MASK_EQ',norm(m1)==norm(m2),'L1norm',norm(m1),'L2norm',norm(m2))
# color neighborhood around replacement bbox, expanded 3 cells
for name,X,m in [('L1_PRE',A,m1),('L1_POST',B,m1),('L2_24',C,m2)]:
 y0,x0=m.min(0);y1,x1=m.max(0)
 sl=X[max(0,y0-3):min(64,y1+4),max(0,x0-3):min(64,x1+4)]
 print(name,'bbox',(int(x0),int(y0),int(x1),int(y1)),'counts',Counter(sl.ravel().tolist()))
# recurse from exact L2 24 state, 6x6 = 36 completion walls
for a1 in [1,2,3,4,5,7]:
 X,o=run(L224+[a1])
 for a2 in [1,2,3,4,5,7]:
  Y,q=run(L224+[a1,a2])
  print('TRY',a1,a2,'lvl',q.levels_completed,'colors',Counter(Y.ravel().tolist()))
  if q.levels_completed>1:
   print('SOLVED',L224+[a1,a2]);raise SystemExit
