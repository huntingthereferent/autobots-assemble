"""Public SK48 Level 2 observation after independently found Level 1 route."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
import json,collections,logging,numpy as np
logging.disable(logging.CRITICAL)
evidence=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())
path=evidence["solution"]["path"]
env=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in path:o=env.step(GameAction.from_id(z),data={})
print("LEVEL2_START",o.levels_completed,"PREVIOUS_NATIVE_ACTIONS",len(path),"STATE",o.state.name,flush=True)
a=np.asarray(o.frame[-1],dtype=np.uint8).reshape((64,64))
print("PALETTE",dict(collections.Counter(a.ravel().tolist())),flush=True)
chars="0123456789ABCDEF"
for y,row in enumerate(a):
 print(f"{y:02d} "+''.join(chars[v] for v in row),flush=True)
