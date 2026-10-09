from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
# Actual color4 motion: A4 left until blocked/changed? target x3 needs 4 more left from x12 after prior.
# derive direct: root anchor15 -> target3 requires A4 x4? observed after full sequence anchor12 means horizontal got undone/coupled by A2.
# Try order vertical first then horizontal: A2x8 then A4x4, monitoring completion.
base=[3]*5+[2]*10+[7,5]
for seq in ([2]*8+[4]*4,[4]*4+[2]*8+[4]*3,[2]*8+[4]*8):
 e=a.make('ar25');o=None
 for z in base:o=e.step(GameAction.from_id(z),data={})
 for i,z in enumerate(seq):
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>1:
   print("SOLVED",seq[:i+1],"lvl",o.levels_completed);break
 else: print("WALL",seq,"lvl",o.levels_completed,"state",o.state)
