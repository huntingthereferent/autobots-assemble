from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
pre=[3]*5+[2]*9
e=a.make('ar25'); o=None
for z in pre:o=e.step(GameAction.from_id(z),data={})
before=o.frame[0].copy()
o=e.step(GameAction.from_id(2),data={}); after=o.frame[0].copy()
print("CLOSURE",o.levels_completed,o.state,"diff",np.count_nonzero(before!=after))
# positive closure witness: exact color transitions + coordinates
ys,xs=np.where(before!=after)
trans=Counter((int(before[y,x]),int(after[y,x])) for y,x0 in zip(ys,xs))
print("closure transitions",trans)
print("closure bbox",(int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
# Compare with exact L2 common re-expression and one resource-consuming T=55 transition
root=after.copy()
b=root
o=e.step(GameAction.from_id(7),data={}); x=o.frame[0].copy()
ys,xs=np.where(b!=x); print("L2 common diff",len(xs),"bbox",(int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),"trans",Counter((int(b[y,x0]),int(x[y,x0])) for y,x0 in zip(ys,xs)))
b=x
for z in [5,5]:o=e.step(GameAction.from_id(z),data={})
t=o.frame[0].copy(); ys,xs=np.where(b!=t)
print("resource T diff",len(xs),"coords",list(zip(xs.tolist(),ys.tolist())),"trans",Counter((int(b[y,x0]),int(t[y,x0])) for y,x0 in zip(ys,xs)))
# structural invariant counts immediately preclosure and returned state
for name,B in [('preclose',before),('returned',after),('common',x),('T',t)]:
 c=Counter(B.ravel().tolist())
 print(name,sorted(c.items()))
