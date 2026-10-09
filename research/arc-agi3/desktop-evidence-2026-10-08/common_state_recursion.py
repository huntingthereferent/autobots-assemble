from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
def env(seq=[]):
 e=a.make('ar25'); o=None
 for z in PRE+seq:
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
 return e,o
def hh(o): return hashlib.sha256(o.frame[0].tobytes()).hexdigest()[:12]
def d(a,b): return int(np.count_nonzero(a!=b))
# Common returned state X is PRE+[7]. Keep X as referent; audit compositions directly.
X=[7]
units=[[3,7],[4,7],[3,4],[4,3],[5,5],[3,5],[5,3],[4,5],[5,4],[3,7,4,7],[4,7,3,7]]
print("X")
e,o=env(X); root=o.frame[0].copy(); print(hh(o),o.levels_completed,o.state)
for u in units:
 e,o=env(X); prev=o.frame[0].copy(); seen={hh(o):0}
 for n in range(1,35):
  terminal=False
  for z in u:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",u,"repeat",n,"after",z,"lvl",o.levels_completed); raise SystemExit
   if 'GAME_OVER' in str(o.state): terminal=True; break
  cur=o.frame[0].copy(); h=hh(o)
  if terminal: print("WALL",u,"GAME_OVER",n); break
  if h in seen: print("WALL",u,"RETURN",n,"to",seen[h],"diff",d(prev,cur)); break
  if d(prev,cur)==0: print("WALL",u,"FIXED",n); break
  seen[h]=n; prev=cur
 else: print("OPEN",u,"35")
