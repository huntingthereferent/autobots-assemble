from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE=[3]*5+[2]*10
# Extract exact two 9x9 carriers from returned L2 and compare transforms of their patterned content.
e=a.make('ar25');o=None
for z in PRE:o=e.step(GameAction.from_id(z),data={})
B=o.frame[0].copy()
L=B[45:54,3:12]; R=B[45:54,51:60]
print("L\n",L); print("R\n",R)
# exact geometric transforms; whole-board source remains parent evidence
trs={'id':L,'rot90':np.rot90(L,1),'rot180':np.rot90(L,2),'rot270':np.rot90(L,3),
'flipLR':np.fliplr(L),'flipUD':np.flipud(L),'transpose':L.T,'anti':np.fliplr(np.flipud(L.T))}
for k,v in trs.items(): print(k,"diff",np.count_nonzero(v!=R))
# Now test whether simple actions move returned L2 toward exact carrier correspondence,
# measured only as diagnostic witness; stop immediately if environment closes.
for act in [1,2,3,4,5,7]:
 e=a.make('ar25');o=None
 for z in PRE:o=e.step(GameAction.from_id(z),data={})
 print("\nACT",act)
 for n in range(1,25):
  o=e.step(GameAction.from_id(act),data={})
  if o.levels_completed>1:
   print("SOLVED",act,n,o.levels_completed); raise SystemExit
  if 'GAME_OVER' in str(o.state): print("GAMEOVER",n); break
  X=o.frame[0]
  # locate candidate 9x9 windows at original carrier x ranges, compare all transforms
  l=X[45:54,3:12]; r=X[45:54,51:60]
  best=min((np.count_nonzero(v!=r),k) for k,v in {'id':l,'r90':np.rot90(l),'r180':np.rot90(l,2),'r270':np.rot90(l,3),'lr':np.fliplr(l),'ud':np.flipud(l),'t':l.T}.items())
  if n<=3 or best[0]==0: print(n,best)
