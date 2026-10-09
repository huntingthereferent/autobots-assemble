"""SK48 Level7 fresh native replay of reference-assisted alternatives.
Four nontrivial adjacent swaps, two fresh different-upstream games each,
public-only control switches and immediate native first-completion gating.
"""
from _sk48_native_public_stage_harness import enter,run_level,F
from _sk48_public_goal_sensor import frame
from hashlib import sha256
import json,logging
logging.disable(logging.CRITICAL)
W=json.loads((F/"sk48_l7_native_reference_mutations_ab.json").read_text())["survivors"]
out=[]
for i,w in enumerate(W):
 checks=[]
 for n in range(2):
  e,o,stages=enter(7,selector=i+n)
  root=sha256(frame(o).tobytes()).hexdigest()
  o,used,clicks=run_level(e,o,w["path"],7)
  checks.append({"trial":n,"L7_root_sha":root,
    "upstream_stage_consumed":[q[1] for q in stages],
    "L7_actions_until_completion":used,"switches":clicks,
    "native_levels":int(o.levels_completed),
    "passed":int(o.levels_completed)>=7 and used<=len(w["path"])})
 item={"swap_index":w["index"],"route":w["path"],
       "fresh_trials":checks,"all_pass":all(x["passed"] for x in checks)}
 out.append(item)
 print("SK48_L7_FRESH_SWAP",w["index"],"PASS",item["all_pass"],
   "FIRST_ACTION",[q["L7_actions_until_completion"] for q in checks],
   "ROOT",[q["L7_root_sha"][:16] for q in checks],flush=True)
dest=F/"sk48_l7_native_fresh_swaps.json"
dest.write_text(json.dumps({"source":"reference-assisted Level7 native alternative routes",
 "public_native_only":True,"fresh_trial_count":len(out)*2,
 "passing_routes":sum(r["all_pass"] for r in out),"routes":out},indent=2),encoding="utf-8")
print("L7_FRESH_TOTAL",sum(r["all_pass"] for r in out),"OF",len(out),"SAVED",dest,flush=True)
