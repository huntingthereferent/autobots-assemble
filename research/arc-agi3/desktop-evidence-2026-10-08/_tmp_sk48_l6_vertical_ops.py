from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for a in prefix:root.step(GameAction.from_id(a),data={})
g=root._game
pairs=list(g.xpmcmtbcv.items())
for p in [(),(2,),(2,2),(2,2,2),(2,2,2,2),(4,),(3,),(2,4),(2,3),(4,2)]:
 q=copy.deepcopy(root)
 q.step(GameAction.ACTION6,data={'x':31,'y':4})
 for z in p:q.step(GameAction.from_id(z),data={})
 gg=q._game
 print('PATH',p,'ACTIVE',(gg.vzvypfsnt.x,gg.vzvypfsnt.y,gg.vzvypfsnt.rotation),'L',len(gg.mwfajkguqx[gg.vzvypfsnt]),'PADS',[(int(t.x),int(t.y),int(t.pixels[1,1])) for t in gg.vbelzuaian if t.y<53],'FLAGS',(len(gg.ljprkjlji),len(gg.pzzwlsmdt)),'Q',gg.qiercdohl,flush=True)
