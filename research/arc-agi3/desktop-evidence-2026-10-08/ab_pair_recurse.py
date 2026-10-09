from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Continue AB on one exact returned board: each 3/4 movement is followed by the
# directly re-enabled 7. Preserve whole returned board and stop on equality/terminal/solve.
base=([3]*13+[4]*21)*2+[7]*59
for first in [3,4]:
 e=a.make('ar25')
 for z in pre+base:o=e.step(GameAction.from_id(z),data={})
 prev=o.frame[0].copy(); seen={hashlib.sha256(prev.tobytes()).hexdigest():0}
 print("\nREL",first,"then7")
 for n in range(1,80):
  for z in [first,7]:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED pair",n,"after",z,"lvl",o.levels_completed,o.state); raise SystemExit
   if 'GAME_OVER' in str(o.state):
    print("GAME_OVER pair",n,"after",z); break
  cur=o.frame[0].copy(); diff=np.count_nonzero(prev!=cur)
  hh=hashlib.sha256(cur.tobytes()).hexdigest()
  print(n,"pairdiff",diff,"lvl",o.levels_completed,o.state,"seen",seen.get(hh))
  if 'GAME_OVER' in str(o.state) or diff==0 or hh in seen: break
  seen[hh]=n; prev=cur
