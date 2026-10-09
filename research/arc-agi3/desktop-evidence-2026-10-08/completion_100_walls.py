from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
L1=[3]*5
# completion-only witness: find which fixed-board contacts/positions distinguish closing A2
e=a.make('ar25'); o=None
for z in L1:o=e.step(GameAction.from_id(z),data={})
print("=== POSITIVE COMPLETION WITNESS ===")
for n in range(1,11):
 before=o.frame[0].copy(); o=e.step(GameAction.from_id(2),data={}); B=o.frame[0]
 # black marker bbox and distances to bottom/right/divider
 yy,xx=np.where(B==0); bb=(xx.min(),xx.max(),yy.min(),yy.max())
 print("A2",n,"lvl",o.levels_completed,"bbox",bb,"bottom_gap",62-bb[3],"divider_gap",30-bb[1])
print("CLOSE_AT",10)

# 100 completion-referent walls from L2's movable 8-path.
# Each wall is a distinct absolute translation endpoint on the native 3-lattice.
# We test endpoints, not arbitrary action histories: 10 x-positions * 10 y-positions.
# Translation realization is canonical from the witnessed B8 state.
BASE=[3]*5+[2]*10+[7,5]
def fresh():
 e=a.make('ar25');o=None
 for z in BASE:o=e.step(GameAction.from_id(z),data={})
 return e,o
# B8 anchor min=(46,19). Native translations in steps of 3.
# choose 10x10 structurally distributed endpoints that remain mostly in-board.
xsteps=list(range(-9,1))   # mins 19..46
ysteps=list(range(-6,4))   # mins 1..28
walls=0
for iy,dy in enumerate(ysteps):
 for ix,dx in enumerate(xsteps):
  e,o=fresh()
  # canonical horizontal then vertical translation; no search/order branching
  actx=3 if dx<0 else 4
  acty=1 if dy<0 else 2
  terminal=False
  for _ in range(abs(dx)):
   o=e.step(GameAction.from_id(actx),data={})
   if o.levels_completed>1:
    print("SOLVED wall",walls+1,"dxdy",dx,dy,"during X","lvl",o.levels_completed); raise SystemExit
   if 'GAME_OVER' in str(o.state): terminal=True; break
  if not terminal:
   for _ in range(abs(dy)):
    o=e.step(GameAction.from_id(acty),data={})
    if o.levels_completed>1:
     print("SOLVED wall",walls+1,"dxdy",dx,dy,"during Y","lvl",o.levels_completed); raise SystemExit
    if 'GAME_OVER' in str(o.state): terminal=True; break
  walls+=1
  B=o.frame[0]; yy,xx=np.where(B==0)
  bb=(int(xx.min()),int(xx.max()),int(yy.min()),int(yy.max())) if len(xx) else None
  print("WALL",walls,"dxdy",dx,dy,"bbox",bb,"state",o.state,"lvl",o.levels_completed)
print("TOTAL_WALLS",walls,"NO_L2_CLOSURE")
