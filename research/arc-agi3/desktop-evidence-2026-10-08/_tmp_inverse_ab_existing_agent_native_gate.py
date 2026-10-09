"""Local integration test: real native SK48 steps through existing AgentLineage."""
import sys,json,logging
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
sys.path.insert(0,r"C:\Users\teepa\continuity-live")
from runtime.service import EcosystemService
from runtime.arc_native_observer import ARCFrameObservationProvider
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
arc=Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sk48")
before=env.observation_space
after=env.step(GameAction.from_id(L1[0]),data={})
b=np.asarray(before.frame[-1]);a=np.asarray(after.frame[-1])
delta=np.argwhere(b!=a)
assert len(delta)>0,"L1 native action did not provide a visible moved witness"
y,x=(int(v) for v in delta[0])
loc=(x,y)
predicted={"cell_color":int(a[y,x]),"levels_completed":int(after.levels_completed)}
with TemporaryDirectory(prefix="inverse_ab_agent_test_") as temp:
 provider=ARCFrameObservationProvider("sk48")
 service=EcosystemService(data_dir=temp,native_observer=provider)
 def activate(name):
  return service.activate_agent({"surface":"begin comparison",
   "actor_id":"james","instance_id":"inverse-ab-test-"+name,
   "referent":"native SK48 construction A/B comparison"})["root"]
 good=activate("good");wrong=activate("wrong");missing=activate("missing")
 for root,pred in [
  (good,predicted),
  (wrong,{**predicted,"cell_color":-100})
 ]:
  provider.record_native_step(handoff_id=root,
   referent="native SK48 construction A/B comparison",
   before=before,after=after,action="actual native L1 action",
   x=x,y=y,predicted_after=pred)
  service.agent_lineage.step(root)
 absent_step=service.agent_lineage.step(missing)
 gs=service.runtime.state(good);ws=service.runtime.state(wrong)
 ms=service.runtime.state(missing)
 assert gs.status=="COMPLETE",(gs.status,gs.output)
 assert gs.output.get("ab_state")=="MOVE"
 assert gs.output.get("prediction_matched") is True
 assert len(gs.evidence)==1
 assert ws.status=="PARTIAL",(ws.status,ws.output)
 assert ws.output.get("prediction_matched") is False
 assert not ws.evidence
 assert ms.status=="READY" and not ms.evidence
 # Known native SK48 phase transition: same public frame can have a
 # different later continuation. The current native observer sees only
 # before/after color and completion, not history phase.
 obs=after
 for n in L1[1:]:
  obs=env.step(GameAction.from_id(n),data={})
  if obs.levels_completed>=1:break
 assert obs.levels_completed==1
 phase_before=obs
 phase_after=env.step(GameAction.ACTION2,data={})
 phase_same=bool(np.array_equal(
  np.asarray(phase_before.frame[-1]),np.asarray(phase_after.frame[-1])))
 phase_root=activate("phase")
 if phase_same:
  provider.record_native_step(handoff_id=phase_root,
   referent="native SK48 construction A/B comparison",
   before=phase_before,after=phase_after,
   action="actual native phase-advancing action2",
   x=0,y=0)
  service.agent_lineage.step(phase_root)
  phase_status=service.runtime.state(phase_root).status
  assert phase_status=="UNKNOWN",phase_status
 else:
  phase_status="NOT_APPLICABLE_NATIVE_FRAME_CHANGED"
 result={"integration":"real native SDK frames into existing EcosystemService / AgentLineage",
  "good":{"status":gs.status,"ab":gs.output.get("ab_state"),"evidence":len(gs.evidence)},
  "mismatched_prediction":{"status":ws.status,"prediction_matched":ws.output.get("prediction_matched"),"evidence":len(ws.evidence)},
  "missing_witness":{"status":ms.status,"evidence":len(ms.evidence)},
  "native_phase_probe":{"same_public_frame":phase_same,"agent_status":phase_status},
  "no_repo_changes":True,"real_arc_witness":True,
  "meaning":"native comparator does not promote unobserved inverse constructions"}
 out=F/"AB_INVERSE_AGENT_NATIVE_GATE_TEST_2026-10-08.json"
 out.write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("INVERSE_AB_NATIVE_AGENT_GATE",result,"SAVED",out,flush=True)
