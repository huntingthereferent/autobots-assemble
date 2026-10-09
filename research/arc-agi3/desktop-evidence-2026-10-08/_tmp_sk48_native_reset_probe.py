from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import hashlib,numpy as np,logging
logging.disable(logging.CRITICAL)
arc=Arcade(operation_mode=OperationMode.NORMAL)
e=arc.make("sk48")
def sig(x):return hashlib.blake2s(np.asarray(x.frame[-1],dtype=np.uint8).tobytes(),digest_size=8).hexdigest()
start=sig(e.observation_space)
print("START",start,flush=True)
for a in (1,4,4):
 o=e.step(GameAction.from_id(a),data={})
 print("MOVE",a,sig(o),o.levels_completed,flush=True)
try:
 o=e.step(GameAction.RESET,data={})
 print("RESET",sig(o),"SAME_START",start==sig(o),"LEVELS",o.levels_completed,"STATUS",o.state.name,flush=True)
except Exception as ex:
 print("RESET_FAILURE",type(ex).__name__,str(ex)[:180],flush=True)
