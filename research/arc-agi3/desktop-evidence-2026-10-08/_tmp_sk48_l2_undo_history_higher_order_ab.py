"""SK48 A/B one layer up: test causal necessity of rollback order/count.

Same native public Level 2 entry, all candidate runs acknowledged RESET;
a tested batch of prior (action, ACTION7) cycles shares the exact current
frame. Apply ACTION4 to distinguish retained history relations.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
from itertools import permutations
import json,logging,numpy as np
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def h(o):return sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:16]
def begin():
 for k in range(8):
  o=g.step(GameAction.RESET,data={})
  if o.levels_completed==0:break
 else:raise RuntimeError("no acknowledged reset")
 for z in L1:o=g.step(GameAction.from_id(z),data={})
 assert o.levels_completed==1
 return o
initial=begin();parent=h(initial)
reference={}
for z in (1,2,3,4):
 begin();r=g.step(GameAction.from_id(z),data={})
 reference[z]=h(r)
print("REFERENCE",reference,flush=True)
histories=list(permutations((1,2,3)))+[(1,1,1),(2,2,2),(3,3,3),(4,4,4),(1,2,4),(4,2,3),(4,1,2),(2,4,1)]
rows=[]
for hist in histories:
 begin()
 restorations=[]
 for a in hist:
  after=g.step(GameAction.from_id(a),data={})
  restored=g.step(GameAction.ACTION7,data={})
  restorations.append(h(restored)==parent)
 if not all(restorations):
  print("CONTINUATION_WALL",hist,"STEPS",restorations,flush=True)
  rows.append({"history":hist,"restores":restorations,"admissible":False})
  continue
 results={}
 for z in (1,2,3,4):
  # Always replay the identical history so action tests don't contaminate each other.
  begin()
  for a in hist:
   g.step(GameAction.from_id(a),data={})
   g.step(GameAction.ACTION7,data={})
  final=g.step(GameAction.from_id(z),data={})
  results[str(z)]={"sha":h(final),"agrees_fresh":h(final)==reference[z]}
 item={"history":hist,"restores":restorations,"admissible":True,"next":results}
 rows.append(item)
 print("THREE_CYCLE_AB",hist,"DIFFERENCES",[int(z) for z,v in results.items() if not v["agrees_fresh"]],flush=True)
out=F/"sk48_l2_undo_history_higher_order_ab.json"
out.write_text(json.dumps({"native_source":"public SDK frames",
 "reference_action_frames":reference,"tested":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
