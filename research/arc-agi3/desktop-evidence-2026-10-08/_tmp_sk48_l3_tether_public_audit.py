"""Public pixel audit: distinguish aligned colored tile from connected tile."""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import json,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
r=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in r if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
samples={"l3_up4":[1,1,1,1],"l3_right4_up4":[4,4,4,4,1,1,1,1],
         "l3_right4_up3":[4,4,4,4,1,1,1],
         "l3_right3_up4":[4,4,4,1,1,1,1],
         "l3_right6_up4":[4]*6+[1]*4}
for name,path in samples.items():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1+L2+path:o=e.step(GameAction.from_id(z),data={})
 a=frame(o);ft=features(a);y=ft["heads"][0][1] if ft["heads"] else 42
 print("PIXEL_AUDIT",name,"NATIVE_LEVEL",o.levels_completed,
       "HEAD",ft["heads"],"SENSOR_PREFIX",ft["best_prefix"],flush=True)
 for row in (y+1,y+2,y+3):
  print(" ROW",row,
    "".join("0123456789ABCDEF"[x] for x in a[row,5:55]),flush=True)
