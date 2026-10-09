from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
base=a.make('ar25');r0=None
for z in SOL+MEET:r0=base.step(GameAction.from_id(z),data={})
def run(prefix):
 e=copy.deepcopy(base);r=r0
 for z in prefix:r=e.step(GameAction.from_id(z),data={})
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
def lab(p):
 e,r=run(p);return labels.get(tuple(map(int,sig(e,r))),'X')
print("7POW",[lab([7]*n) for n in range(10)])
print("2POW",[lab([2]*n) for n in range(10)])
print("5POW",[lab([5]*n) for n in range(10)])
print("5then7")
for i in range(6):print(i,[lab([5]*i+[7]*j) for j in range(6)])
print("7then5")
for j in range(6):print(j,[lab([7]*j+[5]*i) for i in range(6)])
