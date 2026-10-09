from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3:r=e.step(GameAction.from_id(z),data={})
g=e._game
for p in g.hasivfwip:
 n=p.ullzqnksoj(g.gudziatsk)
 print('LAUNCH',(p.sprite.x+p.dx,p.sprite.y+p.dy),'LAND',(p.sprite.x+p.dx+5*n*p.dx,p.sprite.y+p.dy+5*n*p.dy),'CELLS',n,'DIR',(p.dx,p.dy),flush=True)
