"""SK48 L5: public-only 2-color geometry, shape components, transition probes.
Fresh native SDK; stop each prior level at first witnessed completion.
No saved Level5 route.
"""
from pathlib import Path
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import numpy as np,json,hashlib,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((r for r in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
        if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(x["path"] for x in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if x["method"]=="swap_adjacent")
def enter():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for goal,path in enumerate((L1,L2,L3,L4),1):
  for i,z in enumerate(path,1):
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=goal:break
  assert o.levels_completed==goal,(goal,o.levels_completed)
 return e,o
e,o=enter()
a=frame(o)
print("L5_ENTRY",o.levels_completed,hashlib.sha256(a.tobytes()).hexdigest(),flush=True)
for y in range(1,63):
 s="".join("0123456789ABCDEF"[v] for v in a[y,2:62])
 if any(ch in s for ch in '89') or y in (2,3,7,19,25,26,27,28,31,37,43,56,57,58,59,60):
  print(f"L5_ROW {y:02d} {s}",flush=True)
print("TEST_MOVE_RESULT",flush=True)
for name,prog in [("right_x1",[4]),("left_x1",[3]),("up_x1",[1]),("down_x1",[2]),
 ("right_x3",[4]*3),("up_x3",[1]*3),("down_x3",[2]*3),
 ("right_up_right",[4,1,4]),("up_right_up",[1,4,1]),
 ("left_up_right",[3,1,4]),("up_down_right",[1,2,4])]:
 e,o=enter()
 b=frame(o).copy()
 record=[]
 for z in prog:
  o=e.step(GameAction.from_id(z),data={})
  q=frame(o)
  colors={}
  for color in (8,9):
   yy,xx=np.where(q[:53,:]==color)
   colors[str(color)]={"pixels":int(len(xx)),"minmax":
        [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else None,
        "rows":sorted(set(int(y) for y in yy))}
  record.append({"action":z,"levels_completed":int(o.levels_completed),
    "diff":int(np.count_nonzero(q!=b)),"colors":colors})
  b=q.copy()
 print("L5_NATIVE_MOVES",name,json.dumps(record,separators=(",",":")),flush=True)
