"""SK48 native switch witnesses -> real Continuity AgentLineage.

Public-only control and actual SK48 engine steps. No private game object read.
Transitions are witnessed without retrofitting future outcomes into predictions.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys,logging,json
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState
sys.path.insert(0, r"C:\Users\teepa\continuity-live")
from runtime.service import EcosystemService
from runtime.arc_native_observer import ARCFrameObservationProvider

source=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\_tmp_sk48_public_causal_controller.py").read_text()
definitions=source.split("\nlogging.disable(logging.CRITICAL)\noutput=[]")[0]
ns={}
exec(definitions,ns)
actions=ns["actions"]; top_keys=ns["top_keys"]; frame=ns["frame"]
active_from_movement=ns["active_from_movement"]

logging.disable(logging.CRITICAL)
with TemporaryDirectory(prefix="sk48_ab_") as tmp:
 provider=ARCFrameObservationProvider("sk48")
 service=EcosystemService(data_dir=tmp,native_observer=provider)
 arc=Arcade(operation_mode=OperationMode.NORMAL)
 env=arc.make("sk48")
 active=None;last_level=0;switches=[];miles=[]
 for step,z in enumerate(actions,1):
  before=env.observation_space
  if z==6:
   keys=top_keys(before)
   assert len(keys)==2, (step,keys)
   hypothesis=active is None
   if hypothesis:active=0
   chosen=1-active
   x,y,color=keys[chosen]
   click=(x+2,y+2)
   after=env.step(GameAction.ACTION6,data={"x":click[0],"y":click[1]})
   active=chosen

   delta=np.argwhere(frame(before)!=frame(after))
   if len(delta):
    yy,xx=(int(q) for q in delta[0])
   else:
    xx,yy=click

   referent=f"sk48 native switch action {step} level {before.levels_completed+1}"
   instance=f"sk48-native-{step}"
   root=service.activate_agent({
    "surface":"begin comparison","actor_id":"james",
    "instance_id":instance,"referent":referent,
   })["root"]
   assert service.runtime.state(root).status=="READY"
   evidence=provider.record_native_step(
    handoff_id=root,referent=referent,
    before=before,after=after,
    action=f"ACTION6 public click{click}",
    x=xx,y=yy,
   )
   moved=service.agent_lineage.step(root)
   status=service.runtime.state(root)
   switches.append({
    "step":step,"level":before.levels_completed+1,
    "native_changed_pixels":len(delta),
    "click":list(click),"hypothesized_initial_key":hypothesis,
    "ab_state":status.output.get("ab_state"),
    "lineage_status":status.status,
    "witnesses":len(status.evidence),
    "native_before_ref":evidence.before_ref,
    "native_after_ref":evidence.after_ref,
    "witness_ref":status.evidence[0].ref if status.evidence else None,
    "witness_source":status.evidence[0].source if status.evidence else None,
    "observed_before":dict(evidence.before),
    "observed_after":dict(evidence.after),
    "executed":moved.executed==(root,),
   })
  else:
   after=env.step(GameAction.from_id(z),data={})
   if after.levels_completed==before.levels_completed:
    active,_=active_from_movement(before,after,active)
  if after.levels_completed>last_level:
   last_level=after.levels_completed
   miles.append((step,last_level))
   active=None
  if after.state is GameState.WIN:break
 summary={
  "status":after.state.name,"levels":after.levels_completed,"actions":step,
  "local_sdk_score":arc.get_scorecard().score,
  "switches":switches,"milestones":miles,
  "native_move_count":sum(s["ab_state"]=="MOVE" for s in switches),
  "native_unknown_count":sum(s["ab_state"]=="UNKNOWN" for s in switches),
  "native_partial_count":sum(s["ab_state"]=="PARTIAL" for s in switches),
  "all_switches_executed_once":all(s["executed"] for s in switches),
  "causal_controller_not_full_solver":True,
  "direction_actions_from_saved_route":True,
 }
 output=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_native_to_lineage.json")
 output.write_text(json.dumps(summary,indent=2),encoding="utf-8")
 print("SK48_AB_LINEAGE", {k:v for k,v in summary.items() if k!="switches"},flush=True)
 for s in switches:print("SWITCH",s,flush=True)
 print("SAVED",output,flush=True)
