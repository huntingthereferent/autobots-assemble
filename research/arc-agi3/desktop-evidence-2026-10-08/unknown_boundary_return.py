from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# At UNKNOWN boundary, do not invent a derived representation.
# Ask whether the whole-state evidence itself witnesses an earned change of relation:
# follow each nonfixed relation to its fixed/terminal boundary, then apply each permitted action ONCE.
def boundary(rel):
 e=a.make('ar25')
 for z in pre:o=e.step(GameAction.from_id(z),data={})
 prev=o.frame[0].copy()
 for n in range(1,65):
  o=e.step(GameAction.from_id(rel),data={}); cur=o.frame[0].copy()
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): return None,n,o
  if np.array_equal(prev,cur): return (e,cur),n,o
  prev=cur
 return None,n,o
for rel in [1,2,3,4,7]: # 5 terminates, so no valid returned input
 got,n,o=boundary(rel)
 print("\nBOUNDARY",rel,"at",n,o.levels_completed,o.state)
 if got is None: continue
 # recreate boundary separately per permitted action so every witness shares exact parent
 for act in [1,2,3,4,5,7]:
  ee=a.make('ar25')
  for z in pre:oo=ee.step(GameAction.from_id(z),data={})
  prev=oo.frame[0].copy()
  for k in range(1,n+1):
   oo=ee.step(GameAction.from_id(rel),data={}); cur=oo.frame[0].copy()
  b=cur.copy()
  oo=ee.step(GameAction.from_id(act),data={}); c=oo.frame[0].copy()
  print(" next",act,"diff",np.count_nonzero(b!=c),"lvl",oo.levels_completed,oo.state)
  if oo.levels_completed>1: print("SOLVED",rel,n,act)
