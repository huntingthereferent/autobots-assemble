from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
# Completion in L1 moved BOTH halves. Test joint-relation candidate:
# At B8 color4/black pair are horizontally opposed under A3/A4.
# A4 once reaches its left wall; then vertical to y42. At that returned state inspect every simple action
# for whether it changes the joint relation / completes.
prefix=BASE+[4]+[2]*8
for act in [1,2,3,4,5,7]:
 e=a.make('ar25');o=None
 for z in prefix:o=e.step(GameAction.from_id(z),data={})
 pre=o.frame[0].copy()
 o=e.step(GameAction.from_id(act),data={}); post=o.frame[0]
 yy0,xx0=np.where(pre==0); yy4,xx4=np.where(pre==4)
 yy0b,xx0b=np.where(post==0); yy4b,xx4b=np.where(post==4)
 print("A",act,"lvl",o.levels_completed,"state",o.state,"diff",np.count_nonzero(pre!=post),
       "black", (xx0.min(),xx0.max(),yy0.min(),yy0.max()),"->",(xx0b.min(),xx0b.max(),yy0b.min(),yy0b.max()),
       "c4",(xx4.min(),xx4.max(),yy4.min(),yy4.max()),"->",(xx4b.min(),xx4b.max(),yy4b.min(),yy4b.max()))
