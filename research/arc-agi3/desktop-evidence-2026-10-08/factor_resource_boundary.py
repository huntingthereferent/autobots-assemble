from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
# Start at exact returned level2 BEFORE A5. Test whether boundary consumption is common
# to each structure-changing action: this tells us what evidence to factor out.
def run(seq):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 root=o.frame[0].copy()
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 return root,o.frame[0].copy(),o
for act in [1,2,3,4,5,7]:
 r,f,o=run([act]);ys,xs=np.where(r!=f)
 edge=[(y,int(r[y,63]),int(f[y,63])) for y in range(64) if r[y,63]!=f[y,63]]
 print('A',act,'diff',len(xs),'edge',edge,'L',o.levels_completed,o.state)
# Factor one common edge-consumption cell out and compare only interior supports.
R={}
for act in [1,2,3,4,5]:
 r,f,o=run([act]); R[act]=(r,f)
for u,v in [(1,2),(3,4)]:
 _,fu=R[u];_,fv=R[v]
 mask=fu!=fv;mask[:,63]=False
 ys,xs=np.where(mask)
 print('interior opposite',u,v,'diff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
