from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
print("LC",r.levels_completed,"LEVEL",e._game.level_index,"TOTAL_LEVELS",len(e._game._levels))
sp=list(e._game.current_level.get_sprites())
print("N",len(sp),"SEL",sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1)
for i,s in enumerate(sp):
 A=np.array(s.render(),dtype=int)
 print("S",i,"POS",s.x,s.y,"SH",A.shape,"M8",int((A==8).sum()),"M13",int((A==13).sum()),"UNIQ",sorted(set(A.flatten().tolist())))
