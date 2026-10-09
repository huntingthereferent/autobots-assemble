from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
P6=(4,4,2,4,6,2,2,4,4,2,1,4,2,3,1,3,2,6,4,4,4,3,3,3,3,2,2,4,1,3,1,4,6,2,2,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for z in prefix+P6:
 if z==6:
  g=e._game;other=next(k for k in g.xpmcmtbcv if k!=g.vzvypfsnt)
  e.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
 else:e.step(GameAction.from_id(z),data={})
g=e._game
print('LEVEL',g._current_level_index,'ACTIVE',g.vzvypfsnt.name,flush=True)
for k,m in g.xpmcmtbcv.items():
 print('PAIR',k.name,(k.x,k.y,k.rotation),'BODY',[(s.x,s.y) for s in g.mwfajkguqx[k]],'TARGET',[(int(t.pixels[1,1])) for t in g.vjfbwggsd[m]],flush=True)
print('PADS',[(int(t.x),int(t.y),int(t.pixels[1,1])) for t in g.vbelzuaian],flush=True)
print('OBSTACLES',[(s.x,s.y) for s in g.current_level.get_sprites_by_name('mkgqjopcjn')],flush=True)
print('GUIDES',[(s.x,s.y,s.rotation) for s in g.current_level.get_sprites_by_name('irkeobngyh')],flush=True)
print('BOARD',g.lqwkgffeb.x,g.lqwkgffeb.y,g.lqwkgffeb.pixels.shape,flush=True)
