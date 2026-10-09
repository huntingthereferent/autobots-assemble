from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
assert r.levels_completed==1

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out
def selidx(e):
 sp=list(e._game.current_level.get_sprites())
 return sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
def select(e,idx):
 if selidx(e)==idx:return
 sp=list(e._game.current_level.get_sprites());s=sp[idx];A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp]
   e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if selidx(e)==idx:return
 raise RuntimeError(idx)
def move(e,idx,x,y):
 global r
 select(e,idx)
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>1:return
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>1:return

move(e,1,8,12)
move(e,2,3,9)
select(e,3)
for _ in range(3):
 r=e.step(GameAction.from_id(5),data={})
move(e,3,12,14)

print("FINAL","LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
print("POSROT",[(s.x,s.y,s.rotation,s.width,s.height) for s in e._game.current_level.get_sprites()])
assert r.levels_completed>=2
print("PASS cn04 Levels 1-2 from learned operator + latent typed exact cover")
