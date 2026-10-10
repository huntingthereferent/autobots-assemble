from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,random,gc,time
random.seed(4804)
p1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4)
p2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
p3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
p4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
p5=(3,1,3,3,4,4,4,2,1,4,4,1,4,2,3,3,3,2,2,3,2,4,4,4,4,3,1,4,4,3,2,4,1,3,3,3,3,1,3,3,3,4,1,4,4,4,4,4,1,4,2,3,3,3,3,3,3,2,4,4,2,4,4,4,4)
prefix=p1+p2+p3+p4+p5
P6=(4,4,2,4,6,2,2,4,4,2,1,4,2,3,1,3,2,6,4,4,4,3,3,3,3,2,2,4,1,3,1,4,6,2,2,2)
P7=(4,1,4,4,2,4,6,4,2,2,2,2,2,2,1,1,6,1,6,1,3,6,4,4,3,3,3,2,4,4,6,2,6,2,6,2,2,6,3,3,3,3,2,4,4,1,1,1,4,4,4)
P8=(4,4,6,2,2,4,2,3,2,2,2,1,1,1,6,4,4,4,4,3,2,3,3,1)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 prev=0;trans=[];sw=[]
 for i,z in enumerate(prefix+P6+P7+P8):
  if z==6:
   gg=e._game;other=next(k for k in gg.xpmcmtbcv if k!=gg.vzvypfsnt)
   sw.append((i+1,int(other.x+2),int(other.y+2)))
   r=e.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
  else:r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>prev:
   prev=r.levels_completed;trans.append((i+1,prev,r.state.name))
 print('TRIAL',trial,'TRANSITIONS',trans,'FINAL',r.levels_completed,r.state.name,'MOVES',i+1,'P8',len(P8),'SWITCHES',sw[-5:],flush=True)
