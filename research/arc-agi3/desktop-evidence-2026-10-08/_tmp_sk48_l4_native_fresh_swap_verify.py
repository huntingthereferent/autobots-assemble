"""SK48 Level4 fresh native verification: three order-swapped A/B alternatives.

Positive saved Level4 reference used only to generate single-swap
candidate set in previous separate experiment; not independent blind
solve. Native public level completion is the actual criterion.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2all=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2s=[x["L2_actions"] for x in L2all if x["passed"] and x["different_from_saved_reference"]]
L3all=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"]
L3s=[x["L3_path"] for x in L3all if x["passed"] and x["different_from_saved_reference"]]
source=json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())
swaps=[x for x in source["successful_interventions"] if x["method"]=="swap_adjacent"]
rows=[]
for j,w in enumerate(swaps):
 results=[]
 for trial in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  L2=L2s[(j+trial)%len(L2s)]
  L3=L3s[(j+trial)%len(L3s)]
  for z in L1+L2+L3:o=e.step(GameAction.from_id(z),data={})
  entry_level=int(o.levels_completed)
  initial=sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
  first=None
  for n,z in enumerate(w["path"],1):
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>=4:
    first=n;break
  result={"trial":trial,"level4_entry":entry_level,
    "entered_level5_at_action":first,"native_level":int(o.levels_completed),
    "start_frame_sha":initial,
    "passed":entry_level==3 and first is not None}
  results.append(result)
 row={"swap_index":w["edit"],"actions":w["path"],
      "first_completion":w["first_win_action"],
      "fresh_trials":results,"passed":all(x["passed"] for x in results)}
 rows.append(row)
 print("L4_FRESH_SWAPPED",w["edit"],"PASS",row["passed"],
       "NATIVE_FIRST",[x["entered_level5_at_action"] for x in results],flush=True)
out=F/"sk48_l4_native_fresh_swap_witnesses.json"
out.write_text(json.dumps({"source":"A/B permutations of prior positive Level4 action order",
 "native_SDK_only":True,"tested_alternatives":len(rows),
 "fresh_trials":len(rows)*2,"passed":sum(x["passed"] for x in rows),
 "witnesses":rows},indent=2),encoding="utf-8")
print("L4_FRESH_RESULT",len(rows),"PASS",sum(x["passed"] for x in rows),"SAVED",out,flush=True)
