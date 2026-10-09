"""Native L2 bounded undo feasibility, frame equality is the oracle."""
from pathlib import Path
import json,logging,hashlib,numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def key(o):return hashlib.sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:14]
for a in (1,2,3,4,7):
 g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1:r=g.step(GameAction.from_id(z),data={})
 parent=key(r)
 forward=g.step(GameAction.from_id(a),data={})
 first=key(forward)
 seen=[]
 for k in range(1,7):
  rr=g.step(GameAction.ACTION7,data={})
  seen.append((k,key(rr),rr.levels_completed))
  if key(rr)==parent:break
 print("ACTION",a,"PARENT",parent,"AFTER",first,"UNDO_OBSERVATIONS",seen,
       "RESTORED",key(rr)==parent,flush=True)
