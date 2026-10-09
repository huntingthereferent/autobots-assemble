from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
p6=(1,1,2,1,2,4,4,1,4,1,1,1,3,3,4,4,1,1,4,4,1,1,4,2,2,1,1,3,1,2,3,3,3,3,1,2,3,3,2,2,2,2,1,4,4,4,3,3,3,1,1,1,1,1,1,4,4,4,4,4,4,2,4,4,1,1,4,2,2,2,2,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for z in p1+p2+p3+p4+p5+p6:e.step(GameAction.from_id(z),data={})
g=e._game
o=g.wsoslqeku[0];seen={}
for t in range(36):
 key=(o._sprite.x,o._sprite.y,o._dir)
 if key in seen:print('CYCLE',seen[key],t,'LENGTH',t-seen[key],flush=True);break
 seen[key]=t
 print('PHASE',t,key,flush=True);o.step()
