from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
# Keep actual X0->...->returned X1 chain.
states=[]
o=None
for n,i in enumerate([3]*5+[2]*10,1):
 o=e.step(GameAction.from_id(i),data={})
 states.append(o.frame[0].copy())
# Compare the last valid pre-closure board (action14) to returned board X1 after closure.
p,q=states[-2],states[-1]
print('changed',np.count_nonzero(p!=q))
for c in sorted(set(np.unique(p)).union(np.unique(q))):
 yp,xp=np.where(p==c); yq,xq=np.where(q==c)
 def bb(xs,ys):
  return None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max()),len(xs))
 print('c',int(c),'pre',bb(xp,yp),'ret',bb(xq,yq))
# Translation witnesses: find exact overlap under 3-cell translations, per color, to distinguish retained vs replaced evidence.
for c in [0,4,5,11]:
 P=set(zip(*np.where(p==c))); Q=set(zip(*np.where(q==c)))
 best=[]
 for dy in range(-12,13,3):
  for dx in range(-12,13,3):
   moved={(y+dy,x+dx) for y,x in P if 0<=y+dy<64 and 0<=x+dx<64}
   score=len(moved&Q)
   best.append((score,dx,dy,len(P),len(Q)))
 print('best',c,sorted(best,reverse=True)[:4])
