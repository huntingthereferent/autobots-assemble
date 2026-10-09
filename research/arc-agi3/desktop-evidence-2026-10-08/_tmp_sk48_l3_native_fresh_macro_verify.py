"""SK48 Level3 fresh-game independent replay verification of A/B macro routes.

Macro generation used prior positive regression for operator families.
Here only native source routes are replayed; comparison with an old
saved positive Level3 route is solely a post-hoc novelty check.
Test different fresh-verified alternative L2 entrances across trials.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import json,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
L2all=json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"]
L2=[r["L2_actions"] for r in L2all if r["passed"] and r["different_from_saved_reference"]]
W=json.loads((F/"sk48_l3_native_macro_final_color_ab.json").read_text())["native_Level3_wins"]
old=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4)
unique={}
for w in W:
 p=tuple(w["route"])
 if p[-1]!=4:continue
 # Favor first native completion over trailing actions after it.
 unique.setdefault(p,w)
candidates=sorted(unique.values(),key=lambda w:(len(w["route"]),w["pivot"],w["macro"]))
chosen=[]
macro_seen=set()
for w in candidates:
 m=tuple(w["macro"])
 if m in macro_seen:continue
 chosen.append(w);macro_seen.add(m)
 if len(chosen)>=8:break
outcomes=[]
for index,w in enumerate(chosen):
 route=w["route"]
 trials=[]
 for rep in range(2):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  l2=L2[(index+rep)%len(L2)]
  for z in L1+l2:o=e.step(GameAction.from_id(z),data={})
  entered=int(o.levels_completed)
  initial_hash=sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
  first_completion=None;final=None
  for k,z in enumerate(route,1):
   final=e.step(GameAction.from_id(z),data={})
   if final.levels_completed>=3:
    first_completion=k;break
  after_hash=sha256(np.asarray(final.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
  entry={"trial":rep,"l2_entry_len":len(l2),
       "start_level":entered,"start_sha256":initial_hash,
       "level3_first_win_action":first_completion,
       "result_level":int(final.levels_completed),
       "after_sha256":after_hash,
       "passed":entered==2 and first_completion is not None}
  trials.append(entry)
 record={"candidate":index,"L3_path":route,
         "original_macro":w["macro"],"L3_len":len(route),
         "different_from_saved_reference":tuple(route)!=old,
         "passed":all(t["passed"] for t in trials),
         "trials":trials}
 outcomes.append(record)
 print("L3_FRESH_A_B",index,"LEN",len(route),
       "NOVEL",record["different_from_saved_reference"],
       "PASS",record["passed"],
       "FIRST_COMPLETIONS",[t["level3_first_win_action"] for t in trials],flush=True)
output=F/"sk48_l3_native_fresh_macro_wins.json"
output.write_text(json.dumps({"method":"native Arcade freshly instantiated twice per macro",
 "used_saved_L3_route_for_generation":False,
 "saved_L3_reference_only_posthoc_comparison":True,
 "candidate_count":len(chosen),"fresh_trials":2*len(chosen),
 "passing_candidates":sum(x["passed"] for x in outcomes),
 "different_routes":sum(x["different_from_saved_reference"] for x in outcomes),
 "results":outcomes},indent=2),encoding="utf-8")
print("L3_FRESH_SUMMARY",len(outcomes),
      "PASS",sum(x["passed"] for x in outcomes),
      "ALTERNATIVES",sum(x["different_from_saved_reference"] for x in outcomes),
      "SAVED",output,flush=True)
