from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
def fresh():
 e=a.make('ar25'); o=None
 for z in PRE:o=e.step(GameAction.from_id(z),data={})
 return e,o
def clk(e,p): return e.step(GameAction.from_id(6),data={'x':p[0],'y':p[1]})
def h(o): return hashlib.sha256(o.frame[0].tobytes()).hexdigest()[:12]
W=0; classes={}
def wall(desc,o):
 global W
 if o.levels_completed>1:
  print("SOLVED_AT",W+1,desc,"LEVELS",o.levels_completed,o.state); raise SystemExit
 W+=1; print("WALL",W,desc,"lvl",o.levels_completed,o.state,"h",h(o))
# 20 coordinates directly present as structural landmarks in exact returned board:
pts=[
(4,46),(7,46),(10,46),(10,49),(10,52),
(52,46),(55,46),(58,46),(52,49),(52,52),
(3,45),(11,53),(51,45),(59,53),
(30,0),(31,31),(32,62),(63,14),(63,58),(63,63)]
# Five exact returned-state continuations per witnessed coordinate = 100 walls max.
# Each experiment starts from the exact L2 return; no accumulated search history.
for p in pts:
 # 1: click itself
 e,o=fresh(); before=o.frame[0].copy(); o=clk(e,p)
 classes.setdefault(h(o),[]).append(p)
 wall(f"{p} click d={np.count_nonzero(before!=o.frame[0])}",o)
 # 2: same click on its returned state
 b=o.frame[0].copy(); o=clk(e,p)
 wall(f"{p} click->same d={np.count_nonzero(b!=o.frame[0])}",o)
 # 3-5: from the exact one-click return, direct surviving simple relations 3,4,5
 for act in (3,4,5):
  ee,oo=fresh(); oo=clk(ee,p); b=oo.frame[0].copy()
  oo=ee.step(GameAction.from_id(act),data={})
  wall(f"{p} click->{act} d={np.count_nonzero(b!=oo.frame[0])}",oo)
print("HUNDRED_WALLS_DONE",W,"ONE_CLICK_CLASSES",len(classes))
for k,v in classes.items(): print("CLASS",k,"N",len(v),"PTS",v)
