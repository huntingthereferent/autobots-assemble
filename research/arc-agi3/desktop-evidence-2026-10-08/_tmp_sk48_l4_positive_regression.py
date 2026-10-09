"""SK48 Level4 positive movement calibration ONLY, not independent solve.

Old saved Level4 route used here solely as a positive regression to
derive next native A/B operator family. L1-L3 entry routes are native
fresh-verified alternatives. Frame and color order from public pixels.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((v for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
 if v["passed"] and v["different_from_saved_reference"]),key=lambda v:len(v["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
POS=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for a in L1+L2+L3:o=e.step(GameAction.from_id(a),data={})
assert o.levels_completed==3
def getpos(a,color):
 y,x=np.where(a[:53,:]==color)
 return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None
rows=[]
for k,z in enumerate(POS,1):
 o=e.step(GameAction.from_id(z),data={})
 a=frame(o);f=connected_features(a)
 rec={"step":k,"action":z,"level":int(o.levels_completed),
     "head":f["controls"],"attached":[c["connected_colors"] for c in f["candidates"]],
     "connected_prefix":f["connected_prefix"],
     "colors":{str(v):getpos(a,v) for v in (8,12,9,14)}}
 rows.append(rec)
 print("L4_REFERENCE_ONLY",rec,flush=True)
 if o.levels_completed>=4:break
out=F/"sk48_l4_positive_regression_calibration.json"
out.write_text(json.dumps({"old_saved_Level4_route_calibration_only":True,
 "new_solver":False,"entered_via_alternative_L3":True,
 "positive_L4_actions":list(POS),"records":rows,
 "native_completed":bool(o.levels_completed>=4)},indent=2),encoding="utf-8")
print("L4_REFERENCE_AUDIT","COMPLETE",o.levels_completed>=4,"STEPS",k,"SAVED",out,flush=True)
