from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
# Higher-layer generators: A=idempotent first quotient class, B=3,C=4,D=5,E=BC=CB=DD
G={'A':[1],'B':[3],'C':[4],'D':[5],'E':[3,4]}
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
# recurse E itself; compare with D^(2n), (BC)^n, (CB)^n -- same operation/output contract
print('E RECURSION / REPRESENTATION INDEPENDENCE')
for n in range(1,9):
 reps={'E^n':[3,4]*n,'CB^n':[4,3]*n,'D^2n':[5]*(2*n)}
 out={k:run(v) for k,v in reps.items()}
 bs=[x[0] for x in out.values()]
 eq=all(np.array_equal(bs[0],b) for b in bs[1:])
 prev=run([3,4]*(n-1))[0] if n>1 else run([])[0]
 b,o=out['E^n']
 print(n,'all_equal',eq,'stepdiff',np.count_nonzero(prev!=b),'L',o.levels_completed,o.state)
# algebra: compose E with remaining generators both orders and identify exact equalities.
print('\nE COMMUTATORS')
for k,s in G.items():
 if k=='E':continue
 x,ox=run(G['E']+s);y,oy=run(s+G['E'])
 print('E',k,'commdiff',np.count_nonzero(x!=y),'L',ox.levels_completed,oy.levels_completed,ox.state,oy.state)
# Does any higher generator applied after E^n close the level? finite quotient edge audit, not history search.
print('\nE^n NEXT TRANSFORM')
for n in range(0,9):
 for k,s in G.items():
  b,o=run([3,4]*n+s)
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state):
   print('BOUNDARY n',n,'g',k,'L',o.levels_completed,o.state)
