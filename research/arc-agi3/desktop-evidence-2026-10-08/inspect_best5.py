from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[5,5,4,5,7,2,5]
H=[2,2,2,2,3]
e=a.make('ar25');r=None
for z in SOL+MEET+H:r=e.step(GameAction.from_id(z),data={})
g=e._game;b=g.naxbskjmlg()
print("complete",g.vplrhaovhr(),"score",sum(1 for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0))
print("covered",[(t.x,t.y,int(b[t.y,t.x])) for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0])
print("missing",[(t.x,t.y) for t in g.fswikrcrdmx if int(b[t.y,t.x])<0])
sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
print("selected",sel)
for i,s in enumerate(g.ayyvxqrhnzw):print(i,s.x,s.y,s.pixels.shape)
