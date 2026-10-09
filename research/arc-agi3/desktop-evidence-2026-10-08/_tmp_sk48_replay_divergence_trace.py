"""Find first public-frame divergence during repeated route after native RESET."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
seq=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def frame(o):return np.asarray(o.frame[-1],dtype=np.uint8).copy().reshape(64,64)
def h(a):return sha256(a.tobytes()).hexdigest()[:12]
previous=[]
for trial in range(3):
 start=e.step(GameAction.RESET,data={})
 print("RESET",trial,h(frame(start)),start.levels_completed,flush=True)
 observations=[]
 for i,z in enumerate(seq,1):
  obs=e.step(GameAction.from_id(z),data={})
  arr=frame(obs)
  observations.append(arr)
  prior=previous[i-1] if trial and len(previous)>=i else arr
  dd=np.where(arr!=prior)
  print("ACTION",trial,i,z,"LEVEL",obs.levels_completed,
        "HASH",h(arr),"DIFF_PRIOR",len(dd[0]),flush=True)
 if not trial:previous=observations
