from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
L3A=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
L3B=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
L6=[2]*11+[5,3,5]+[3]*15+[2]*4+[5]+[3]*7+[2]*12
base=SOL+L3A+L3B+L4+L5
e=a.make('ar25');r=None
for z in base:r=e.step(GameAction.from_id(z),data={})
print("START",r.levels_completed,e._game.level_index,[(s.x,s.y) for s in e._game.ayyvxqrhnzw])
for j,z in enumerate(L6,1):
 r=e.step(GameAction.from_id(z),data={})
 if r.levels_completed>=6:
  print("L6_SOLVED_SUFFIX",L6[:j],"LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
  g=e._game
  print("NEXT_OBJS",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.ayyvxqrhnzw])
  print("NEXT_TARGETS",[(t.x,t.y) for t in g.fswikrcrdmx])
  raise SystemExit
print("END",r.levels_completed,e._game.level_index,r.state.name)
