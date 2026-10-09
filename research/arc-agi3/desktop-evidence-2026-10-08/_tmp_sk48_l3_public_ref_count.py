from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,distinct_colors,features
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
routes=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in routes if x["passed"] and x["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1+L2:o=e.step(GameAction.from_id(z),data={})
a=frame(o)
for y in (19,20,25,26,27,28,31,32,37,38,43,44,47,53,56,57,58,59,60,61):
 s="".join("0123456789ABCDEF"[v] for v in a[y,:])
 print("L3_PUBLIC_ROW",y,s,"DISTINCT_TILES",[v for _,v in distinct_colors(a[y])],flush=True)
print("L3_PALETTE",dict(zip(*np.unique(a,return_counts=True))),flush=True)
