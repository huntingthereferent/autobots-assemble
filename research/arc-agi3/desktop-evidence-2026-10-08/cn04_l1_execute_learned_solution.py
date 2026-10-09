from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
# select object 1 at the previously discovered public display coordinate
r=e.step(GameAction.from_id(6),data={"x":41,"y":31})
sp=list(e._game.current_level.get_sprites())
print("SEL",sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1)
# learned order-4 operator once
r=e.step(GameAction.from_id(5),data={})
print("AFTER_OP",[(s.x,s.y,s.width,s.height) for s in e._game.current_level.get_sprites()],"LC",r.levels_completed)
# move object 1 from (12,9) -> (2,8)
for i in range(10):
 r=e.step(GameAction.from_id(3),data={})
 print("L",i+1,"POS",e._game.xseexqzst.x,e._game.xseexqzst.y,"LC",r.levels_completed,"STATE",r.state.name)
 if r.levels_completed>0 or r.state.name!="NOT_FINISHED":break
if r.levels_completed==0:
 r=e.step(GameAction.from_id(1),data={})
 print("UP","POS",e._game.xseexqzst.x,e._game.xseexqzst.y,"LC",r.levels_completed,"STATE",r.state.name)
print("FINAL","LC",r.levels_completed,"STATE",r.state.name,"LEVEL",e._game.level_index)
