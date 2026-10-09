from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
FIRST=[3]*5+[2]*10
REST=[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
def dump(label,e,r):
 g=e._game
 print("\n",label,"LC",0 if r is None else r.levels_completed,"LEVEL",g.level_index)
 print("CARR",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.jtkyjqznbnp])
 print("PAY",[(s.x,s.y,s.pixels.tolist(),sorted(s.tags)) for s in g.ouurgkpbbjj])
 print("AYY",[(i,s.x,s.y,s.pixels.shape,sorted(s.tags)) for i,s in enumerate(g.ayyvxqrhnzw)])
 print("TARGETS",len(g.fswikrcrdmx),[(t.x,t.y) for t in g.fswikrcrdmx])
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 print("SEL",sel)
e=a.make('ar25');r=None;dump("L1_START",e,r)
for z in FIRST:r=e.step(GameAction.from_id(z),data={})
dump("L2_START",e,r)
for z in REST:r=e.step(GameAction.from_id(z),data={})
dump("L3_START",e,r)
