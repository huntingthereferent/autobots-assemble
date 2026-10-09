from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]; P=[1,2]
# The P/5 commutator is exactly a 2-cell edge displacement. Recurse the conjugate-like
# words that move 5 across P^n and record whether support tracks the boundary.
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o
for n in range(0,16):
 left=run(P*n+[5]); right=run([5]+P*n)
 if not left.frame or not right.frame: print(n,'terminal'); break
 A,B=left.frame[0],right.frame[0]; ys,xs=np.where(A!=B)
 pts=[(int(x),int(y),int(A[y,x]),int(B[y,x])) for y,x in zip(ys,xs)]
 print(n,'comm',len(xs),'pts',pts,'L',left.levels_completed,right.levels_completed)
