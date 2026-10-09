from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10+[7]
e=a.make('ar25');o=None
for z in PRE:o=e.step(GameAction.from_id(z),data={})
def pts(B,c):
 yy,xx=np.where(B==c); return set(zip(xx.tolist(),yy.tolist()))
def report(n,B):
 p0=pts(B,0); p11=pts(B,11)
 # periodic interior black lattice and right edge navy
 lattice=sorted((x,y) for x,y in p0 if x==37 and y%3==1)
 edge=sorted(y for x,y in p11 if x==63)
 print(n,"lvl",o.levels_completed,"black",len(p0),"lat",len(lattice),"latY",[y for x,y in lattice],"navy",len(p11),"edgeN",len(edge),"edgeRange",(min(edge),max(edge)) if edge else None)
report(0,o.frame[0])
# A5 is the witnessed 21<->8 transformation. Follow every return, not just diff counts.
for n in range(1,66):
 o=e.step(GameAction.from_id(5),data={})
 if o.levels_completed>1:
  print("SOLVED",n,o.levels_completed); break
 if 'GAME_OVER' in str(o.state):
  print("GAMEOVER",n); break
 report(n,o.frame[0])
