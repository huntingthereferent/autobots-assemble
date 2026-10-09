from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Successful L1: pre A2#10 -> returned L2
_,op,P=run([3]*5+[2]*9); _,oc,C=run([3]*5+[2]*10)
# L2 candidate: B8 -> after exact displacement
base=[3]*5+[2]*10+[7,5]
_,ob,B=run(base); _,on,N=run(base+[3]*4+[2]*8)
def trans(A,Z):
 yy,xx=np.where(A!=Z); co=Counter((int(A[y,x]),int(Z[y,x])) for y,x in zip(yy,xx))
 return len(xx),(int(xx.min()),int(xx.max()),int(yy.min()),int(yy.max())),co
for name,A,Z in [('L1_CLOSE',P,C),('L2_REGISTER',B,N)]:
 n,bb,co=trans(A,Z);print(name,'diff',n,'bbox',bb,'trans',co)
 print('before counts',Counter(map(int,A.ravel())),'after',Counter(map(int,Z.ravel())))
# For L2 track the exact-pair masks after movement: did BOTH move? registration assumption audit.
def component_at(A,c,seed):
 M=A==c; st=[seed];seen={seed};q=[]
 while st:
  x,y=st.pop();q.append((x,y))
  for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if 0<=p[0]<64 and 0<=p[1]<64 and p not in seen and M[p[1],p[0]]:seen.add(p);st.append(p)
 return q
for label,A in [('B8',B),('AFTER',N)]:
 print(label)
 for c in [4,11]:
  # all comps >=20
  M=A==c;seen=set()
  for y,x in zip(*np.where(M)):
   if (x,y) in seen:continue
   q=component_at(A,c,(int(x),int(y)));seen|=set(q)
   if len(q)>=20:print(c,len(q),(min(x for x,y in q),max(x for x,y in q),min(y for x,y in q),max(y for x,y in q)))
