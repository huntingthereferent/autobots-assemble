from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def get(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy(),o
# positive witness preclosure and returned L2
P,_=get([3]*5+[2]*9); R,_=get([3]*5+[2]*10)
# marker/carrier relation: marker colors 0(left),11(right), carriers 5(left),4(right).
# Report marker coordinates relative to connected carrier's 9x9 bbox at the closure witness.
def rel(B,bbox,marker):
 x0,y0,x1,y1=bbox
 yy,xx=np.where(B[y0:y1+1,x0:x1+1]==marker)
 return sorted((int(x),int(y)) for y,x in zip(yy,xx))
for name,B in [('PRE',P),('RET',R)]:
 print(name,"L",rel(B,(3,42 if name=='PRE' else 45,11,53 if name=='PRE' else 53),0))
 print(name,"R",rel(B,(51,42 if name=='PRE' else 45,59,53 if name=='PRE' else 53),11))
# Exact L2 returned marker patterns in 9x9 carriers.
L=rel(R,(3,45,11,53),0); Q=rel(R,(51,45,59,53),11)
print("L2 marker L",L);print("L2 marker R",Q)
# compare marker coordinate transforms only
S=set(L); T=set(Q)
funcs={'id':lambda x,y:(x,y),'r90':lambda x,y:(8-y,x),'r180':lambda x,y:(8-x,8-y),'r270':lambda x,y:(y,8-x),'lr':lambda x,y:(8-x,y),'ud':lambda x,y:(x,8-y),'diag':lambda x,y:(y,x),'anti':lambda x,y:(8-y,8-x)}
for k,f in funcs.items():
 U={f(x,y) for x,y in S}; print(k,"symdiff",len(U^T),"mapped",sorted(U))
