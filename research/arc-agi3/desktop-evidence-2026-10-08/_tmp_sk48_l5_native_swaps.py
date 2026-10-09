"""SK48 Level5 native adjacent-action A/B (reference-assisted).

Only nonidentical adjacent swaps of validated 65-action positive witness,
reset with positive acknowledgement, L1-L4 first-completion handoff, and
Level5 native completion. No cloned game or private engine.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame
import json,logging,hashlib,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2=min((r for r in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if r["passed"] and r["different_from_saved_reference"]),key=lambda r:len(r["L2_actions"]))["L2_actions"]
L3=json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"][0]["L3_path"]
L4=next(w["path"] for w in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if w["method"]=="swap_adjacent")
old=json.loads((F/"sk48_l5_saved_positive_control_calibration.json").read_text())["saved_candidate_actions"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;retry=0;root=None
def st(z):
 global calls
 r=g.step(z,data={});calls+=1;return r
def test(path):
 global retry,root
 for i in range(8):
  o=st(GameAction.RESET)
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("native reset unacknowledged")
 for level,p in enumerate((L1,L2,L3,L4),1):
  for z in p:
   o=st(GameAction.from_id(z))
   if o.levels_completed>=level:break
  if o.levels_completed!=level:raise RuntimeError(("stage",level))
 h=hashlib.sha256(frame(o).tobytes()).hexdigest()
 if root is None:root=h
 if root!=h:raise RuntimeError("L5 entry changed")
 for k,z in enumerate(path,1):
  o=st(GameAction.from_id(z))
  if o.levels_completed>=5:return k
 return None
wins=[];results=[];time0=time.monotonic()
for i in range(len(old)-1):
 if old[i]==old[i+1]:continue
 seq=old.copy()
 seq[i],seq[i+1]=seq[i+1],seq[i]
 first=test(seq)
 item={"swap_index":i,"original_pair":[old[i],old[i+1]],"native_win_at":first,
       "passed":first is not None,"full_route":seq if first is not None else None}
 results.append(item)
 if first is not None:
  wins.append(item)
  print("L5_ORDER_SURVIVED",i,"PAIR",item["original_pair"],"FIRST_WIN",first,flush=True)
 if len(results)%10==0:print("L5_ORDER_CHECK",len(results),"WINS",len(wins),
                            "NATIVE",calls,"SEC",round(time.monotonic()-time0,1),flush=True)
out=F/"sk48_l5_native_adjacent_swap_ab.json"
out.write_text(json.dumps({"source":"native controlled mutations of old positive Level5 route",
 "reference_assisted":True,"native_public_only":True,"tested":len(results),
 "winners":wins,"results":results,"native_calls":calls,"reset_retry":retry},indent=2),encoding="utf-8")
print("L5_SWAP_DONE","TESTS",len(results),"WINS",len(wins),"SAVED",out,flush=True)
