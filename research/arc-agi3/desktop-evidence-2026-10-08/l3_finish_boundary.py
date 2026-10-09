from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
FIN=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
e=a.make('ar25');r=None
prev=0
for i,z in enumerate(SOL+P+FIN):
    r=e.step(GameAction.from_id(z),data={})
    if r.levels_completed!=prev:
        print("LEVEL_CHANGE","at",i,"action",z,"from",prev,"to",r.levels_completed,"state",r.state.name,"game_level",e._game.level_index)
        prev=r.levels_completed
    if r.levels_completed>=3:
        j=i-len(SOL)-len(P)+1
        print("L3_FINISH_SUFFIX",FIN[:max(0,j)])
        print("L3_FINISH_INDEX",i)
        print("FULL_PREFIX",(SOL+P+FIN)[:i+1])
        g=e._game
        print("NEW_LEVEL_OBJECTS",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.ayyvxqrhnzw])
        print("NEW_LEVEL_TARGETS",[(t.x,t.y) for t in g.fswikrcrdmx])
        raise SystemExit
