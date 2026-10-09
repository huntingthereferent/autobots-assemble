from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
e=a.make('ar25');r=None
for z in SOL+P:r=e.step(GameAction.from_id(z),data={})
g=e._game;b=g.naxbskjmlg()
covered=[];missing=[]
for t in g.fswikrcrdmx:
 row=(t.x,t.y,int(b[t.y,t.x]))
 (covered if row[2]>=0 else missing).append(row)
print("score",len(covered),"covered",covered)
print("missing",missing)
sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
print("selected",sel,"objs",[(s.x,s.y,s.pixels.tolist()) for s in g.ayyvxqrhnzw])
