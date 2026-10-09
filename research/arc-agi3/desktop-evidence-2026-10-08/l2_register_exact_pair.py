from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
# exact pair: color4 bbox 15..29,18..29 ; color11 bbox3..17,42..53
# Their anchors differ target-current = (-12,+24) = left4, down8 native moves.
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
seq=[3]*4+[2]*8
for i,z in enumerate(seq,1):
 o=e.step(GameAction.from_id(z),data={})
 print(i,z,"lvl",o.levels_completed,"state",o.state)
 if o.levels_completed>1: print("SOLVED_AT",i,"SEQ",seq[:i]);break
