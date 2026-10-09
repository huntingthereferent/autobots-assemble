from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,copy,hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
def sign(e):
 return hashlib.blake2s(np.asarray(e._last_response.frame[-1],dtype='int16').tobytes(),digest_size=8).hexdigest()
for game in ('bp35','dc22','ft09','cd82'):
 try:root=a.make(game)
 except Exception as x:print('FAIL',game,type(x).__name__,str(x)[:100],flush=True);continue
 print('GAME',game,'START',sign(root),'STATE',root._last_response.state.name,flush=True)
 for z in (1,2,3,4,5,7):
  e=copy.deepcopy(root)
  hashes={sign(e)};rr=None
  for i in range(12):
   try:rr=e.step(GameAction.from_id(z),data={})
   except Exception as x:
    print('ACT',z,'ERR',type(x).__name__,str(x)[:90],flush=True);break
   hashes.add(sign(e))
   if rr.state.name!='NOT_FINISHED':break
  if rr:print('ACT',z,'STEPS',i+1,'VIS',len(hashes),'LEVEL',rr.levels_completed,'STATUS',rr.state.name,flush=True)
