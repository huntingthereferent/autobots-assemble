"""Native SK48 Level2 goal-reference screening, independent pattern probes."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,json,logging
from pathlib import Path
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
programs={
 "alternating_right_up":[4,1]*30,
 "alternating_up_right":[1,4]*30,
 "right_right_up":[4,4,1]*20,
 "up_right_right":[1,4,4]*20,
 "up_up_right":[1,1,4]*20,
 "right_up_up":[4,1,1]*20,
 "zigzag":[4,1,3,2]*15,
 "right_up_left":[4,1,3]*20,
 "up_right_down":[1,4,2]*20,
}
for name,program in programs.items():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1:r=e.step(GameAction.from_id(z),data={})
 origin=np.asarray(r.frame[-1],dtype=np.uint8).reshape(64,64)
 current_level=r.levels_completed;changes=[];win=None
 for i,z in enumerate(program,1):
  before=np.asarray(r.frame[-1],dtype=np.uint8).reshape(64,64).copy()
  r=e.step(GameAction.from_id(z),data={})
  after=np.asarray(r.frame[-1],dtype=np.uint8).reshape(64,64)
  top=tuple(int(after[25,30+6*n]) for n in range(4))
  if top != tuple(int(before[25,30+6*n]) for n in range(4)):changes.append((i,top))
  if r.levels_completed>current_level:
   win=i;break
 print("PATTERN",name,"L2_COMPLETED",win,"L2_STEPS",i,"TOP_CHANGED",changes[:18],"FINAL_TOP",top,"END",r.state.name,flush=True)
