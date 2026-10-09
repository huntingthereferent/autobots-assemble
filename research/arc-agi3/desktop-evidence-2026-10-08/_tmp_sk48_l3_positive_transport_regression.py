"""SK48 Level3 positive regression, AUDIT ONLY.

Previously saved native Level3 direction route loaded only in this
calibration file, to locate true color/transport transitions and devise
new A/B macro hypotheses. Not an independent Level3 solver.
Level1 and Level2 entrance are fresh verified alternative routes.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
r=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in r if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
REFERENCE=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for a in L1+L2:o=e.step(GameAction.from_id(a),data={})
assert o.levels_completed==2
results=[]
def positions(a,v):
 ys,xs=np.where(a[:53,:]==v)
 if not len(xs):return None
 return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
for i,z in enumerate(REFERENCE,1):
 o=e.step(GameAction.from_id(z),data={})
 a=frame(o);f=connected_features(a)
 row={"i":i,"action":z,"level":int(o.levels_completed),
      "head":f["controls"],"connected":f["connected_prefix"],
      "colors":[c["connected_colors"] for c in f["candidates"]],
      "positions":{str(v):positions(a,v) for v in (8,12,9,14)}}
 results.append(row)
 print("L3_REFERENCE_AUDIT",row,flush=True)
 if o.levels_completed>=3:break
out=F/"sk48_l3_reference_transport_calibration.json"
out.write_text(json.dumps({"purpose":"positive regression only",
 "preexisting_saved_L3_route_loaded":True,"new_solver":False,
 "entry_L2_used_novel_alternative":True,
 "reference_actions":list(REFERENCE),"records":results,
 "completed_Level3":bool(o.levels_completed>=3)},indent=2),encoding="utf-8")
print("L3_REFERENCE_CALIBRATION","WIN",o.levels_completed>=3,"ACTIONS",i,"SAVED",out,flush=True)
