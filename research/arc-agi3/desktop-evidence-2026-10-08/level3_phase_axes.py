from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
def make(prefix):
 e=a.make('ar25');r=None
 for z in SOL+MEET+prefix:r=e.step(GameAction.from_id(z),data={})
 return e,r
def K(e,r,w):
 x=copy.deepcopy(e);rr=r
 for z in w:rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
def sig(e,r):
 k0=r.frame[0].tobytes()
 return (K(e,r,(3,))[2]==k0,K(e,r,(4,))[2]==k0,K(e,r,(3,))==K(e,r,(4,)),
 K(e,r,(3,4))==K(e,r,(1,2)),len({K(e,r,(z,7)) for z in [1,2,3,4]})==1,K(e,r,(2,))==K(e,r,(1,7,7)))
labels={(1,1,1,0,0,1):'A',(1,1,1,0,0,0):'B',(0,0,0,1,1,0):'C',(0,0,0,1,1,1):'D'}
for z in [2,7]:
 print("POWER",z)
 for n in range(10):
  e,r=make([z]*n); print(n,labels.get(tuple(map(int,sig(e,r))),sig(e,r)))
print("GRID 5^i 7^j")
for i in range(6):
 row=[]
 for j in range(6):
  e,r=make([5]*i+[7]*j); row.append(labels.get(tuple(map(int,sig(e,r))),'X'))
 print(i,row)
print("GRID 7^j 5^i")
for j in range(6):
 row=[]
 for i in range(6):
  e,r=make([7]*j+[5]*i); row.append(labels.get(tuple(map(int,sig(e,r))),'X'))
 print(j,row)
