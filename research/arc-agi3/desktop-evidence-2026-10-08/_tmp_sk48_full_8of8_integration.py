"""SK48 full-chain public native integration regression, no private game reads.

Differential route selection across Levels 2-8. All prior positive
observations were used to build candidate families except Level 1.
This is a reference-assisted 8/8 replay, NOT a blind ARC3 submission.
"""
from _sk48_native_public_stage_harness import F,routes,run_level
from _sk48_public_goal_sensor import frame
from arc_agi import Arcade,OperationMode
from hashlib import sha256
import json,logging,time
logging.disable(logging.CRITICAL)
prior=routes()
l7=[x["route"] for x in json.loads((F/"sk48_l7_native_fresh_swaps.json").read_text())["routes"] if x["all_pass"]]
l8=[x["L8_route"] for x in json.loads((F/"sk48_l8_native_fresh_alternative_WINs.json").read_text())["results"] if x["both_fresh_WINS"]]
all_options=prior+[l7,l8]
runs=[];t0=time.monotonic()
for trial in range(3):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 o=e.observation_space
 stages=[];action_count=0
 for goal,choices in enumerate(all_options,1):
  route=choices[(trial+goal-1)%len(choices)]
  entry=sha256(frame(o).tobytes()).hexdigest()
  o,consumed,clicks=run_level(e,o,route,goal)
  action_count+=consumed
  row={"level":goal,"selected_route_index":(trial+goal-1)%len(choices),
   "route_length":len(route),"native_actions_consumed":consumed,
   "unused_after_first_completion":len(route)-consumed,
   "entry_public_SHA256":entry,
   "exit_public_SHA256":sha256(frame(o).tobytes()).hexdigest(),
   "clicks_from_public_pixels":clicks,
   "native_levels_completed":int(o.levels_completed),
   "native_state_name":o.state.name}
  stages.append(row)
  print("SK48_NATIVE_WITNESS",trial,goal,
        "CONSUMED",consumed,"UNUSED",len(route)-consumed,
        "CUMULATIVE",action_count,"LEVEL",o.levels_completed,flush=True)
 assert o.levels_completed==8 and o.state.name=="WIN",(trial,o.levels_completed,o.state.name)
 run={"trial":trial,"total_actions_consumed":action_count,
      "native_WIN":True,"stages":stages}
 runs.append(run)
 print("SK48_ALL_LEVELS_NATIVE_WIN",trial,"ACTIONS",action_count,
    "FULL_GAME_STATE",o.state.name,flush=True)
obj={"date":"2026-10-08","game_id":"sk48",
 "method":"public-native ARC SDK staged first-completion integration",
 "provenance":"Level1 blind independent; Levels2-8 reference-assisted alternatives",
 "official_ARC_competition_submission":False,
 "private_engine_access":False,
 "trials":len(runs),"native_WINs":sum(r["native_WIN"] for r in runs),
 "elapsed_seconds":round(time.monotonic()-t0,2),"runs":runs}
dest=F/"SK48_FULL_NATIVE_ALTERNATIVE_8OF8_PROVENANCE_2026-10-08.json"
dest.write_text(json.dumps(obj,indent=2),encoding="utf-8")
head=["# SK48 — Full native 8/8 A/B alternative route integration",
 "Date: 2026-10-08",
 "",
 "## Native results",
 "",
 "All three fresh runs reached **GameState WIN** with all 8 levels completed.",
 "The runs used only public native frames, SDK actions, public-pixel click",
 "selection, and the returned native completion signal. Every stage ended at",
 "its first completion; unused candidate-list actions were **not** executed",
 "in the next level.",
 "",
 "| Trial | Consumed actions | Native result |",
 "|---:|---:|---|"]
for r in runs:
 head.append(f"| {r['trial']} | {r['total_actions_consumed']} | 8/8 WIN |")
head+=["","## Provenance and limitations","",
 "Level 1 was discovered independently earlier. Levels 2-8 are **reference-assisted**",
 "alternative sequences generated from prior positive histories by native A/B",
 "macro movement variation and action-order mutation. A successful complete",
 "native replay is real evidence of this SK48 completion but does not prove a",
 "general blind ARC-AGI-3 solver, an official submission, or unseen-task success.",
 "",
 "The exact native stage witnesses (entry/exit SHA256, consumed action count,",
 "native state, pixel-selected ACTION6 clicks, and unused tail) are in",
 "SK48_FULL_NATIVE_ALTERNATIVE_8OF8_PROVENANCE_2026-10-08.json.",
 "",
 "No GitHub edits or official competition submission occurred.",
 "Research workspace: C:\\Users\\teepa\\arc3\\AB_ARC_EVIDENCE"]
report=F/"SK48_FULL_NATIVE_ALTERNATIVE_8OF8_REPORT_2026-10-08.md"
report.write_text("\n".join(head)+"\n",encoding="utf-8")
print("INTEGRATION_PASS",len(runs), "OF",len(runs),
 "JSON",dest,"REPORT",report,flush=True)
