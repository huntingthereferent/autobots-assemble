from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
paths=[(),(1,),(2,),(3,),(4,),(7,),(1,1),(1,2),(2,1),(3,4),(7,2),(1,1,1),(2,3,4)]
def sig(e):
 r=e._last_response;g=e._game
 return (hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:10],g.qiercdohl,r.state.name,len(g.ljprkjlji),len(g.pzzwlsmdt),g.lgdrixfno,g.xsoixcero)
for p in paths:
 e=copy.deepcopy(root)
 for z in p:e.step(GameAction.from_id(z),data={})
 a,b=list(e._game.xpmcmtbcv.items())[0]
 out=[]
 for tag,x,y in [('miss',0,0),('key',int(a.x+2),int(a.y+2)),('mate',int(b.x+2),int(b.y+2))]:
  q=copy.deepcopy(e);q.step(GameAction.ACTION6,data={'x':x,'y':y});out.append((tag,sig(q)))
 print(p,'BEFORE',sig(e),'AFTER',out,flush=True)
