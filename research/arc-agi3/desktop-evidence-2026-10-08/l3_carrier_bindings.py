from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
e=a.make('ar25');r=None
for z in SOL+P:r=e.step(GameAction.from_id(z),data={})
g=e._game
print("VERT",None if g.iabnfcqotmd is None else (g.iabnfcqotmd.x,g.iabnfcqotmd.y,sorted(g.iabnfcqotmd.tags)))
print("HORIZ",None if g.lakiokfgmlc is None else (g.lakiokfgmlc.x,g.lakiokfgmlc.y,sorted(g.lakiokfgmlc.tags)))
print("OVO_N",len(g.ovoizfolxfq))
for i,(s,d) in enumerate(g.ovoizfolxfq.items()):
 print("OVO",i,"xy",s.x,s.y,"shape",s.pixels.shape,"tags",sorted(s.tags),"dist",d)
