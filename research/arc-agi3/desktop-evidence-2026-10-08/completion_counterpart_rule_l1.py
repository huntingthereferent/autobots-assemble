from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25');o=None
# capture state after horizontal registration but before vertical movement, then A2#9/#10
for z in [3]*5:o=e.step(GameAction.from_id(z),data={})
S0=o.frame[0].copy()
states=[]
for n in range(10):
 o=e.step(GameAction.from_id(2),data={}); states.append(o.frame[0].copy())
# identify moving left gray carrier and moving right yellow carrier vs fixed right navy receiver.
# Compare normalized occupancy masks of the 9x9 carriers at representative pre-overlap step and fixed receiver.
B=states[0]
def mask(B,x0,y0,color):
 return {(x-x0,y-y0) for y in range(y0,y0+9) for x in range(x0,x0+9) if int(B[y,x])==color}
L=mask(B,3,18,5); Y=mask(B,51,18,4); N=mask(B,51,45,11)
print("Lgray",len(L),sorted(L));print("Y",len(Y),sorted(Y));print("Nfixed",len(N),sorted(N))
# all D4 transforms for normalized sets
def tr(P,k):
 q=[]
 for x,y in P:
  if k==0:q.append((x,y))
  elif k==1:q.append((8-y,x))
  elif k==2:q.append((8-x,8-y))
  elif k==3:q.append((y,8-x))
  elif k==4:q.append((8-x,y))
  elif k==5:q.append((x,8-y))
  elif k==6:q.append((y,x))
  else:q.append((8-y,8-x))
 return set(q)
names=['id','r90','r180','r270','flipLR','flipUD','diag','anti']
for Aname,A in [('Lgray',L),('Yellow',Y)]:
 print(Aname,"to N",[(names[k],len(tr(A,k)^N)) for k in range(8)])
# markers: black moving inside left vs holes/receiver geometry? report complements for carriers
U={(x,y) for x in range(9) for y in range(9)}
print("complements sizes",len(U-L),len(U-Y),len(U-N))
for Aname,A in [('Lcomp',U-L),('Ycomp',U-Y)]:
 print(Aname,"to Ncomp",[(names[k],len(tr(A,k)^(U-N))) for k in range(8)])
