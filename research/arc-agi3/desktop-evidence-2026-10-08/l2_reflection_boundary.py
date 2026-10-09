from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
base=[3]*5+[2]*10
# Level2 is exact horizontal reflection, already aligned. Movement actions preserve/refine spatial relation;
# test whether closure is reaching the divider boundary while preserving mirror: A3 moves apart, A4 together.
# Instead of long enumeration, derive distance: inner edges x11 and x51, divider x36..38. paired A4 shifts 3 each -> gaps shrink 6.
# Need symmetric contact to divider: left right-edge 11+3n, right left-edge 51-3n. n=8 =>35 and27? crossing asymmetrically; test n=7,8.
for n in [6,7,8]:
 e=a.make('ar25')
 for i in base: o=e.step(GameAction.from_id(i),data={})
 for _ in range(n): o=e.step(GameAction.ACTION4,data={})
 print('n',n,'L',o.levels_completed,o.state)
