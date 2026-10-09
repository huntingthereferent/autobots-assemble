from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
# From B8: color4 must move from anchor(15,18) to fixed(3,42): left12/down24.
# Witnessed semantics HERE: A4 moves color4 left3; A2 moves it down3.
seq=[3]*5+[2]*10+[7,5]+[4]*4+[2]*8
e=a.make('ar25');o=None
for i,z in enumerate(seq):
 o=e.step(GameAction.from_id(z),data={})
 if i>=17: print("move",i-16,z,"lvl",o.levels_completed,"state",o.state)
 if o.levels_completed>1:
  print("SOLVED L2 fullseq",seq[:i+1]);break
