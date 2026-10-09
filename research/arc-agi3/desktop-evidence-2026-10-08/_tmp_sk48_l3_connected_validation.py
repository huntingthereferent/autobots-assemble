"""Native SK48 Level3: verify connected target vs mere row alignment.

Transfer uses different fresh-verified L2 route; no saved Level3 route.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
import json,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
rr=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((r for r in rr if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
def fresh(path):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for a in L1+L2+path:o=e.step(GameAction.from_id(a),data={})
 return e,o
paths=[[],[1]*4,[1]*4+[4],[1]*4+[4]*2,
       [1]*4+[4]*3,[1]*4+[4]*4,[1]*4+[4]*5,
       [1]*4+[4]*3+[2],
       [1]*4+[4]*3+[3],
       [1]*4+[4]*3+[4],
       [1]*4+[4]*3+[1],
       [1]*4+[4]*3+[3,2],
       [1]*4+[4]*3+[3,3,2],
       [1]*4+[4]*3+[2,4],
       [1]*4+[4]*3+[3,2,4]]
rows=[]
for path in paths:
 e,o=fresh(path);f=connected_features(frame(o))
 row={"path":path,"level":int(o.levels_completed),
      "aligned":f["unverified_row_alignment_prefix"],
      "connected":f["connected_prefix"],
      "head":f["controls"],
      "colors":[x["connected_colors"] for x in f["candidates"]]}
 rows.append(row)
 print("CONNECTED_AB",row,flush=True)
out=F/"sk48_l3_public_connection_validation.json"
out.write_text(json.dumps({"native_public_only":True,"old_L3_route_loaded":False,
                            "samples":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
