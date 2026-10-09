from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque,Counter,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL); ROOT=[3]*5+[2]*10+[7,5]+[2]*5+[5]; acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Root held exchange support: cells that were navy before down5 and yellow after down5+A5.
_,_,before=run([3]*5+[2]*10+[7,5]+[2]*4)
_,_,root=run(ROOT)
held=set(map(tuple,np.argwhere((before==11)&(root==4))))
print("HELD_N",len(held),sorted(held))
def sig(B):
 vals=Counter(int(B[p]) for p in held)
 return tuple(sorted(vals.items()))
print("ROOTSIG",sig(root))
# Recreate first 300 exact-state recursion, but classify every returned board by colors on held support.
seen={root.tobytes():()};q=deque([()]);classes=defaultdict(list);classes[sig(root)].append(())
edges=0
while q and edges<300:
 h=q.popleft()
 for z in acts:
  e,o,A=run(ROOT+list(h));r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();edges+=1
  if r.levels_completed>1: print("SOLVED",ROOT+list(h)+[z]);raise SystemExit
  k=B.tobytes()
  if r.state.name=="NOT_FINISHED" and k not in seen:
   nh=h+(z,);seen[k]=nh;q.append(nh);classes[sig(B)].append(nh)
  if edges>=300:break
print("CLASSES",len(classes))
for s,hs in sorted(classes.items(),key=lambda kv:(-len(kv[1]),kv[0])):
 print("SIG",s,"N",len(hs),"MIN",min(map(len,hs)),"REP",hs[0])
# Only recurse representatives of classes where held support remains entirely yellow (persistent exchange).
persist=[hs[0] for s,hs in classes.items() if s==((4,len(held)),)]
print("PERSIST_REPS",persist)
walls=0
for h in persist:
 for z in acts:
  e,o,A=run(ROOT+list(h));r=e.step(GameAction.from_id(z),data={});walls+=1
  if r.levels_completed>1: print("SOLVED_PERSIST",ROOT+list(h)+[z]);raise SystemExit
print("PERSIST_WALLS",walls)
