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
P6=(4,4,2,4,6,2,2,4,4,2,1,4,2,3,1,3,2,6,4,4,4,3,3,3,3,2,2,4,1,3,1,4,6,2,2,2)
for trial in range(2):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
 transitions=[];prev=0
 for idx,z in enumerate(prefix+P6):
  if z==6:
   g=e._game
   other=next(k for k in g.xpmcmtbcv if k!=g.vzvypfsnt)
   r=e.step(GameAction.ACTION6,data={'x':int(other.x+2),'y':int(other.y+2)})
  else:
   r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>prev:
   prev=r.levels_completed;transitions.append((idx+1,prev))
 print('TRIAL',trial,'TRANS',transitions,'RESULT',r.levels_completed,r.state.name,flush=True)
