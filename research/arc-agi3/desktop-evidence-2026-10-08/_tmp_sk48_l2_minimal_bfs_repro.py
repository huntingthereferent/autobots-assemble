import json,time,logging,hashlib,numpy as np
from pathlib import Path
from collections import Counter
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
L1=json.loads(Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def key(o):
 return (int(o.levels_completed),o.state.name,hashlib.sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest())
def goto_level2():
 o=game.step(GameAction.RESET,data={})
 for z in L1:o=game.step(GameAction.from_id(z),data={})
 return o
initial=goto_level2()
start_key=key(initial)
start_pixels=np.asarray(initial.frame[-1],dtype=np.uint8).copy().reshape(64,64)
front=[((),start_key)]
seen={start_key:()}
history=[]
n_actions=len(L1)+1;edges=0
sol=None;start=time.monotonic();mismatches=0
for depth in range(1,2):
 for path,parent in front:
  for z in (1,2,3,4):
   now=goto_level2()
   n_actions+=len(L1)+1
   current=key(now)
   print("REPLAY",z,"EXPECTED",start_key[2][:16],"OBSERVED",current[2][:16], "SAME",current==start_key,flush=True)
   after=game.step(GameAction.from_id(z),data={})
   print("MOVE",z,"BEFORE",current[2][:16],"AFTER",key(after)[2][:16],flush=True)
