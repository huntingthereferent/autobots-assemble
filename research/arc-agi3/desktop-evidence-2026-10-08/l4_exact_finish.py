from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,7,5,2,2,2,2,2,5,3,5,2,2,2,5,3,5,5,4,5,7,2,5,2,2,2,2,3,5,1,1,1,1,1,1,1,1,3,3,3,3,5,1,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,2,2,2,5,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2]
L4=[2]*6+[5]+[4]*7+[5]+[4]*7+[1]*7
e=a.make('ar25');r=None
for i,z in enumerate(PRE+L4):
 r=e.step(GameAction.from_id(z),data={})
 if i>=len(PRE)-1 and r.levels_completed>=4:
  print("L4_SOLVED_AT",i,"SUFFIX",L4[:i-len(PRE)+1],"LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
  g=e._game
  print("NEXT_OBJS",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.ayyvxqrhnzw])
  print("NEXT_TARGETS",[(t.x,t.y) for t in g.fswikrcrdmx])
  print("FULL_PREFIX",(PRE+L4)[:i+1])
  raise SystemExit
print("END",r.levels_completed,e._game.level_index,r.state.name)
