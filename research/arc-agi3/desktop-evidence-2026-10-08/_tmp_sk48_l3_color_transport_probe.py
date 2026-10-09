"""SK48 Level3 native A/B color transport under connected head movement."""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
from _sk48_public_connected_goal import connected_features
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
routes=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=min((x for x in routes if x["passed"] and x["different_from_saved_reference"]),key=lambda x:len(x["L2_actions"]))["L2_actions"]
root=[1]*4+[4]*3
tests={
 "connected":[],
 "down":[2],
 "down_right":[2,4],
 "right_down":[4,2],
 "right_right_down":[4,4,2],
 "left_down":[3,2],
 "left_down_right":[3,2,4],
 "left_left_down_right":[3,3,2,4],
 "right_down_left":[4,2,3],
 "down_down_up":[2,2,1],
 "up_down":[1,2],
 "up_right_down":[1,4,2],
 "down_right_down":[2,4,2],
 "right_down_right":[4,2,4],
}
def coords(a,c):
 yy,xx=np.where(a[:53,:]==c)
 if not len(xx):return None
 return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx)]
for label,extra in tests.items():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1+L2+root+extra:o=e.step(GameAction.from_id(z),data={})
 a=frame(o);ff=connected_features(a)
 print("COLOR_TRANSPORT",label,"PFX",ff["connected_prefix"],"HEAD",ff["controls"],
  "COORDS",{c:coords(a,c) for c in (8,12,9,14)},
  "COLORS",[c["connected_colors"] for c in ff["candidates"]],
  "LEVEL",o.levels_completed,flush=True)
