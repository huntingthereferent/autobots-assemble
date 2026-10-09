from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
# score-16 state: selected carrier(0), L=(3,11), cap=(11,1)
SWAP=[5]+[4]*8+[1]*10+[5]+[3]*8+[2]*13
e=a.make('ar25');r=None
for i,z in enumerate(SOL+P+SWAP):
    r=e.step(GameAction.from_id(z),data={})
    if r.levels_completed>2:
        print("SOLVED_AT",i,"LEVELS",r.levels_completed,"STATE",r.state.name)
        print("FULL",SOL+P+SWAP[:i-len(SOL)-len(P)+1])
        raise SystemExit
    if r.state.name!="NOT_FINISHED":
        print("STOP_AT",i,r.state.name,r.levels_completed);raise SystemExit
g=e._game;b=g.naxbskjmlg()
covered=[(t.x,t.y,int(b[t.y,t.x])) for t in g.fswikrcrdmx if int(b[t.y,t.x])>=0]
missing=[(t.x,t.y) for t in g.fswikrcrdmx if int(b[t.y,t.x])<0]
sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
print("END_LEVELS",r.levels_completed,r.state.name,"complete",g.vplrhaovhr(),"covered",len(covered))
print("MISSING",missing)
print("SELECTED",sel,"OBJS",[(s.x,s.y,s.pixels.shape) for s in g.ayyvxqrhnzw])
