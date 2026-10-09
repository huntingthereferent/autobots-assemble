from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
import json,numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
seq=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def frame(o):return np.asarray(o.frame[-1],dtype=np.uint8).reshape(64,64)
def sign(o):return hashlib.sha256(frame(o).tobytes()).hexdigest()[:16]
first=None
for trial in range(4):
 root=e.step(GameAction.RESET,data={})
 for z in seq:
  r=e.step(GameAction.from_id(z),data={})
 a=frame(r)
 if first is None:first=a.copy()
 difference=int(np.count_nonzero(a!=first))
 yy,xx=np.where(a!=first)
 print("TRIAL",trial,"ROOT",sign(root),"FINAL",sign(r),"LEVEL",r.levels_completed,
       "DIFF_FIRST",difference,
       "DIFF_BOX",None if not len(yy) else [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],flush=True)
