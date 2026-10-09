"""Public native SK48 Level3: validate actual color engagement, not row alignment."""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
routes=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in routes if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1+L2+[1,1,1,1]:o=g.step(GameAction.from_id(z),data={})
for i in range(8):
 a=frame(o)
 y=features(a)["heads"][0][1]
 ys,xs=np.where(a[:53,:]==8)
 pos=list(zip(xs.tolist()[::4],ys.tolist()[::4]))[:12]
 ss="".join("0123456789ABCDEF"[v] for v in a[y+2,5:55])
 print("CONNECTED_TEST","R",i,"LEVEL",o.levels_completed,"HEAD_Y",y,
       "COLOR8_BOX",[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
       "ROW",ss,"SENSOR",features(a)["best_prefix"],flush=True)
 o=g.step(GameAction.ACTION4,data={})
