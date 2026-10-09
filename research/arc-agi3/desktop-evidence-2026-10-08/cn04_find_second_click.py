from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
for y in range(25,55):
 for x in range(35,55):
  e=a.make("cn04")
  try:e.step(GameAction.from_id(6),data={"x":x,"y":y})
  except:continue
  sp=list(e._game.current_level.get_sprites())
  sel=sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
  if sel==1:
   print("FOUND",x,y,"GRID",e._game.camera.display_to_grid(x,y))
   raise SystemExit
print("NONE")
