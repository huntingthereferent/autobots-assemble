from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25'); o=None
for z in [3]*5+[2]*9:o=e.step(GameAction.from_id(z),data={})
pre=o.frame[0].copy()
o=e.step(GameAction.from_id(2),data={}); ret=o.frame[0].copy()
def report(name,A,B):
 yy,xx=np.where(A!=B)
 tr=Counter((int(A[y,x]),int(B[y,x])) for y,x in zip(yy,xx))
 print(name,"diff",len(xx),"bbox",None if not len(xx) else (int(xx.min()),int(xx.max()),int(yy.min()),int(yy.max())),"trans",tr)
report("CLOSURE",pre,ret)
# returned L2 -> common reexpression
b=ret.copy(); o=e.step(GameAction.from_id(7),data={}); common=o.frame[0].copy(); report("COMMON",b,common)
# common -> 55 resource
b=common.copy()
for z in [5,5]:o=e.step(GameAction.from_id(z),data={})
T=o.frame[0].copy(); report("RESOURCE55",b,T)
# Color-count deltas are diagnostics, whole states remain referent.
for name,B in [('PRE',pre),('RET',ret),('COMMON',common),('T',T)]:
 print(name,Counter(map(int,B.ravel())))
# positive closure: identify cells participating by 3x3 lattice residues and connected change rows/cols
yy,xx=np.where(pre!=ret)
print("closure residues",Counter((int(x%3),int(y%3)) for y,x in zip(yy,xx)))
print("closure rows",Counter(map(int,yy)))
print("closure cols",Counter(map(int,xx)))
