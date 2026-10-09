from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out
def vis(g):return [s for s in g.current_level.get_sprites() if s.is_visible]
def selidx(e):
 sp=vis(e._game)
 return sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
def select(e,idx):
 if selidx(e)==idx:return
 sp=vis(e._game);s=sp[idx];A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp];e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if selidx(e)==idx:return
 raise RuntimeError(idx)
def move(e,idx,x,y,lc):
 global r
 select(e,idx)
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>lc:return
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>lc:return

e=a.make("cn04");r=None
# L1
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:r=e.step(GameAction.from_id(z),data=data)
# L2 corrected
move(e,1,8,12,1);move(e,2,3,9,1);select(e,3)
for _ in range(3):r=e.step(GameAction.from_id(5),data={})
move(e,3,12,14,1)
assert r.levels_completed==2
print("L3START",[(s.x,s.y,s.rotation,s.width,s.height) for s in vis(e._game)])

# candidate
move(e,0,9,5,2)
select(e,1)
for _ in range(2):r=e.step(GameAction.from_id(5),data={})
move(e,1,3,4,2)
move(e,2,9,3,2)
print("RESULT","LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
print("NOW",[(s.x,s.y,s.rotation,s.width,s.height) for s in vis(e._game)])
assert r.levels_completed>=3
print("PASS L3 empirical-cycle exact cover")
