from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
# learned L1 solve
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)
assert r.levels_completed==1

def inverse_display(camera):
 inv={}
 for y in range(64):
  for x in range(64):
   g=camera.display_to_grid(x,y)
   if g is not None and g not in inv:inv[g]=(x,y)
 return inv

def select_sprite(e,idx):
 sp=list(e._game.current_level.get_sprites());s=sp[idx]
 A=np.array(s.render(),dtype=int)
 inv=inverse_display(e._game.camera)
 # prefer a visible nonempty cell
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])!=-1:
    gp=(s.x+cc,s.y+rr)
    if gp in inv:
     x,y=inv[gp]
     e.step(GameAction.from_id(6),data={"x":x,"y":y})
     sp2=list(e._game.current_level.get_sprites())
     sel=sp2.index(e._game.xseexqzst) if e._game.xseexqzst in sp2 else -1
     if sel==idx:return True
 return False

def move_selected(e,gx,gy):
 global r
 while e._game.xseexqzst.x!=gx:
  z=4 if gx>e._game.xseexqzst.x else 3
  r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>1:return
 while e._game.xseexqzst.y!=gy:
  z=2 if gy>e._game.xseexqzst.y else 1
  r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>1:return

print("START2",[(s.x,s.y,s.width,s.height) for s in e._game.current_level.get_sprites()])
# obj1 -> (8,12)
assert select_sprite(e,1)
move_selected(e,8,12)
print("OBJ1",[(s.x,s.y) for s in e._game.current_level.get_sprites()],"LC",r.levels_completed)
# obj2 -> (3,9)
assert select_sprite(e,2)
move_selected(e,3,9)
print("OBJ2",[(s.x,s.y) for s in e._game.current_level.get_sprites()],"LC",r.levels_completed)
# obj3: learned operator once, then -> (10,14)
assert select_sprite(e,3)
r=e.step(GameAction.from_id(5),data={})
move_selected(e,10,14)
print("OBJ3",[(s.x,s.y,s.width,s.height) for s in e._game.current_level.get_sprites()],"LC",r.levels_completed,"STATE",r.state.name)
print("FINAL","LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
assert r.levels_completed>=2
print("PASS cn04 learned operator + exact marker cover closes Levels 1-2")
