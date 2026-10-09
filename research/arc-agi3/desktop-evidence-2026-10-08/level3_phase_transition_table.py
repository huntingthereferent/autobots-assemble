from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib
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
 return (
   K(e,r,(3,))[2]==k0,
   K(e,r,(4,))[2]==k0,
   K(e,r,(3,))==K(e,r,(4,)),
   K(e,r,(3,4))==K(e,r,(1,2)),
   len({K(e,r,(z,7)) for z in [1,2,3,4]})==1,
   K(e,r,(2,))==K(e,r,(1,7,7))
 )
for p in range(3):
 e,r=make([5]*p)
 print("BASE_PHASE",p,"SIG",sig(e,r))
 for z in ACTS:
  ee=copy.deepcopy(e);rr=ee.step(GameAction.from_id(z),data={})
  if rr.levels_completed>2:
   print(" ",z,"SOLVED",rr.levels_completed,rr.state.name);continue
  print(" ",z,"->",sig(ee,rr),"HASH",hashlib.sha1(rr.frame[0].tobytes()).hexdigest()[:8])
