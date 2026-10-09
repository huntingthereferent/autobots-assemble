from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
# COLOR is the referent: inspect the one known positive closure as color relations, not geometry.
pre,_=run([3]*5+[2]*9); post,op=run([3]*5+[2]*10)
print("L1 POSITIVE COLOR TRANSITIONS")
D=pre!=post
print(Counter(zip(pre[D].tolist(),post[D].tolist())))
# For every color pair, count adjacency/contact pre vs closure.
def adj(A):
 out=Counter()
 for y in range(64):
  for x in range(64):
   for dx,dy in ((1,0),(0,1)):
    X,Y=x+dx,y+dy
    if X<64 and Y<64 and A[y,x]!=A[Y,X]:
     out[tuple(sorted((int(A[y,x]),int(A[Y,X]))))]+=1
 return out
ap,ac=adj(pre),adj(post)
print("ADJ CHANGES",[(k,ap[k],ac[k],ac[k]-ap[k]) for k in sorted(set(ap)|set(ac)) if ap[k]!=ac[k]])
# L2 B8 and 10 joint-descent parents: print color adjacency signatures involving meaningful colors.
for k in range(11):
 A,o=run([3]*5+[2]*10+[7,5]+[2]*k); q=adj(A)
 print("L2",k,"lvl",o.levels_completed,"counts",Counter(A.ravel().tolist()),
       "04",q[(0,4)],"05",q[(0,5)],"011",q[(0,11)],"45",q[(4,5)],"411",q[(4,11)],"511",q[(5,11)],"410",q[(4,10)],"510",q[(5,10)],"1011",q[(10,11)])
