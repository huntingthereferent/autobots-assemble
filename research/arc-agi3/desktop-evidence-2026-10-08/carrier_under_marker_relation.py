from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
# Witnessed marker transform is LR reflection. Ask whether carrier occupancy satisfies same transform.
def get(seq):
 e=a.make('ar25');o=None
 for z in PRE+seq:
  o=e.step(GameAction.from_id(z),data={})
 return e,o
def carrier_relation(B):
 L=B[45:54,3:12]; R=B[45:54,51:60]
 # compare occupancy relative to background 9, abstracting colors but not geometry
 LO=L!=9; RO=R!=9
 return int(np.count_nonzero(np.fliplr(LO)!=RO)),LO,RO
e,o=get([]); B=o.frame[0]; print("ROOT carrier LR occupancy diff",carrier_relation(B)[0])
# Track only the witnessed carrier relation under each permitted simple movement.
for act in [1,2,3,4,5,7]:
 e,o=get([]); best=(999,None)
 print("\nACT",act)
 for n in range(1,70):
  o=e.step(GameAction.from_id(act),data={})
  if o.levels_completed>1: print("SOLVED",act,n); raise SystemExit
  if 'GAME_OVER' in str(o.state): print("GAMEOVER",n); break
  q=carrier_relation(o.frame[0])[0]
  if q<best[0]: best=(q,n); print("best",best)
  if q==0: print("EXACT",n)
 print("FINALBEST",best)
