"""SK48 Level 2: A/B hidden action-count probe using public no-op ACTION2.

Compare public frame and future ACTION4 after repeated ACTION2 at Level2
entry. All native operations through the SDK; no _game/private source.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def H(o):
 return f"{o.levels_completed}:{o.state.name}:"+sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:18]
def enter():
 for j in range(8):
  o=g.step(GameAction.RESET,data={})
  if o.levels_completed==0:break
 else:raise RuntimeError("reset not acknowledged")
 for z in L1:o=g.step(GameAction.from_id(z),data={})
 assert o.levels_completed==1
 return o
rows=[]
for direction in (2,7):
 for n in range(8):
  root=enter();start=H(root);history=[]
  for i in range(n):
   r=g.step(GameAction.from_id(direction),data={})
   history.append(H(r))
  observed=H(r) if history else start
  after=g.step(GameAction.ACTION4,data={})
  row={"repeated_action":direction,"count":n,
       "same_current_frame_as_entry":observed==start,
       "intermediate_frames":history,
       "next_action4":H(after)}
  rows.append(row)
  print("ACTION_COUNT_AB",direction,n,"SAME_VISIBLE",row["same_current_frame_as_entry"],
        "NEXT4",row["next_action4"],"LEVEL",after.levels_completed,flush=True)
out=F/"sk48_l2_native_noop_action_count_ab.json"
out.write_text(json.dumps({"method":"public native frame and action API",
 "no_private_engine_reads":True,"tests":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
