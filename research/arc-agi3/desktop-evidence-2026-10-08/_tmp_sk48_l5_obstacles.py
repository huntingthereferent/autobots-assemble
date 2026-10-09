from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4);p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4);p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4);p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for z in p1+p2+p3+p4:e.step(GameAction.from_id(z),data={})
g=e._game
for name in ('mkgqjopcjn','irkeobngyh'):
 print(name,[(s.x,s.y,s.width,s.height) for s in g.current_level.get_sprites_by_name(name)],flush=True)
print('board',g.lqwkgffeb.x,g.lqwkgffeb.y,g.lqwkgffeb.pixels.shape,flush=True)
