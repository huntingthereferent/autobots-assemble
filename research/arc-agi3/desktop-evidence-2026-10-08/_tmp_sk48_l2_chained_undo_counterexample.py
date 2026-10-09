"""Public SK48 Level 2: A/B chained rollback counterexample.
Each native observation is read from actual fresh game. No private state.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def key(o):
 return "%d|%s|%s"%(int(o.levels_completed),o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:16])
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1:o=g.step(GameAction.from_id(z),data={})
parent=key(o)
print("PARENT",parent,flush=True)
events=[]
def event(action,o,note=""):
 row={"action":action,"key":key(o),"matches_parent":key(o)==parent,"note":note}
 events.append(row);print("EVENT",row,flush=True)
for z in (1,2,3,4):
 before=g.observation_space
 event("PRE"+str(z),before)
 after=g.step(GameAction.from_id(z),data={})
 event(str(z),after)
 undo=g.step(GameAction.ACTION7,data={})
 event("7",undo,"after "+str(z))
 if key(undo)!=parent:
  print("NATIVE_UNDO_WALL","after",z,flush=True)
  for tries in range(1,9):
   reset=g.step(GameAction.RESET,data={})
   event("RESET",reset,"attempt %d"%tries)
   if reset.levels_completed==0:break
  for first in L1:r=g.step(GameAction.from_id(first),data={})
  event("L1_REPLAY",r)
# Fresh direct reference of action4 from Level 2
h=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1:r=h.step(GameAction.from_id(z),data={})
direct=h.step(GameAction.ACTION4,data={})
event("FRESH_ACTION4",direct)
out=F/"sk48_l2_chained_undo_counterexample.json"
out.write_text(json.dumps({"method":"native public observations only","parent":parent,"events":events},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
