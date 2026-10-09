from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
parents={
 'A':([3]*13+[4]*21)*2+[7]*59,
 'B':([4]*9+[3]*21)*2+[7]*47,
}
def board(seq):
 e=a.make('ar25')
 for z in pre+seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy(),o
for name,p in parents.items():
 x,o=board(p)
 print("\nPARENT",name,hashlib.sha256(x.tobytes()).hexdigest()[:12])
 # The current state witnesses 3 and 4 equally at one step. Apply each once,
 # then compare complete returned states and their immediately available relations.
 outs={}
 for first in [3,4]:
  y,oo=board(p+[first]); outs[first]=y
  print(" first",first,"hash",hashlib.sha256(y.tobytes()).hexdigest()[:12],"lvl",oo.levels_completed,oo.state)
  for nxt in [1,2,3,4,5,7]:
   z,oz=board(p+[first,nxt])
   print("  next",nxt,"diff",np.count_nonzero(y!=z),"lvl",oz.levels_completed,oz.state)
   if oz.levels_completed>1:
    print("SOLVED",name,first,nxt); raise SystemExit
 print(" 3_vs_4_exact",np.array_equal(outs[3],outs[4]),"diff",np.count_nonzero(outs[3]!=outs[4]))
