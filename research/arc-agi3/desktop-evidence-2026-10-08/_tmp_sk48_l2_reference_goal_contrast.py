"""SK48 saved Level2 solution is a reference witness ONLY, not a new solve.
Compare positive public frames with recently failed visual-clearance patterns.
"""
import logging,numpy as np,json
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
REF=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
def board(title,o):
 a=np.asarray(o.frame[-1],dtype=np.uint8).reshape(64,64)
 top=[int(a[25,30+i*6]) for i in range(4)]
 bottom=[int(a[57,23+i*6]) for i in range(4)]
 print("PUBLIC",title,"LEVEL",o.levels_completed,"TOP",top,"BOTTOM",bottom,flush=True)
 for y in (19,20,21,22,24,25,26,27,28,29,31,32,35,36,37,38,39,40,41,42,43,44,45,46,47):
  s="".join("0123456789ABCDEF"[v] for v in a[y,5:55])
  if len(set(s))>2:print(f"{y:02d} {s}",flush=True)
e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1:o=e.step(GameAction.from_id(z),data={})
board("L2_REFERENCE_ENTRY",o)
for k,z in enumerate(REF,1):
 o=e.step(GameAction.from_id(z),data={})
 if k in (3,7,11,17,23,27,28,29,30):board("L2_REFERENCE_STEP_"+str(k),o)
