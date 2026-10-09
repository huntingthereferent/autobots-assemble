from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Recurse the relation witnessed at each returned boundary.
# No branch choice by score: at a fixed point, continue only with relations that actually move that returned board.
def step(e,act):
 o=e.step(GameAction.from_id(act),data={}); return o,o.frame[0].copy()
def to_fixed(e,act,limit=70):
 prev=e._last_observation.frame[0].copy() if hasattr(e,'_last_observation') and e._last_observation else None
 # caller supplies prev separately instead
def run(seq):
 e=a.make('ar25')
 for z in pre:o=e.step(GameAction.from_id(z),data={})
 prev=o.frame[0].copy()
 for act in seq:
  o=e.step(GameAction.from_id(act),data={}); prev=o.frame[0].copy()
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
 return e,o,prev
# Earned parents: 3 repeated to fixed uses 13 presses; 4 repeated to fixed uses 9.
parents={'3*':[3]*13,'4*':[4]*9}
# At 3*: survivors 4,5,7. At 4*: survivors 3,5,7.
# Continue each survivor until it itself fixes/terminates/solves.
for name,prefix in parents.items():
 for rel in ([4,5,7] if name=='3*' else [3,5,7]):
  e=a.make('ar25')
  for z in pre+prefix:o=e.step(GameAction.from_id(z),data={})
  prev=o.frame[0].copy()
  print("\n",name,"=>",rel)
  for n in range(1,70):
   o=e.step(GameAction.from_id(rel),data={}); cur=o.frame[0].copy()
   diff=np.count_nonzero(prev!=cur)
   print(n,diff,o.levels_completed,o.state)
   if o.levels_completed>1:
    print("SOLVED L2",prefix+[rel]*n); raise SystemExit
   if 'GAME_OVER' in str(o.state) or diff==0: break
   prev=cur
