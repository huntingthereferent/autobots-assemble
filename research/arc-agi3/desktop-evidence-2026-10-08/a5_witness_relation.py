from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
# use Q4 stable state; recurrence is same witnessed 30-cell family
prefix=[3,3]+[7]*6
def run(n):
 e=a.make('ar25')
 for i in solve+prefix:o=e.step(GameAction.from_id(i),data={})
 for _ in range(n):o=e.step(GameAction.ACTION5,data={})
 return o.frame[0].copy()
B=[run(n) for n in range(5)]
W=[]
for n in range(1,5):
 p,c=B[n-1],B[n]; ys,xs=np.where(p!=c)
 s={(int(x),int(y),int(p[y,x]),int(c[y,x])) for y,x in zip(ys,xs)}
 W.append(s)
 print('W',n,'n',len(s),'trans', {k:sum(1 for x,y,a,b in s if (a,b)==k) for k in sorted(set((a,b) for x,y,a,b in s))})
# compare supports and directed transitions across consecutive witnesses
for i in range(3):
 A=W[i];C=W[i+1]
 sa={(x,y) for x,y,a,b in A}; sc={(x,y) for x,y,a,b in C}
 print('W',i+1,'vs',i+2,'support_equal',sa==sc,'support_delta',len(sa^sc))
 rev=sum(1 for x,y,a,b in A if (x,y,b,a) in C)
 same=sum(1 for z in A if z in C)
 print(' directed same',same,'reversed',rev)
# two-step whole-board residual: what survives after applying same AB twice?
for n in range(3):
 p,c=B[n],B[n+2];ys,xs=np.where(p!=c)
 trans={}
 for y,x in zip(ys,xs):trans[(int(p[y,x]),int(c[y,x]))]=trans.get((int(p[y,x]),int(c[y,x])),0)+1
 print('two-step',n,'->',n+2,'diff',len(xs),'coords',list(zip(xs.tolist(),ys.tolist())),'trans',trans)
