from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
import json,numpy as np,hashlib,logging
logging.disable(logging.CRITICAL)
L1=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1:r=e.step(GameAction.from_id(z),data={})
print("L1_COMPLETE",r.levels_completed,r.state.name,flush=True)
probe=e.step(GameAction.ACTION1,data={})
print("PROBE_AFTER_LEVEL",probe.levels_completed,probe.state.name,flush=True)
for i in range(1,45):
 after=e.step(GameAction.RESET,data={})
 print("RESET_ATTEMPT",i,"LEVELS",after.levels_completed,"STATE",after.state.name,flush=True)
 if after.levels_completed==0:
  print("RESET_ACCEPTED_AT",i,flush=True)
  for z in L1:r=e.step(GameAction.from_id(z),data={})
  print("AFTER_CONFIRMED_REPLAY",r.levels_completed,
        hashlib.sha256(np.asarray(r.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:24],flush=True)
  break
else: print("RESET_WALL after 44 attempts",flush=True)
