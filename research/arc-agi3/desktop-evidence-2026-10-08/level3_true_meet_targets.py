from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(5,5,4,5,7,2,5)
e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
g=e._game
board=g.naxbskjmlg()
print("LEVEL",g.level_index,"TARGETS",len(g.fswikrcrdmx),"COMPLETE",g.vplrhaovhr())
missing=[]; covered=[]
for i,t in enumerate(g.fswikrcrdmx):
 v=int(board[t.y,t.x])
 row=(i,t.x,t.y,v)
 (covered if v>=0 else missing).append(row)
print("COVERED",covered)
print("MISSING",missing)
sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
print("SELECTED",sel)
for i,s in enumerate(g.ayyvxqrhnzw):
 print("OBJ",i,"xy",s.x,s.y,"shape",s.pixels.shape,"tags",sorted(s.tags))
