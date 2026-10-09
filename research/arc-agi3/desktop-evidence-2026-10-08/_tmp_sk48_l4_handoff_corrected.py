"""SK48 A/B corrected inter-level handoff: stop on native transition.

Previous cross-stage replay fed a Level3 route's trailing moves to Level4
even after levels_completed became 3. This test consumes at most the
first witnessed completion prefix for every stage before the next starts.
Then tests reference-assisted Level4 adjacent-swap variants from fresh
game instances and varied upstream Level2 / Level3 alternatives.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
R2=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2s=[x["L2_actions"] for x in R2 if x["passed"] and x["different_from_saved_reference"]]
R3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"]
L3s=[x["L3_path"] for x in R3 if x["passed"] and x["different_from_saved_reference"]]
M=json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())
S=[r for r in M["successful_interventions"] if r["method"]=="swap_adjacent"]
records=[]
def consume(env,seq,goal):
 consumed=0;obs=None
 for z in seq:
  obs=env.step(GameAction.from_id(z),data={})
  consumed+=1
  if obs.levels_completed>=goal:break
 if obs is None or obs.levels_completed<goal:
  raise RuntimeError(("stage_not_completed",goal,consumed))
 return consumed,obs
for j,s in enumerate(S):
 attempts=[]
 for trial in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  l2=L2s[(j+trial)%len(L2s)]
  l3=L3s[(j+trial)%len(L3s)]
  steps1,o=consume(e,L1,1)
  steps2,o=consume(e,l2,2)
  steps3,o=consume(e,l3,3)
  after3=sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
  steps4,o=consume(e,s["path"],4)
  entry={"trial":trial,"L2_index":(j+trial)%len(L2s),
     "L3_index":(j+trial)%len(L3s),
     "consumed":[steps1,steps2,steps3,steps4],
     "input_route_lengths":[len(L1),len(l2),len(l3),len(s["path"])],
     "trimmed_L3_tail":len(l3)-steps3,
     "L4_entry_sha256":after3,
     "levels_completed":int(o.levels_completed),"passed":int(o.levels_completed)>=4}
  attempts.append(entry)
 rec={"swap_index":s["edit"],"complete":all(x["passed"] for x in attempts),
      "native_trials":attempts}
 records.append(rec)
 print("HANDOFF_CORRECTED",s["edit"],"PASS",rec["complete"],
       "L3_TAIL_TRIMMED",[a["trimmed_L3_tail"] for a in attempts],
       "L4_ROOT_HASHES",[a["L4_entry_sha256"][:16] for a in attempts],
       "LEVEL4_FINISH",[a["consumed"][3] for a in attempts],flush=True)
obj={"game":"sk48","test":"native first-completion handoff across Levels1-4",
 "uses_private_engine":False,"reference_assisted_L4_mutations":True,
 "swaps_tested":len(records),"fresh_trials":len(records)*2,
 "all_pass":all(x["complete"] for x in records),
 "results":records}
out=F/"sk48_l4_native_handoff_corrected.json"
out.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("HANDOFF_RESULT","PASS",obj["all_pass"],"REPLAY_TRIALS",obj["fresh_trials"],"SAVED",out,flush=True)
