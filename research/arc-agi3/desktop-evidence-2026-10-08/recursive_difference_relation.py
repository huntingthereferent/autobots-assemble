from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
# Returned level2 -> A5 re-expression -> one recursive difference
o=e.step(GameAction.ACTION5,data={}); p=o.frame[0].copy()
o=e.step(GameAction.ACTION5,data={}); q=o.frame[0].copy()
# Compare the 8-cell L in the recursive difference to every 8-cell subset relation we can earn by translation/reflection
D={(int(x),int(y)) for y,x in zip(*np.where((p==0)&(q==9)))}
print('D',sorted(D))
# normalize and test dihedral transforms of D against black pixels in q and other sparse nonwhite components
def norm(S):
 mx=min(x for x,y in S); my=min(y for x,y in S)
 return {(x-mx,y-my) for x,y in S}
def tf(S,k):
 S=norm(S)
 if k==0:T={(x,y) for x,y in S}
 if k==1:T={(-x,y) for x,y in S}
 if k==2:T={(x,-y) for x,y in S}
 if k==3:T={(-x,-y) for x,y in S}
 if k==4:T={(y,x) for x,y in S}
 if k==5:T={(-y,x) for x,y in S}
 if k==6:T={(y,-x) for x,y in S}
 if k==7:T={(-y,-x) for x,y in S}
 return norm(T)
for c in [0,4,5,10,11]:
 S={(int(x),int(y)) for y,x in zip(*np.where(q==c))}
 matches=[]
 for k in range(8):
  T=tf(D,k)
  for ax,ay in S:
   placed={(x+ax,y+ay) for x,y in T}
   if placed<=S: matches.append((k,ax,ay))
 print('color',c,'contains transformed D',matches[:20],'count',len(matches))
