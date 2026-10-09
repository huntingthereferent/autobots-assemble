"""SK48 Level3 transfer via a newly witnessed nonreference Level2 path.
Reads only native public 64x64 frames and returned game-state signals.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import numpy as np,json,hashlib,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
routes=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
alternate=min((x for x in routes if x["passed"] and x["different_from_saved_reference"]),
              key=lambda r:len(r["L2_actions"]))
L2=alternate["L2_actions"]
print("TRANSFER_REFERENCE","ALT_L2_LENGTH",len(L2),"DIFFERENT_SAVED",True,flush=True)
def enter():
 g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1+L2:o=g.step(GameAction.from_id(z),data={})
 assert o.levels_completed==2
 return g,o
records=[]
for action in (None,1,2,3,4):
 g,o=enter()
 a=frame(o).copy();before=features(a)
 if action is not None:
  o=g.step(GameAction.from_id(action),data={})
  b=frame(o).copy()
 else:b=a
 now=features(b)
 ys,xs=np.where(b!=a)
 item={"action":action,
       "native_level":int(o.levels_completed),
       "entry_target":before["target"],
       "entry_heads":before["heads"],
       "after_target":now["target"],
       "after_heads":now["heads"],
       "after_best_prefix":now["best_prefix"],
       "changed_pixels":int(len(ys)),
       "changed_box":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(ys) else None,
       "entry_sha256":hashlib.sha256(a.tobytes()).hexdigest(),
       "after_sha256":hashlib.sha256(b.tobytes()).hexdigest()}
 records.append(item)
 print("L3_NATIVE_TRANSFER",item,flush=True)
out=F/"sk48_l3_public_goal_sensor_transfer.json"
out.write_text(json.dumps({"level3_from_fresh_replay":True,
 "L2_alternate_route":L2,"saved_reference_route_used":False,
 "native_public_only":True,"probes":records},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
