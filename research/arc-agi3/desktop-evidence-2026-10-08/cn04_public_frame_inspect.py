from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
r=e.step(GameAction.from_id(7),data={})
f=r.frame
print("TYPE",type(f),"LEN",len(f))
for i,x in enumerate(f):
 print("ITEM",i,type(x))
 if isinstance(x,np.ndarray):
  print(" SH",x.shape,"DT",x.dtype,"UNIQ",np.unique(x)[:30].tolist())
 else:
  print(" REPR",repr(x)[:500])
