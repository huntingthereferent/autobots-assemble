from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
e=a.make('ar25');r=None
for z in SOL+P:r=e.step(GameAction.from_id(z),data={})
g=e._game
print("JT")
for i,s in enumerate(g.jtkyjqznbnp): print(i,(s.x,s.y),s.pixels.shape,sorted(s.tags))
print("OU")
for i,s in enumerate(g.ouurgkpbbjj): print(i,(s.x,s.y),s.pixels.shape,sorted(s.tags),s.pixels.tolist())
print("AYY")
for i,s in enumerate(g.ayyvxqrhnzw): print(i,(s.x,s.y),s.pixels.shape,sorted(s.tags))
print("OVO",[(g.ouurgkpbbjj.index(s) if s in g.ouurgkpbbjj else -1,v) for s,v in g.ovoizfolxfq.items()])
