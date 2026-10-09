from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
e=a.make('ar25');r=None
for z in SOL+MEET:r=e.step(GameAction.from_id(z),data={})
def key(word):
 x=copy.deepcopy(e);rr=r
 for z in word:rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
for n in range(0,19):
 if n>0:r=e.step(GameAction.from_id(5),data={})
 if r.levels_completed>2:
  print("SOLVED_AT_5_POWER",n,r.levels_completed,r.state.name);break
 k0=r.frame[0].tobytes(); x=copy.deepcopy(e)
 def kk(w):
  xx=copy.deepcopy(x);rr=r
  for z in w:rr=xx.step(GameAction.from_id(z),data={})
  return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
 sig=(kk((3,))[2]==k0,kk((4,))[2]==k0,kk((3,))==kk((4,)),kk((3,4))==kk((1,2)),len({kk((z,7)) for z in [1,2,3,4]})==1,kk((2,))==kk((1,7,7)))
 print(n,hashlib.sha1(k0).hexdigest()[:8],sig)
