from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
L=(2,2,2,1,1,7,7,7,7,5)
R=(5,5,4,5,7,2,5)
ACTS=[1,2,3,4,5,7]
base=a.make('ar25');r0=None
for z in SOL:r0=base.step(GameAction.from_id(z),data={})
def after(h):
 e=copy.deepcopy(base);r=r0
 for z in h:r=e.step(GameAction.from_id(z),data={})
 return e,r
def key(e,r):
 g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=tuple((tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla)
 objs=tuple((s.x,s.y,s.pixels.shape,s.pixels.tobytes()) for s in g.ayyvxqrhnzw)
 ovo=tuple(sorted((g.ayyvxqrhnzw.index(s) if s in g.ayyvxqrhnzw else -1,v) for s,v in g.ovoizfolxfq.items()))
 return (r.frame[0].tobytes(),g.level_index,sel,stack,objs,ovo,g.xukxeewuexo,g.xjwpeqpcxav,g.qehjebksqcm,g.hujpxmlafgh,g.hsiusrsrdkswnt,g.lelsvjlwneo.current_steps)
e1,r1=after(L);e2,r2=after(R)
print("ROOT_KEY_EQUAL",key(e1,r1)==key(e2,r2))
print("LEVELS",r1.levels_completed,r2.levels_completed)
for z in ACTS:
 x1=copy.deepcopy(e1);a1=x1.step(GameAction.from_id(z),data={})
 x2=copy.deepcopy(e2);a2=x2.step(GameAction.from_id(z),data={})
 print("NEXT",z,"KEY_EQ",key(x1,a1)==key(x2,a2),"FRAME_EQ",a1.frame[0].tobytes()==a2.frame[0].tobytes(),"LEVEL",a1.levels_completed,a2.levels_completed)
