from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
base=a.make('ar25');r0=None
for z in SOL:r0=base.step(GameAction.from_id(z),data={})
def run(w):
 e=copy.deepcopy(base);r=r0
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return e,r
def coords(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 return (sel,len(g.flqblmrxsla),g.xukxeewuexo,g.xjwpeqpcxav,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.level_index)
H1=(2,2,2,1,1);H2=(5,5,4,5,7,2)
e1,r1=run(H1);e2,r2=run(H2)
print("FRAME_EQUAL",r1.frame[0].tobytes()==r2.frame[0].tobytes())
print("H1_COORDS",coords(e1,r1))
print("H2_COORDS",coords(e2,r2))
for z in [1,2,3,4,5,7]:
 x1=copy.deepcopy(e1);a1=x1.step(GameAction.from_id(z),data={})
 x2=copy.deepcopy(e2);a2=x2.step(GameAction.from_id(z),data={})
 print("NEXT",z,a1.frame[0].tobytes()==a2.frame[0].tobytes(),coords(x1,a1),coords(x2,a2))
