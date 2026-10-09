"""SK48 Level 2 public-only action response shapes."""
import json,collections,logging,numpy as np
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
L1=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
env=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def reset_l2():
 o=env.step(GameAction.RESET,data={})
 for z in L1:o=env.step(GameAction.from_id(z),data={})
 assert o.levels_completed==1
 return o
for action in (1,2,3,4):
 before=reset_l2()
 before_pixels=np.asarray(before.frame[-1],dtype=np.uint8).reshape(64,64)
 after=env.step(GameAction.from_id(action),data={})
 after_pixels=np.asarray(after.frame[-1],dtype=np.uint8).reshape(64,64)
 ys,xs=np.where(before_pixels != after_pixels)
 coords=collections.Counter((int(y)//6,int(x)//6) for y,x in zip(ys,xs))
 print("ACTION",action,"MOVED_PIXELS",len(ys),"CELL_REGIONS",coords.most_common(12),
    "CHANGED_PALETTE",dict(collections.Counter((int(before_pixels[y,x]),int(after_pixels[y,x])) for y,x in zip(ys,xs)).most_common(8)),
    "LEVEL",after.levels_completed,flush=True)
