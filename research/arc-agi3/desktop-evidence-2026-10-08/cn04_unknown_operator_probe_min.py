from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
g=e._game
sp=list(g.current_level.get_sprites())
print("N",len(sp))
print("SEL",sp.index(g.xseexqzst) if g.xseexqzst in sp else -1)
print("BASE",[(s.x,s.y,s.width,s.height,bool(s.is_visible)) for s in sp])
for z in [1,2,3,4,5,7]:
 ee=copy.deepcopy(e); gg=ee._game
 b=[(s.x,s.y,s.width,s.height,bool(s.is_visible)) for s in gg.current_level.get_sprites()]
 r=ee.step(GameAction.from_id(z),data={})
 a1=[(s.x,s.y,s.width,s.height,bool(s.is_visible)) for s in gg.current_level.get_sprites()]
 print("A",z,"CH",[i for i,(x,y) in enumerate(zip(b,a1)) if x!=y],"AFTER",a1,"STATE",r.state.name)
