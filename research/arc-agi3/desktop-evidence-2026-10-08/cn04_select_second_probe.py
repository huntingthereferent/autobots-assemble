from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
sp=list(e._game.current_level.get_sprites())
print("BEFORE_SEL",sp.index(e._game.xseexqzst))
for xy in [(12,9),(13,10),(15,12),(240,180)]:
 ee=a.make("cn04")
 try:
  rr=ee.step(GameAction.from_id(6),data={"x":xy[0],"y":xy[1]})
  sp2=list(ee._game.current_level.get_sprites())
  print("CLICK",xy,"SEL",sp2.index(ee._game.xseexqzst) if ee._game.xseexqzst in sp2 else -1)
 except Exception as ex: print("CLICK",xy,"ERR",type(ex).__name__,str(ex))
