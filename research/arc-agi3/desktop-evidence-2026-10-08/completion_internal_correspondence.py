from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy(),o
# Successful L1 just-before and close.
P,_=run([3]*5+[2]*9); C,oc=run([3]*5+[2]*10)
# L2 B8 and correct geometric registration.
base=[3]*5+[2]*10+[7,5]
B,_=run(base); R,orr=run(base+[4]*4+[2]*8)
# Compare the completion-pair windows exactly.
# L1 mover pre anchor51,42; receiver51,45; after anchor receiver.
print("L1 pre mover/receiver overlap rows:")
for y in range(42,54):
 print(y,''.join(str(int(P[y,x])).rjust(2) for x in range(51,60)))
print("L1 returned:")
for y in range(45,54):
 print(y,''.join(str(int(C[y,x])).rjust(2) for x in range(51,60)))
print("L2 registered target window x3..17 y42..53:")
for y in range(42,54):
 print(y,''.join(str(int(R[y,x])).rjust(2) for x in range(3,18)))
# quantify whether 72 color4 actually equals receiver coords after sequence
recv={(x,y) for y in range(42,54) for x in range(3,18) if B[y,x]==11}
mov={(x,y) for y,x in zip(*np.where(R==4))}
print("receiver72",len(recv),"color4_after",len(mov),"intersection",len(recv&mov),"missing",len(recv-mov),"extra",len(mov-recv))
# track black 8 markers and gray carrier relative to registration; maybe complementary pair must co-register too
for name,A in [('B8',B),('REG',R)]:
 for c in [0,5,4,11]:
  yy,xx=np.where(A==c)
  print(name,c,len(xx),(int(xx.min()),int(xx.max()),int(yy.min()),int(yy.max())))
