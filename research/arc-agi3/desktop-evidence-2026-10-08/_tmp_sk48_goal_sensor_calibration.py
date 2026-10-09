"""Positive/negative calibration for SK48 public sensor.

Reference route used ONLY here for test labeling, not in policy module.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import logging,json
from pathlib import Path
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
REFERENCE=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
for group,prog in (("reference",REFERENCE),("failed_right_right_up",(4,4,1)*10),
                   ("failed_right_up",(4,1)*15)):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1:o=e.step(GameAction.from_id(z),data={})
 print("SENSOR",group,"ROOT",features(frame(o)),flush=True)
 for i,z in enumerate(prog,1):
  o=e.step(GameAction.from_id(z),data={})
  f=features(frame(o))
  if i in (3,7,9,10,11,14,17,19,22,25,27,28,29,30) or o.levels_completed>=2:
   print("SENSOR",group,"ACTION",i,"LEVEL",o.levels_completed,
         "TARGET",f["target"],"HEADS",f["heads"],
         "ORDER",[(q["attached_row"],q["matched_prefix"]) for q in f["candidates"]],
         "REMAIN",f["visible_target_remaining"],flush=True)
  if o.levels_completed>=2:break
