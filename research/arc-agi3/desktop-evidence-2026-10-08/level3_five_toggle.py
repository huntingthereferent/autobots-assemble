from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
def state(prefix):
 e=a.make('ar25');r=None
 for z in SOL+MEET+prefix:r=e.step(GameAction.from_id(z),data={})
 return e,r
def key(e,r,w):
 x=copy.deepcopy(e);rr=r
 for z in w:rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
for n in range(0,7):
 e,r=state([5]*n); k0=r.frame[0].tobytes()
 print("N5",n,"ROOT",hashlib.sha1(k0).hexdigest()[:10])
 singles={z:key(e,r,(z,)) for z in ACTS}
 print("  3=e",singles[3][2]==k0,"4=e",singles[4][2]==k0,"3=4",singles[3]==singles[4])
 print("  34=12",key(e,r,(3,4))==key(e,r,(1,2)),"43=21",key(e,r,(4,3))==key(e,r,(2,1)))
 print("  7collapse",len({key(e,r,(z,7)) for z in [1,2,3,4]})==1)
 print("  2=177",key(e,r,(2,))==key(e,r,(1,7,7)))
