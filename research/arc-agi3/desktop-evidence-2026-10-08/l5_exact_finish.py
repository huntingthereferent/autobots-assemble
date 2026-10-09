from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE3=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,7,5,2,2,2,2,2,5,3,5,2,2,2,5,3,5,5,4,5,7,2,5,2,2,2,2,3,5,1,1,1,1,1,1,1,1,3,3,3,3,5,1,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,2,2,2,5,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2]
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
e=a.make('ar25');r=None
seq=PRE3+L4+L5
for i,z in enumerate(seq):
 r=e.step(GameAction.from_id(z),data={})
 if i>=len(PRE3)+len(L4)-1 and r.levels_completed>=5:
  print("L5_SOLVED_AT",i,"SUFFIX",L5[:i-len(PRE3)-len(L4)+1],"LC",r.levels_completed,"LEVEL",e._game.level_index)
  g=e._game
  print("NEXT_OBJS",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.ayyvxqrhnzw])
  print("NEXT_TARGETS",[(t.x,t.y) for t in g.fswikrcrdmx])
  print("FULL_PREFIX",seq[:i+1])
  raise SystemExit
print("END",r.levels_completed,e._game.level_index,r.state.name)
