from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
dots=[(46,4),(46,7),(46,10),(49,10),(52,10),(46,52),(46,55),(46,58),(49,52),(52,52)]
edge=[(63,58),(63,59),(63,60),(63,61),(63,62),(63,63)]
def make(seq=[]):
 e=a.make('ar25'); o=None
 for z in PRE+seq:o=e.step(GameAction.from_id(z),data={})
 return e,o
def click(e,x,y): return e.step(GameAction.from_id(6),data={'x':x,'y':y})
def diff(a,b): return np.count_nonzero(a!=b)
W=0
def wall(s):
 global W; W+=1; print("WALL",W,s)
# 1-4: recursive click same witnessed coordinate twice: does returned state carry relation?
for pt in [dots[0],dots[4],dots[5],dots[9]]:
 e,o=make(); b=o.frame[0].copy(); o=click(e,*pt); c=o.frame[0].copy(); o2=click(e,*pt); d=o2.frame[0].copy()
 if o2.levels_completed>1: print("SOLVED same",pt,o2.levels_completed); raise SystemExit
 wall(f"same {pt}: d1={diff(b,c)} d2={diff(c,d)} state={o2.state}")
# 5-6: click complete witnessed dot sets in their board order
for label,pts in [('black',dots[:5]),('navy',dots[5:])]:
 e,o=make(); prev=o.frame[0].copy(); terminal=False
 for i,p in enumerate(pts,1):
  o=click(e,*p)
  if o.levels_completed>1: print("SOLVED",label,i,o.levels_completed); raise SystemExit
  if 'GAME_OVER' in str(o.state): terminal=True; break
 wall(f"{label} set: finaldiff={diff(prev,o.frame[0])} state={o.state}")
# 7-8: corresponding paired dots, two orders. Coordinates are exact board witnesses.
for rev in [False,True]:
 e,o=make(); pairs=list(zip(dots[:5],dots[5:]))
 if rev:pairs=pairs[::-1]
 for p,q in pairs:
  o=click(e,*p)
  if o.levels_completed>1: print("SOLVED pair p",p); raise SystemExit
  o=click(e,*q)
  if o.levels_completed>1: print("SOLVED pair q",q); raise SystemExit
  if 'GAME_OVER' in str(o.state): break
 wall(f"paired rev={rev}: lvl={o.levels_completed} state={o.state}")
# 9: recursively click carried edge cells in witnessed progression
e,o=make()
for p in edge:
 o=click(e,*p)
 if o.levels_completed>1: print("SOLVED edge",p,o.levels_completed); raise SystemExit
 if 'GAME_OVER' in str(o.state): break
wall(f"edge sequence lvl={o.levels_completed} state={o.state}")
# 10: after one dot click, inspect direct simple-action relations on exact returned board
e,o=make(); o=click(e,*dots[0]); parent=o.frame[0].copy(); vals=[]
for act in [1,2,3,4,5,7]:
 ee,oo=make(); oo=click(ee,*dots[0]); b=oo.frame[0].copy(); oo=ee.step(GameAction.from_id(act),data={})
 if oo.levels_completed>1: print("SOLVED dot->simple",act,oo.levels_completed); raise SystemExit
 vals.append((act,diff(b,oo.frame[0]),str(oo.state)))
wall("dot->simple "+str(vals))
print("TEN_WALLS_DONE",W)
