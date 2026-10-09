from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
def board(seq):
 e=a.make('ar25');o=None
 for z in PRE+seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy()
R=board([])
# compare returned L2 against its first re-expression X, preserving whole board;
# ask which exact relation in R is transformed, not whether it is "closer".
X=board([7])
D=R!=X
print("R->X changed",np.count_nonzero(D))
# For every color pair, count preserved vs rewritten cells.
for c in sorted(set(map(int,R.ravel()))):
 m=R==c; n=int(m.sum()); same=int(np.count_nonzero(m & (X==c)))
 print("color",c,"n",n,"preserved",same,"rewritten",n-same)
# marker coordinates from R: inspect their exact images in X.
for label,pts in [('L',[(4,46),(7,46),(10,46),(10,49),(10,52)]),('R',[(52,46),(55,46),(58,46),(52,49),(52,52)])]:
 print(label,[(p,int(R[p[1],p[0]]),int(X[p[1],p[0]])) for p in pts])
# Determine if the mirrored marker relation itself survives R->X anywhere by locating marker colors.
for name,B in [('R',R),('X',X)]:
 for c in [0,11]:
  yy,xx=np.where(B==c); print(name,c,list(zip(xx.tolist(),yy.tolist()))[:40],"N",len(xx))
