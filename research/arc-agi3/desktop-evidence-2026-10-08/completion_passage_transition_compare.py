from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Compare positive L1 passage into receiver with L2 full divider passage at y42.
# Track transitions per inward step and test whether closure corresponds to a specific color-pair exchange.
L1=[3]*5+[2]*9
e,o,A=run(L1); pre=A.copy(); oo=e.step(GameAction.from_id(2),data={}); post=oo.frame[0]
print("L1_CLOSE_TRANS",Counter(zip(pre[pre!=post].tolist(),post[pre!=post].tolist())))
BASE=[3]*5+[2]*10+[7,5]+[2]*8
e,o,A=run(BASE)
for i in range(1,11):
 pre=A.copy(); oo=e.step(GameAction.from_id(3),data={}); post=oo.frame[0]
 m=pre!=post
 print("L2_IN",i,"lvl",oo.levels_completed,"diff",int(m.sum()),"trans",Counter(zip(pre[m].tolist(),post[m].tolist())))
 if oo.levels_completed>1: print("SOLVED",BASE+[3]*i);raise SystemExit
 A=post;o=oo
# At far-side expanded state, continue inward until action closes; then test vertical alignment and A5/A7 there.
print("FAR",o.levels_completed,o.state)
for j in range(1,8):
 pre=A.copy(); oo=e.step(GameAction.from_id(3),data={});post=oo.frame[0]
 print("FAR+",j,"diff",int(np.sum(pre!=post)),"lvl",oo.levels_completed,"state",oo.state)
 if oo.levels_completed>1: print("SOLVED_FAR",BASE+[3]*(10+j));raise SystemExit
 A=post;o=oo
