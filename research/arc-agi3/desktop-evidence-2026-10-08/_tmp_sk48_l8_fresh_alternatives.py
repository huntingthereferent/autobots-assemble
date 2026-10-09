"""SK48 Level8 native WIN verification, reference-assisted swapped routes.

Alternate previously verified Level2..7 predecessors. Public-pixel
control switching, native first-completion handoff, true WIN terminal state.
"""
from _sk48_native_public_stage_harness import F,enter,run_level,controls
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import json,logging
logging.disable(logging.CRITICAL)
w=json.loads((F/"sk48_l8_native_reference_mutations_ab.json").read_text())["survivors"]
l7=[x["route"] for x in json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"] if x["all_pass"]]
results=[]
for k,item in enumerate(w):
 trials=[]
 for trial in range(2):
  e,o,early=enter(7,selector=k+trial)
  o,n7,c7=run_level(e,o,l7[(k+trial)%len(l7)],7)
  entry=sha256(frame(o).tobytes()).hexdigest()
  o,n8,c8=run_level(e,o,item["path"],8)
  checks={"trial":trial,"upstream_consumed":[z[1] for z in early],
      "L7_consumed":n7,"L8_native_WIN_at":n8,
      "native_levels_completed":int(o.levels_completed),"state":o.state.name,
      "L8_entry_sha":entry,"L8_control_clicks":c8,
      "passed":o.state.name=="WIN" and o.levels_completed==8 and n8<=len(item["path"])}
  trials.append(checks)
 itemout={"swap_index":item["index"],"L8_route":item["path"],
      "both_fresh_WINS":all(t["passed"] for t in trials),"trials":trials}
 results.append(itemout)
 print("LEVEL8_FRESH_A_B","SWAP",item["index"],"PASS",itemout["both_fresh_WINS"],
       "WIN_ACTIONS",[z["L8_native_WIN_at"] for z in trials],
       "ENTRY",[z["L8_entry_sha"][:16] for z in trials],flush=True)
obj={"provenance":"reference-assisted native all-level WIN with alternative Level8 routes",
 "native_public_only":True,"total_fresh_trials":len(results)*2,
 "passing_routes":sum(x["both_fresh_WINS"] for x in results),"results":results}
out=F/"sk48_l8_native_fresh_alternative_WINs.json"
out.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("LEVEL8_FRESH_SUMMARY","PASS",obj["passing_routes"],"OF",len(results),"SAVED",out,flush=True)
