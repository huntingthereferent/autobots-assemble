from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
arc=Arcade(operation_mode=OperationMode.NORMAL)
def frame(e):
 r=e._last_response
 return np.asarray(r.frame[-1],dtype=np.int16).reshape(64,64)
for game in ('ls20','sk48'):
 e=arc.make(game)
 before=frame(e)
 print('GAME',game,'STATE',e._last_response.state.name,'UNIQUE_COLORS',sorted(set(before.flatten())),'BG',int(np.bincount(before.flatten().astype(int)).argmax()),'FRAME_SHA',hashlib.sha1(before.tobytes()).hexdigest()[:10],flush=True)
 for action in range(1,8):
  try:
   q=copy.deepcopy(e); d={'x':31,'y':31} if action==6 else {}
   r=q.step(GameAction.from_id(action),data=d)
   after=frame(q)
   print(' ACTION',action,'DELTA',(before!=after).sum(),'STATE',r.state.name,'LEVELS',r.levels_completed,'COUNTER',getattr(r,'actions_remaining','n/a'),'SHA',hashlib.sha1(after.tobytes()).hexdigest()[:10],flush=True)
  except Exception as ex:print(' ACTION',action,'EXCEPTION',str(ex)[:180],flush=True)
