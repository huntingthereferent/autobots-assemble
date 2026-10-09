from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
def get(seq):
 e=a.make('ar25')
 for z in pre+seq:o=e.step(GameAction.from_id(z),data={})
 b=o.frame[0].copy()
 return b,o
def h(b): return hashlib.sha256(b.tobytes()).hexdigest()[:12]
# Test whether the recursively returned boundaries are genuinely new or exact returns
# to already witnessed whole states. No semantic compression: exact whole-board equality.
seqs={
 'root':[],
 'common7*':[7,7],
 '3*':[3]*13,
 '4*':[4]*9,
 '3*4*':[3]*13+[4]*21,
 '4*3*':[4]*9+[3]*21,
 '3*7*':[3]*13+[7]*13,
 '4*7*':[4]*9+[7]*9,
}
boards={}
for n,s in seqs.items():
 b,o=get(s); boards[n]=b
 print(n,h(b),o.levels_completed,o.state)
print("\nEXACT EQUALITIES")
names=list(boards)
for i in range(len(names)):
 for j in range(i+1,len(names)):
  if np.array_equal(boards[names[i]],boards[names[j]]):
   print(names[i],"==",names[j])
# If a cycle is exact, its repetition cannot supply new evidence. Verify one repeated cycle.
for name,seq in [('cycle34',[3]*13+[4]*21),('cycle43',[4]*9+[3]*21)]:
 b1,o1=get(seq); b2,o2=get(seq+seq)
 print(name,"repeat_equal",np.array_equal(b1,b2),"diff",np.count_nonzero(b1!=b2),o2.levels_completed,o2.state)
