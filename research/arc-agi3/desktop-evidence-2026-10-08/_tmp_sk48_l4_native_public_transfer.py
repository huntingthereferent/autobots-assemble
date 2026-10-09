"""SK48 public native Level4 transfer through verified alternative Level3 route.

No saved Level4 route or private state. Public frame/palette/controls
and one-step native action probes; resets by fresh game instances.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
from hashlib import sha256
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((r for r in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
 if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 o=e.observation_space
 for a in L1+L2+L3:o=e.step(GameAction.from_id(a),data={})
 assert o.levels_completed==3,o.levels_completed
 return e,o
def spots(a,c):
 yy,xx=np.where(a[:53,:]==c)
 return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx)] if len(xx) else None
records=[];old=None
for z in (None,1,2,3,4):
 e,o=enter()
 orig=frame(o).copy()
 start=connected_features(orig)
 if old is None:old=sha256(orig.tobytes()).hexdigest()
 if z is not None:o=e.step(GameAction.from_id(z),data={})
 a=frame(o);v=connected_features(a)
 y,x=np.where(a!=orig)
 entry={"action":z,"level":int(o.levels_completed),
        "entry_native_sha":sha256(orig.tobytes()).hexdigest(),
        "after_native_sha":sha256(a.tobytes()).hexdigest(),
        "reference":list(v["reference"]),"control_heads":v["controls"],
        "visible_connected_order":[x["connected_colors"] for x in v["candidates"]],
        "changed_pixels":len(x),
        "color_locations":{str(c):spots(a,c) for c in (8,9,12,14,11,6,15)},
        "palette":{str(int(c)):int(n) for c,n in zip(*np.unique(a,return_counts=True))}}
 records.append(entry)
 print("NATIVE_LEVEL4_TRANSFER",entry,flush=True)
out=F/"sk48_l4_public_native_entry_probes.json"
out.write_text(json.dumps({"level4_entered_via_alternative_L3":True,
 "L1_actions":len(L1),"L2_alternative_actions":len(L2),
 "L3_alternative_actions":len(L3),"no_saved_L4_route_loaded":True,
 "native_public_probes":records},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
