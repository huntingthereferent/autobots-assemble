from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5, 2,2,2,2,3, 5] + [1]*8 + [3]*4
e=a.make('ar25');r=None
for z in SOL+P:r=e.step(GameAction.from_id(z),data={})
def sc():
 g=e._game;b=g.naxbskjmlg()
 return sum(1 for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0)
print("BASE",sc(),[(s.x,s.y) for s in e._game.ayyvxqrhnzw])
for z in [5]+[1]*10:
 r=e.step(GameAction.from_id(z),data={})
 print("STEP",z,"score",sc(),"objs",[(s.x,s.y) for s in e._game.ayyvxqrhnzw],"L",r.levels_completed,r.state.name)
 if r.levels_completed>2:break
