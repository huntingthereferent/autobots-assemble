from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10+[7]
e=a.make('ar25');o=None
for z in PRE:o=e.step(GameAction.from_id(z),data={})
def coords(B,c):
 y,x=np.where(B==c); return set(zip(x.tolist(),y.tolist()))
B21=o.frame[0].copy()
o=e.step(GameAction.from_id(5),data={}); B8=o.frame[0].copy()
P21=coords(B21,0); P8=coords(B8,0)
print("21",sorted(P21)); print("8",sorted(P8))
# 5 source marker coordinates, normalized from returned L2 left carrier.
src={(1,1),(4,1),(7,1),(7,4),(7,7)}
print("SRC",sorted(src))
# Diagnose exact lattice normalization of 8 representation.
xs=sorted({x for x,y in P8}); ys=sorted({y for x,y in P8})
print("8 xs",xs,"ys",ys)
print("8 mod3",sorted((x%3,y%3) for x,y in P8))
# Show 8 points normalized to their min and /3 where integral.
mx=min(x for x,y in P8); my=min(y for x,y in P8)
print("8 norm",sorted((x-mx,y-my) for x,y in P8))
print("8 /3",sorted(((x-mx)//3,(y-my)//3) for x,y in P8 if (x-mx)%3==0 and (y-my)%3==0))
# 21 is 1D periodic; compare its index set to flattened 8 and source without assigning semantics.
print("21 y-index",sorted((y-1)//3 for x,y in P21 if x==37))
