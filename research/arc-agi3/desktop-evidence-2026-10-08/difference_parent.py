from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
o=e.step(GameAction.ACTION5,data={}); p=o.frame[0].copy()
o=e.step(GameAction.ACTION5,data={}); q=o.frame[0].copy()
# exact 8-cell difference D and all gray embeddings; report local neighborhoods to identify its carried parent.
D={(int(x),int(y)) for y,x in zip(*np.where((p==0)&(q==9)))}
def norm(S):
 mx=min(x for x,y in S); my=min(y for x,y in S); return {(x-mx,y-my) for x,y in S}
T=norm(D); G={(int(x),int(y)) for y,x in zip(*np.where(q==5))}
emb=[]
for ax,ay in G:
 P={(x+ax,y+ay) for x,y in T}
 if P<=G: emb.append((ax,ay,P))
print('embeddings',[(a,b) for a,b,_ in emb])
for a,b,P in emb:
 print('anchor',a,b,'bbox',min(x for x,y in P),max(x for x,y in P),min(y for x,y in P),max(y for x,y in P))
