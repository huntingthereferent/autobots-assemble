from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,copy,collections,time
a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ft09')
def fr(e):return np.asarray(e._last_response.frame[-1],dtype='int16')
b=copy.deepcopy(root);b.step(GameAction.ACTION5,data={});base=fr(b).copy()
print('BASE',len(set(int(x) for x in base.flatten())),'COLOR_HIST',collections.Counter(base.flatten()).most_common(12),flush=True)
found=[];distribution=collections.Counter()
for y in range(4,64,8):
 for x in range(4,64,8):
  e=copy.deepcopy(root)
  try:r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
  except Exception as ex:print('ERROR',x,y,type(ex).__name__,str(ex)[:100]);continue
  score=int(np.count_nonzero(fr(e)!=base));distribution[score]+=1
  if score>0:found.append((score,x,y,r.levels_completed,r.state.name))
print('DIST',distribution,'CHANGED',len(found),'TOP',sorted(found,reverse=True)[:35],flush=True)
