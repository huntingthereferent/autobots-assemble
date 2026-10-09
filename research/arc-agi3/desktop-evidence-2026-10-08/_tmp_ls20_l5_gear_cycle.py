from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3+p4:r=e.step(GameAction.from_id(z),data={})
g=e._game
for i,o in enumerate(g.wsoslqeku):
 print('OBJECT',i,'PARENT',(o.bfdcztirdu.x,o.bfdcztirdu.y,o.bfdcztirdu.width,o.bfdcztirdu.height),'MOVER',(o._sprite.x,o._sprite.y),'DIR',o._dir,flush=True)
for tick in range(1,81):
 for o in g.wsoslqeku:o.step()
 if tick<=30 or tick%5==0:
  print('TICK',tick,[(o._sprite.x,o._sprite.y,o._dir) for o in g.wsoslqeku],flush=True)
