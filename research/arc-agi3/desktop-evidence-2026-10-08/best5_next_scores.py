from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3]
e=a.make('ar25');r=None
for z in SOL+P:r=e.step(GameAction.from_id(z),data={})
def sc(env):
 g=env._game;b=g.naxbskjmlg()
 return sum(1 for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0)
for z in [1,2,3,4,5,7]:
 x=copy.deepcopy(e);rr=x.step(GameAction.from_id(z),data={});g=x._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 print(z,"score",sc(x),"sel",sel,"objs",[(s.x,s.y) for s in g.ayyvxqrhnzw],"complete",g.vplrhaovhr(),"state",rr.state.name)
