from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
P=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
FIN=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
e=a.make('ar25');r=None
full=SOL+P+FIN
for i,z in enumerate(full):
    r=e.step(GameAction.from_id(z),data={})
    if e._game.level_index==2:
        g=e._game
        try: comp=g.vplrhaovhr()
        except: comp=False
        if comp:
            print("TARGET_COMPLETE_AFTER_INDEX",i,"SUFFIX_USED",FIN[:i-len(SOL)-len(P)+1])
            print("LEVEL_INDEX",g.level_index,"LEVELS_COMPLETED",r.levels_completed,"STATE",r.state.name,"HUJ",g.hujpxmlafgh)
            # one action advances because huj is checked before action handling
            r=e.step(GameAction.from_id(3),data={})
            print("AFTER_ADVANCE","LEVEL_INDEX",e._game.level_index,"LEVELS_COMPLETED",r.levels_completed,"STATE",r.state.name)
            print("FULL_SOLVE",full[:i+1]+[3])
            raise SystemExit
print("NO_COMPLETE",r.levels_completed,r.state.name,e._game.level_index)
