from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,3,2,2,2,2,2,2,2,2,1,1,1,3,3,1,4,4,4,4,4,4,4,1,1,1,3,1,2,1,4,2)
p4=(3,3,3,2,2,2,3,2,2,3,3,1,2,1,2,1,2,1,1,3,3,1,2,3,3,1,1,1,2,2,4,1,1,1,1,4,1,4,1,1,3,3,3)
p5=(1,3,1,1,3,3,3,4,3,4,3,4,1,1,3,3,3,3,1,3,3,3,4,4,2,2,2,2,2,4,4,3,2,2,4,2,4,4,4,4,4,4,4,1)
p6=(1,1,2,1,2,4,4,1,4,1,1,1,3,3,4,4,1,1,4,4,1,1,4,2,2,1,1,3,1,2,3,3,3,3,1,2,3,3,2,2,2,2,1,4,4,4,3,3,3,1,1,1,1,1,1,4,4,4,4,4,4,2,4,4,1,1,4,2,2,2,2,2)
p7=(1,1,2,2,3,3,2,2,2,2,2,1,2,4,4,1,2,1,2,3,2,1,4,1,2,3,3,1,1,1,4,4,4,4,1,4,4,1,4,4,1,1,4,2,2,3,3,3,1,2,2,2,2)
for trial in (0,1):
 e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
 prev=0;milestones=[]
 for i,z in enumerate(p1+p2+p3+p4+p5+p6+p7,1):
  r=e.step(GameAction.from_id(z),data={})
  if r.levels_completed>prev:
   prev=r.levels_completed;milestones.append((i,prev,r.state.name))
  if r.state.name=='WIN':break
 print('TRIAL',trial,'TRANSITIONS',milestones,'STATE',r.state.name,'LEVELS',r.levels_completed,'ACTIONS',i,'P7',len(p7),'SCORE',e._last_response.levels_completed,flush=True)
