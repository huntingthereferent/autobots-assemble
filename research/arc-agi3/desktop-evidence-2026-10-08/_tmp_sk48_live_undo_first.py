"""SK48 live interface experiment: inspect only SDK public frames/actions."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
arc=Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sk48")
def signature(o):
 return hashlib.blake2s(np.asarray(o.frame[-1],dtype=np.uint8).tobytes(),digest_size=10).hexdigest()
start=env.observation_space
print("START",signature(start),"LEVEL",start.levels_completed,"AVAILABLE",start.available_actions,flush=True)
for z in (1,7,4,7,1,1,7,7,7,4,7):
 before=env.observation_space
 after=env.step(GameAction.from_id(z),data={})
 print("ACT",z,"BEFORE",signature(before),"AFTER",signature(after),
       "DIFFERENT",signature(before)!=signature(after),
       "RESTORED_INITIAL",signature(after)==signature(start),
       "LEVEL",after.levels_completed,"STATE",after.state.name,
       "AVAILABLE",after.available_actions,flush=True)
