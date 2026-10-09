from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
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
reps={'A':[],'B':[2],'C':[5],'D':[5,1]}
labels={}
for name,p in reps.items():
 e,r=make(p); s=sig(e,r);labels[s]=name;print("REP",name,p,s)
for name,p in reps.items():
 e,r=make(p);print("FROM",name)
 for z in ACTS:
  ee=copy.deepcopy(e);rr=ee.step(GameAction.from_id(z),data={})
  s=sig(ee,rr)
  print(z,"->",labels.get(s,"NEW"),s)
