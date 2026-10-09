from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,copy
arc=Arcade(operation_mode=OperationMode.NORMAL)
for game in ('bp35','ft09','dc22','cd82','ar25','cn04'):
 e=arc.make(game)
 base=np.asarray(e._last_response.frame[-1],dtype='int16')
 outs={}
 for z in (1,2,3,4,5,7):
  q=copy.deepcopy(e)
  r=q.step(GameAction.from_id(z),data={})
  outs[z]=np.asarray(r.frame[-1],dtype='int16').copy()
 print('GAME',game,'PIXELS',(base.shape),'BASE_DIFFERENCES',{z:int(np.count_nonzero(v!=base)) for z,v in outs.items()},'PAIRWISE_1',{z:int(np.count_nonzero(v!=outs[1])) for z,v in outs.items()},'UNIQUE_ACTION_IMAGES',len({v.tobytes() for v in outs.values()}),flush=True)
