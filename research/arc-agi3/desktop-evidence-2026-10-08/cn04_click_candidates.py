from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
pts=[(38,29),(39,29),(40,29),(38,30),(39,30),(40,30),(41,31),(42,32),(45,35)]
for x,y in pts:
 e=a.make("cn04")
 g=e._game.camera.display_to_grid(x,y)
 try:
  e.step(GameAction.from_id(6),data={"x":x,"y":y})
  sp=list(e._game.current_level.get_sprites())
  sel=sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
  print(x,y,g,sel)
 except Exception as ex:
  print(x,y,g,"ERR",type(ex).__name__)
