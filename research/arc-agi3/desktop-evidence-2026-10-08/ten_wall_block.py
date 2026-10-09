from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
# Ten-wall block. Whole board is referent. We test exact returned-state continuations only.
# Existing late fixed output A is the starting witness.
BASE=([3]*13+[4]*21)*2+[7]*59
def run(seq):
 e=a.make('ar25')
 o=None
 for z in PRE+seq:
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
 return e,o
def frame(o): return o.frame[0].copy()
walls=0
def wall(msg):
 global walls; walls+=1; print("WALL",walls,msg)
# 1-4: direct pair realizations from exact returned state
for pair in ([3,7],[4,7],[3,3],[4,4]):
 e,o=run(BASE); x=frame(o)
 terminal=False
 for n in range(1,70):
  for z in pair:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",pair,n,o.levels_completed); raise SystemExit
   if 'GAME_OVER' in str(o.state): terminal=True; break
  if terminal: break
 wall(f"{pair} -> {'GAME_OVER' if terminal else 'no closure'} at repeat {n}")
# 5-6: alternating 3/7/4/7 orders
for unit in ([3,7,4,7],[4,7,3,7]):
 e,o=run(BASE); terminal=False
 for n in range(1,50):
  for z in unit:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",unit,n,o.levels_completed); raise SystemExit
   if 'GAME_OVER' in str(o.state): terminal=True; break
  if terminal: break
 wall(f"{unit} -> {'GAME_OVER' if terminal else 'no closure'} at repeat {n}")
# 7-8: one 3/4->7 return then switch to opposite pair recursively
for first,unit in [(3,[4,7]),(4,[3,7])]:
 e,o=run(BASE+[first,7]); terminal=False
 for n in range(1,50):
  for z in unit:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED switch",first,unit,n,o.levels_completed); raise SystemExit
   if 'GAME_OVER' in str(o.state): terminal=True; break
  if terminal: break
 wall(f"switch {first},7 -> {unit} => {'GAME_OVER' if terminal else 'no closure'} {n}")
# 9-10: action6 only at board-witnessed coordinates: the visible dot coordinates of exact returned L2,
# and the one-cell carried right-boundary witness. This is not grid brute force.
coords=[(46,4),(46,7),(46,10),(49,10),(52,10),(46,52),(46,55),(46,58),(49,52),(52,52)]
# GameAction 6 requires x/y data; use exact root, one click each.
for label,pts in [('dots',coords),('boundary',[(63,58),(63,59),(63,60),(63,61),(63,62),(63,63)])]:
 solved=False; anychange=0
 for x,y in pts:
  e,o=run([])
  b=frame(o)
  o=e.step(GameAction.from_id(6),data={'x':x,'y':y})
  anychange+=int(np.count_nonzero(b!=frame(o))>0)
  if o.levels_completed>1:
   print("SOLVED click",label,x,y,o.levels_completed); raise SystemExit
 wall(f"click witness {label}: {anychange}/{len(pts)} changed, no L2 closure")
print("TEN_WALLS_DONE",walls)
